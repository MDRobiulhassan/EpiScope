
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

ROOT = Path(__file__).resolve().parents[2]

DAILY_PATH = ROOT / "data" / "gold" / "daily_cases"
SCORES_PATH = ROOT / "data" / "gold" / "outbreak_scores"
OUTPUT_PATH = ROOT / "data" / "gold" / "detection_evaluation"


def main():
    spark = (
        SparkSession.builder
        .appName("EpiScope-Detection-Evaluation")
        .master("local[*]")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    try:
        truth = (
            spark.read.parquet(str(DAILY_PATH))
            .select(
                "encounter_date", "district", "disease",
                F.col("ground_truth_outbreak").cast("boolean"),
            )
            .dropDuplicates(["encounter_date", "district", "disease"])
        )

        scores = spark.read.parquet(str(SCORES_PATH))

        evaluated = (
            scores.alias("s")
            .join(
                truth.alias("t"),
                on=["encounter_date", "district", "disease"],
                how="left",
            )
            .withColumn(
                "actual_outbreak",
                F.coalesce(F.col("ground_truth_outbreak"), F.lit(False)),
            )
            .filter(F.col("baseline_days") >= 14)
            .withColumn(
                "tp",
                F.when(
                    F.col("is_outbreak_alert") & F.col("actual_outbreak"), 1
                ).otherwise(0),
            )
            .withColumn(
                "fp",
                F.when(
                    F.col("is_outbreak_alert") & ~F.col("actual_outbreak"), 1
                ).otherwise(0),
            )
            .withColumn(
                "fn",
                F.when(
                    ~F.col("is_outbreak_alert") & F.col("actual_outbreak"), 1
                ).otherwise(0),
            )
            .withColumn(
                "tn",
                F.when(
                    ~F.col("is_outbreak_alert") & ~F.col("actual_outbreak"), 1
                ).otherwise(0),
            )
        )

        metrics = evaluated.agg(
            F.sum("tp").alias("true_positives"),
            F.sum("fp").alias("false_positives"),
            F.sum("fn").alias("false_negatives"),
            F.sum("tn").alias("true_negatives"),
        )

        result = (
            metrics
            .withColumn(
                "sensitivity",
                F.when(
                    F.col("true_positives") + F.col("false_negatives") > 0,
                    F.col("true_positives")
                    / (F.col("true_positives") + F.col("false_negatives")),
                ),
            )
            .withColumn(
                "false_positive_rate",
                F.when(
                    F.col("false_positives") + F.col("true_negatives") > 0,
                    F.col("false_positives")
                    / (F.col("false_positives") + F.col("true_negatives")),
                ),
            )
            .withColumn(
                "evaluation_unit",
                F.lit("district-disease-day with at least 14 baseline days"),
            )
        )

        result.write.mode("overwrite").json(str(OUTPUT_PATH))

        print("--- Detection evaluation ---")
        result.show(truncate=False)
        print(f"Metrics saved to: {OUTPUT_PATH}")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
