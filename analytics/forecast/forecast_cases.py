
from pathlib import Path

from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = PROJECT_ROOT / "data" / "gold" / "daily_cases"
OUTPUT_PATH = PROJECT_ROOT / "data" / "gold" / "case_forecasts"

HISTORY_DAYS = 7
FORECAST_DAYS = 28


def main():
    spark = (
        SparkSession.builder
        .appName("EpiScope-Case-Forecasting")
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
                F.col("case_count").cast("double").alias("case_count"),
            )
            .groupBy("encounter_date", "district", "disease")
            .agg(F.sum("case_count").alias("case_count"))
        )

        if daily.limit(1).count() == 0:
            raise ValueError(f"No records found in {INPUT_PATH}")

        combinations = daily.select("district", "disease").distinct()

        bounds = daily.agg(
            F.min("encounter_date").alias("min_date"),
            F.max("encounter_date").alias("max_date"),
        )

        # Build a complete daily calendar for each district and disease.
        calendar = (
            combinations.crossJoin(bounds)
            .withColumn(
                "encounter_date",
                F.explode(
                    F.sequence(
                        F.col("min_date"),
                        F.col("max_date"),
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
            .fillna({"case_count": 0.0})
            .withColumn(
                "_day_epoch",
                F.unix_timestamp("encounter_date"),
            )
        )

        history_window = (
            Window
            .partitionBy("district", "disease")
            .orderBy(F.col("_day_epoch"))
            .rangeBetween(
                -HISTORY_DAYS * 24 * 60 * 60,
                -24 * 60 * 60,
            )
        )

        historical = (
            complete_daily
            .withColumn(
                "history_days",
                F.count(F.lit(1)).over(history_window),
            )
            .withColumn(
                "moving_average",
                F.avg("case_count").over(history_window),
            )
            .withColumn(
                "history_stddev",
                F.coalesce(F.stddev_pop("case_count").over(history_window), F.lit(0.0)),
            )
        )

        latest = (
            historical
            .withColumn(
                "_latest_date",
                F.max("encounter_date").over(
                    Window.partitionBy("district", "disease")
                ),
            )
            .filter(F.col("encounter_date") == F.col("_latest_date"))
            .select(
                "district",
                "disease",
                F.col("encounter_date").alias("forecast_origin"),
                "case_count",
                "history_days",
                F.coalesce(
                    F.col("moving_average"), F.lit(0.0)
                ).alias("daily_forecast"),
                F.col("history_stddev"),
            )
        )

        # Generate 28 forecast dates after the last observed date.
        forecasts = (
            latest
            .withColumn(
                "forecast_day",
                F.explode(F.sequence(F.lit(1), F.lit(FORECAST_DAYS))),
            )
            .withColumn(
                "forecast_date",
                F.date_add("forecast_origin", F.col("forecast_day")),
            )
            .withColumn(
                "forecast_cases",
                F.greatest(
                    F.lit(0.0),
                    F.round(F.col("daily_forecast"), 2),
                ),
            )
            .withColumn(
                "lower_80",
                F.greatest(
                    F.lit(0.0),
                    F.round(F.col("daily_forecast") - 1.2816 * F.col("history_stddev"), 2),
                ),
            )
            .withColumn(
                "upper_80",
                F.round(F.col("daily_forecast") + 1.2816 * F.col("history_stddev"), 2),
            )
            .withColumn(
                "model",
                F.lit("7-day-moving-average"),
            )
            .select(
                "district",
                "disease",
                "forecast_origin",
                "forecast_date",
                "forecast_day",
                "forecast_cases",
                "lower_80",
                "upper_80",
                "model",
            )
        )

        forecasts.write.mode("overwrite").partitionBy("district").parquet(
            str(OUTPUT_PATH)
        )

        print(f"Forecast rows generated: {forecasts.count():,}")
        print(f"Forecast horizon: {FORECAST_DAYS} days")
        print(f"Saved forecasts to: {OUTPUT_PATH}")

        forecasts.orderBy(
            "district", "disease", "forecast_date"
        ).show(30, truncate=False)

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
