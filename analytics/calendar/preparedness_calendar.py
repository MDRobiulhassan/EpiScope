
from pathlib import Path

from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = PROJECT_ROOT / "data" / "gold" / "daily_cases"
OUTPUT_PATH = PROJECT_ROOT / "data" / "gold" / "preparedness_calendar"

# Planning assumption: prepare one month before the historical peak month.
PREPARATION_LEAD_MONTHS = 1


def main():
    spark = (
        SparkSession.builder
        .appName("EpiScope-Preparedness-Calendar")
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
        )

        if daily.limit(1).count() == 0:
            raise ValueError(f"No data found in {INPUT_PATH}")

        # Average cases for each calendar month across the observed years.
        monthly = (
            daily
            .withColumn("calendar_month", F.month("encounter_date"))
            .withColumn("year", F.year("encounter_date"))
            .groupBy("district", "disease", "year", "calendar_month")
            .agg(F.sum("case_count").alias("monthly_cases"))
        )

        seasonal = (
            monthly
            .groupBy("district", "disease", "calendar_month")
            .agg(
                F.avg("monthly_cases").alias("avg_monthly_cases"),
                F.max("monthly_cases").alias("historical_max_monthly_cases"),
                F.countDistinct("year").alias("years_observed"),
            )
        )

        peak_window = Window.partitionBy("district", "disease").orderBy(
            F.desc("avg_monthly_cases"),
            F.asc("calendar_month"),
        )

        calendar = (
            seasonal
            .withColumn("peak_rank", F.row_number().over(peak_window))
            .withColumn(
                "is_peak_month",
                F.col("peak_rank") == 1,
            )
            .withColumn(
                "preparation_month",
                F.pmod(
                    F.col("calendar_month") - 1 - PREPARATION_LEAD_MONTHS,
                    F.lit(12),
                ) + 1,
            )
            .withColumn(
                "preparedness_action",
                F.when(
                    F.col("is_peak_month"),
                    F.lit("Increase readiness and monitor reported cases"),
                ).otherwise(
                    F.lit("Maintain routine surveillance and readiness")
                ),
            )
            .withColumn(
                "planning_basis",
                F.lit("Historical monthly case counts; review with public-health experts"),
            )
            .select(
                "district",
                "disease",
                "calendar_month",
                "avg_monthly_cases",
                "historical_max_monthly_cases",
                "years_observed",
                "is_peak_month",
                "preparation_month",
                "preparedness_action",
                "planning_basis",
            )
        )

        calendar.write.mode("overwrite").parquet(str(OUTPUT_PATH))

        print(f"Calendar rows: {calendar.count():,}")
        print(f"Saved to: {OUTPUT_PATH}")

        print("\n--- Peak months by district and disease ---")
        (
            calendar
            .filter(F.col("is_peak_month"))
            .orderBy("district", "disease")
            .show(64, truncate=False)
        )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
