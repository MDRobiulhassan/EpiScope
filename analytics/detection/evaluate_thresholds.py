from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

ROOT = Path(__file__).resolve().parents[2]
SCORES_PATH = ROOT / "data" / "gold" / "outbreak_scores"
TRUTH_PATH = ROOT / "data" / "gold" / "daily_cases"
OUTPUT_PATH = ROOT / "data" / "gold" / "detection_threshold_tradeoff"
THRESHOLDS = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0]


def main():
    spark = (
        SparkSession.builder
        .appName("EpiScope-Detection-Threshold-Evaluation")
        .master("local[*]")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    try:
        truth = spark.read.parquet(str(TRUTH_PATH)).select(
            "encounter_date", "district", "disease", "ground_truth_outbreak"
        )
        scores = (
            spark.read.parquet(str(SCORES_PATH))
            .join(truth, ["encounter_date", "district", "disease"], "left")
            .filter(F.col("baseline_days") >= 14)
            .withColumn(
                "alert_score",
                F.when(
                    F.col("baseline_stddev") > 0,
                    (F.col("case_count") - F.col("baseline_mean"))
                    / F.col("baseline_stddev"),
                ).otherwise(F.lit(0.0)),
            )
        )
        threshold_rows = spark.createDataFrame([(value,) for value in THRESHOLDS], ["threshold"])
        evaluated = (
            scores.crossJoin(threshold_rows)
            .withColumn("predicted", F.col("alert_score") >= F.col("threshold"))
            .withColumn("actual", F.coalesce(F.col("ground_truth_outbreak"), F.lit(False)))
            .groupBy("threshold")
            .agg(
                F.sum(F.when(F.col("predicted") & F.col("actual"), 1).otherwise(0)).alias("true_positives"),
                F.sum(F.when(F.col("predicted") & ~F.col("actual"), 1).otherwise(0)).alias("false_positives"),
                F.sum(F.when(~F.col("predicted") & F.col("actual"), 1).otherwise(0)).alias("false_negatives"),
                F.sum(F.when(~F.col("predicted") & ~F.col("actual"), 1).otherwise(0)).alias("true_negatives"),
            )
            .withColumn("sensitivity", F.col("true_positives") / (F.col("true_positives") + F.col("false_negatives")))
            .withColumn("precision", F.col("true_positives") / (F.col("true_positives") + F.col("false_positives")))
            .withColumn("false_alerts_per_district_year", F.col("false_positives") / F.lit(64.0) / F.lit(5.0))
        )
        evaluated.write.mode("overwrite").json(str(OUTPUT_PATH))
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
