
from pathlib import Path

from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F

ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = ROOT / "data" / "gold" / "daily_cases"
OUTPUT_PATH = ROOT / "data" / "gold" / "forecast_evaluation"

HISTORY_DAYS = 7
TEST_DAYS = 28


def main():
    spark = (
        SparkSession.builder
        .appName("EpiScope-Forecast-Evaluation")
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
            raise ValueError(f"No Gold records found at {INPUT_PATH}")

        # Build a complete daily calendar so missing dates count as zero.
        combinations = daily.select("district", "disease").distinct()

        bounds = daily.agg(
            F.min("encounter_date").alias("min_date"),
            F.max("encounter_date").alias("max_date"),
        )

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

        complete = (
            calendar.join(
                daily,
                on=["district", "disease", "encounter_date"],
                how="left",
            )
            .fillna({"case_count": 0.0})
        )

        # Use the last 28 observed calendar days as the test period.
        latest_date = bounds.first()["max_date"]
        test_start = latest_date - __import__("datetime").timedelta(
            days=TEST_DAYS - 1
        )
        history_start = test_start - __import__("datetime").timedelta(
            days=HISTORY_DAYS
        )

        training = (
            complete
            .filter(
                (F.col("encounter_date") >= F.lit(history_start))
                & (F.col("encounter_date") < F.lit(test_start))
            )
            .groupBy("district", "disease")
            .agg(F.avg("case_count").alias("predicted_cases"))
        )

        actual = (
            complete
            .filter(F.col("encounter_date") >= F.lit(test_start))
            .withColumn(
                "test_day",
                F.row_number().over(
                    Window.partitionBy("district", "disease")
                    .orderBy("encounter_date")
                ),
            )
            .filter(F.col("test_day") <= TEST_DAYS)
        )

        evaluated = (
            actual.join(
                training,
                on=["district", "disease"],
                how="left",
            )
            .withColumn(
                "predicted_cases",
                F.coalesce(F.col("predicted_cases"), F.lit(0.0)),
            )
            .withColumn(
                "error",
                F.col("case_count") - F.col("predicted_cases"),
            )
            .withColumn("absolute_error", F.abs("error"))
            .withColumn("squared_error", F.pow("error", 2))
        )

        def metrics(frame):
            return frame.agg(
                F.count("*").alias("observations"),
                F.avg("absolute_error").alias("mae"),
                F.sqrt(F.avg("squared_error")).alias("rmse"),
            )

        overall = (
            metrics(evaluated)
            .withColumn("test_start", F.lit(test_start.isoformat()))
            .withColumn("test_end", F.lit(latest_date.isoformat()))
            .withColumn(
                "model",
                F.lit("7-day-average-fixed-28-day-horizon"),
            )
        )

        by_district_disease = (
            evaluated
            .groupBy("district", "disease")
            .agg(
                F.count("*").alias("observations"),
                F.avg("absolute_error").alias("mae"),
                F.sqrt(F.avg("squared_error")).alias("rmse"),
            )
        )

        overall.coalesce(1).write.mode("overwrite").json(
            str(OUTPUT_PATH / "overall")
        )
        by_district_disease.write.mode("overwrite").parquet(
            str(OUTPUT_PATH / "by_district_disease")
        )

        print("--- Overall forecast metrics ---")
        overall.show(truncate=False)

        print("--- Highest MAE by district and disease ---")
        by_district_disease.orderBy(
            F.desc("mae")
        ).show(20, truncate=False)

        print(f"Evaluation outputs saved to: {OUTPUT_PATH}")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
