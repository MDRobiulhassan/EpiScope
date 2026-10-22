
from pathlib import Path

from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = PROJECT_ROOT / "data" / "gold" / "daily_cases"
SCORES_PATH = PROJECT_ROOT / "data" / "gold" / "outbreak_scores"
ALERTS_PATH = PROJECT_ROOT / "data" / "gold" / "outbreak_alerts"

BASELINE_DAYS = 28
MIN_BASELINE_DAYS = 14
STANDARD_DEVIATIONS = 2.0
MIN_CASES_FOR_ALERT = 5


def main():
    spark = (
        SparkSession.builder
        .appName("EpiScope-Outbreak-Detection")
        .master("local[*]")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    try:
        daily = (
            spark.read.parquet(str(INPUT_PATH))
            .select(
                F.to_date("encounter_date").alias("encounter_date"),
                "district",
                "disease",
                F.col("case_count").cast("long").alias("case_count"),
            )
            .groupBy("encounter_date", "district", "disease")
            .agg(F.sum("case_count").alias("case_count"))
        )

        if daily.limit(1).count() == 0:
            raise ValueError(f"No records found in {INPUT_PATH}")

        # One row for every date in the observed period for each
        # district-disease combination.
        combinations = daily.select("district", "disease").distinct()

        date_bounds = daily.agg(
            F.min("encounter_date").alias("start_date"),
            F.max("encounter_date").alias("end_date"),
        )

        calendar = (
            combinations.crossJoin(date_bounds)
            .withColumn(
                "encounter_date",
                F.explode(
                    F.sequence(
                        F.col("start_date"),
                        F.col("end_date"),
                        F.expr("INTERVAL 1 DAY"),
                    )
                ),
            )
            .select("district", "disease", "encounter_date")
        )

        complete_daily = (
            calendar.join(
                daily,
                on=["encounter_date", "district", "disease"],
                how="left",
            )
            .withColumn(
                "case_count",
                F.coalesce(F.col("case_count"), F.lit(0)).cast("long"),
            )
            .withColumn(
                "_day_epoch",
                F.unix_timestamp("encounter_date"),
            )
        )

        # The range frame covers the previous 28 calendar days,
        # excluding the current day.
        baseline_window = (
            Window
            .partitionBy("district", "disease")
            .orderBy(F.col("_day_epoch"))
            .rangeBetween(
                -BASELINE_DAYS * 24 * 60 * 60,
                -24 * 60 * 60,
            )
        )

        scored = (
            complete_daily
            .withColumn(
                "baseline_days",
                F.count(F.lit(1)).over(baseline_window),
            )
            .withColumn(
                "baseline_mean",
                F.avg("case_count").over(baseline_window),
            )
            .withColumn(
                "baseline_stddev",
                F.stddev_pop("case_count").over(baseline_window),
            )
            .withColumn(
                "alert_threshold",
                F.greatest(
                    F.lit(float(MIN_CASES_FOR_ALERT)),
                    F.coalesce(F.col("baseline_mean"), F.lit(0.0))
                    + STANDARD_DEVIATIONS
                    * F.coalesce(F.col("baseline_stddev"), F.lit(0.0)),
                ),
            )
            .withColumn(
                "is_outbreak_alert",
                (F.col("baseline_days") >= MIN_BASELINE_DAYS)
                & (F.col("case_count") >= F.col("alert_threshold")),
            )
            .withColumn(
                "excess_cases",
                F.greatest(
                    F.col("case_count")
                    - F.coalesce(F.col("baseline_mean"), F.lit(0.0)),
                    F.lit(0.0),
                ),
            )
            .drop("_day_epoch")
        )

        alerts = scored.filter(F.col("is_outbreak_alert"))

        scored.write.mode("overwrite").partitionBy("district").parquet(
            str(SCORES_PATH)
        )
        alerts.write.mode("overwrite").partitionBy("district").parquet(
            str(ALERTS_PATH)
        )

        print(f"Daily district-disease rows scored: {scored.count():,}")
        print(f"Outbreak alerts generated: {alerts.count():,}")
        print(f"Scores saved to: {SCORES_PATH}")
        print(f"Alerts saved to: {ALERTS_PATH}")

        print("\n--- Highest case counts ---")
        (
            scored
            .filter(F.col("baseline_days") >= MIN_BASELINE_DAYS)
            .orderBy(F.desc("case_count"))
            .select(
                "encounter_date",
                "district",
                "disease",
                "case_count",
                "baseline_mean",
                "baseline_stddev",
                "alert_threshold",
                "is_outbreak_alert",
            )
            .show(20, truncate=False)
        )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
