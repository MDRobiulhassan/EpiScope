
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "silver" / "encounters"
DAILY_PATH = ROOT / "data" / "gold" / "daily_cases"
SUMMARY_PATH = ROOT / "data" / "gold" / "district_summary"


def main():
    spark = (
        SparkSession.builder
        .appName("EpiScope-Gold-Aggregation")
        .master("local[*]")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.shuffle.partitions", "32")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    try:
        encounters = spark.read.parquet(str(INPUT_PATH))

        daily = (
            encounters
            .withColumn("year", F.year("encounter_date"))
            .withColumn("month", F.month("encounter_date"))
            .withColumn("week", F.weekofyear("encounter_date"))
            .groupBy(
                "encounter_date", "district", "disease",
                "year", "month", "week",
            )
            .agg(
                F.count("*").alias("case_count"),
                F.sum(
                    F.when(F.col("severity") == "severe", 1).otherwise(0)
                ).alias("severe_case_count"),
                F.avg("age").alias("mean_patient_age"),
                F.max(
                    F.col("synthetic_outbreak").cast("int")
                ).cast("boolean").alias("ground_truth_outbreak"),
            )
        )

        daily.write.mode("overwrite").partitionBy("year").parquet(
            str(DAILY_PATH)
        )

        summary = (
            daily
            .groupBy("district", "disease")
            .agg(
                F.sum("case_count").alias("total_cases"),
                F.sum("severe_case_count").alias("total_severe_cases"),
                F.countDistinct("encounter_date").alias("reporting_days"),
                F.avg("case_count").alias("mean_daily_cases"),
                F.max("case_count").alias("peak_daily_cases"),
                F.sum(
                    F.when(F.col("ground_truth_outbreak"), 1).otherwise(0)
                ).alias("labelled_outbreak_days"),
            )
        )

        summary.write.mode("overwrite").parquet(str(SUMMARY_PATH))

        print(f"Daily rows: {daily.count():,}")
        print(f"District-disease summary rows: {summary.count():,}")
        print(f"Daily Gold saved to: {DAILY_PATH}")
        print(f"Summary saved to: {SUMMARY_PATH}")

        daily.orderBy(F.desc("case_count")).show(20, truncate=False)

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
