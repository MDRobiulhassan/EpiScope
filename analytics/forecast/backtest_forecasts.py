from datetime import timedelta
from pathlib import Path

from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F

ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = ROOT / "data" / "gold" / "daily_cases"
OUTPUT_PATH = ROOT / "data" / "gold" / "forecast_backtest"
TEST_DAYS = 28
HISTORY_DAYS = 364


def main():
    spark = (
        SparkSession.builder
        .appName("EpiScope-Forecast-Rolling-Backtest")
        .master("local[*]")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    try:
        daily = (
            spark.read.parquet(str(INPUT_PATH))
            .select("encounter_date", "district", "disease", "case_count")
            .groupBy("encounter_date", "district", "disease")
            .agg(F.sum("case_count").cast("double").alias("actual"))
        )
        latest = daily.agg(F.max("encounter_date").alias("latest")).first()["latest"]
        test_start = latest - timedelta(days=TEST_DAYS - 1)
        history_start = test_start - timedelta(days=HISTORY_DAYS)
        history = daily.filter(
            (F.col("encounter_date") >= F.lit(history_start))
            & (F.col("encounter_date") < F.lit(test_start))
        )
        statistics = history.groupBy("district", "disease").agg(
            F.avg("actual").alias("mean_prediction"),
            F.stddev_pop("actual").alias("history_stddev"),
        )
        actual = daily.filter(F.col("encounter_date") >= F.lit(test_start))
        evaluated = (
            actual.join(statistics, ["district", "disease"], "left")
            .withColumn("prediction", F.coalesce("mean_prediction", F.lit(0.0)))
            .withColumn("lower_80", F.greatest(F.lit(0.0), F.col("prediction") - 1.2816 * F.coalesce("history_stddev", F.lit(0.0))))
            .withColumn("upper_80", F.col("prediction") + 1.2816 * F.coalesce("history_stddev", F.lit(0.0)))
            .withColumn("covered_80", (F.col("actual") >= F.col("lower_80")) & (F.col("actual") <= F.col("upper_80")))
        )
        result = evaluated.agg(
            F.count("*").alias("observations"),
            F.avg(F.abs(F.col("actual") - F.col("prediction"))).alias("mae"),
            F.avg(F.col("covered_80").cast("double")).alias("coverage_80"),
        ).withColumn("test_start", F.lit(str(test_start))).withColumn("test_end", F.lit(str(latest)))
        result.write.mode("overwrite").json(str(OUTPUT_PATH))
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
