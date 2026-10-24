
from pathlib import Path
import shutil

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "data" / "gold"
OUTPUT = ROOT / "dashboard" / "data"
TEMP = ROOT / "data" / "dashboard_export_temp"


def export_json(df, name):
    """Stream Spark JSONL output into a valid JSON array."""
    temp_dir = TEMP / name
    output_file = OUTPUT / f"{name}.json"

    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    df.coalesce(1).write.mode("overwrite").json(str(temp_dir))

    part_files = list(temp_dir.glob("part-*.json"))
    if not part_files:
        part_files = list(temp_dir.glob("part-*"))

    if not part_files:
        raise RuntimeError(f"No output generated for {name}")

    with part_files[0].open("r", encoding="utf-8") as src:
        with output_file.open("w", encoding="utf-8") as dst:
            dst.write("[")
            first = True

            for line in src:
                line = line.strip()
                if not line:
                    continue

                if not first:
                    dst.write(",")

                dst.write(line)
                first = False

            dst.write("]")

    shutil.rmtree(temp_dir)
    print(f"Exported {output_file}")


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    TEMP.mkdir(parents=True, exist_ok=True)

    spark = (
        SparkSession.builder
        .appName("EpiScopeDashboardExport")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "16")
        .getOrCreate()
    )

    # 1. Weekly public cases. Aggregate before suppression so multiple
    # small daily counts can be safely published as a weekly total.
    cases = spark.read.parquet(str(GOLD / "daily_cases"))
    missing_case_columns = {"encounter_date", "district", "disease", "case_count"} - set(cases.columns)
    if missing_case_columns:
        raise ValueError(
            "Gold daily_cases is missing required columns: "
            f"{sorted(missing_case_columns)}"
        )
    source_case_rows = cases.count()
    if source_case_rows == 0:
        raise ValueError(f"Gold daily_cases is empty: {GOLD / 'daily_cases'}")

    weekly_cases = (
        cases
        .withColumn(
            "week_start",
            F.to_date(F.date_trunc("week", F.to_timestamp("encounter_date"))),
        )
        .groupBy("week_start", "district", "disease")
        .agg(F.sum("case_count").cast("long").alias("case_count"))
        .withColumn(
            "suppressed",
            (F.col("case_count") > 0) & (F.col("case_count") < 5),
        )
        .withColumn(
            "published_case_count",
            F.when(F.col("suppressed"), F.lit(None).cast("long"))
            .otherwise(F.col("case_count")),
        )
        .select(
            F.col("week_start").cast("string").alias("date"),
            "district",
            "disease",
            "published_case_count",
            "suppressed",
        )
    )

    weekly_case_rows = weekly_cases.count()
    publishable_case_rows = weekly_cases.filter(
        F.col("published_case_count").isNotNull()
    ).count()
    print(
        "Dashboard cases: "
        f"{source_case_rows:,} daily rows -> {weekly_case_rows:,} weekly rows; "
        f"{publishable_case_rows:,} publishable"
    )
    if weekly_case_rows == 0:
        raise ValueError("Weekly case aggregation produced no rows.")

    export_json(weekly_cases, "cases")

    # 2. Outbreak alerts
    alerts_path = GOLD / "outbreak_alerts"
    scores_path = GOLD / "outbreak_scores"

    alert_files = list(alerts_path.rglob("*.parquet"))

    if alert_files:
        alerts = spark.read.parquet(str(alerts_path))
    else:
        print("No alert Parquet files found; deriving alerts from outbreak scores.")
        alerts = (
            spark.read.parquet(str(scores_path))
            .filter(F.col("is_outbreak_alert") == True)
        )

    if (
        "alert_score" not in alerts.columns
        and {"case_count", "baseline_mean", "baseline_stddev"}.issubset(alerts.columns)
    ):
        alerts = alerts.withColumn(
            "alert_score",
            F.when(
                F.col("baseline_stddev") > 0,
                (F.col("case_count") - F.col("baseline_mean"))
                / F.col("baseline_stddev"),
            ).otherwise(F.lit(0.0)),
        )

    alert_columns = alerts.columns

    # Select only fields that exist in this pipeline's output.
    wanted = [
        "encounter_date", "district", "disease", "case_count",
        "baseline_mean", "baseline_stddev", "alert_score",
        "is_outbreak_alert",
    ]
    selected = [c for c in wanted if c in alert_columns]

    alerts = alerts.select(*selected)

    if "encounter_date" in selected:
        alerts = alerts.withColumn(
            "encounter_date",
            F.col("encounter_date").cast("string"),
        )

    export_json(alerts, "alerts")

    # 3. Forecasts
    forecasts = spark.read.parquet(str(GOLD / "case_forecasts"))
    forecast_columns = forecasts.columns

    date_col = next(
        (c for c in ["forecast_date", "encounter_date", "date"]
         if c in forecast_columns),
        None,
    )

    value_col = next(
        (c for c in ["forecast_cases", "predicted_cases", "prediction"]
         if c in forecast_columns),
        None,
    )

    if not date_col or not value_col:
        raise ValueError(
            "Could not identify forecast date/value columns. "
            f"Found: {forecast_columns}"
        )

    forecasts = forecasts.select(
        F.col(date_col).cast("string").alias("date"),
        "district",
        "disease",
        F.col(value_col).cast("double").alias("forecast_cases"),
        F.col("lower_80").cast("double").alias("lower_80")
        if "lower_80" in forecast_columns
        else F.lit(None).cast("double").alias("lower_80"),
        F.col("upper_80").cast("double").alias("upper_80")
        if "upper_80" in forecast_columns
        else F.lit(None).cast("double").alias("upper_80"),
    )

    export_json(forecasts, "forecasts")

    # 4. Resource allocation
    resources = spark.read.parquet(str(GOLD / "resource_allocations"))
    export_json(resources, "resources")

    # 5. Preparedness calendar
    calendar = spark.read.parquet(str(GOLD / "preparedness_calendar"))
    export_json(calendar, "calendar")

    spark.stop()


if __name__ == "__main__":
    main()
