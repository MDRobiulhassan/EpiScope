
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = ROOT / "data" / "gold" / "daily_cases"
OUTPUT_PATH = ROOT / "data" / "public" / "daily_cases"

SUPPRESSION_THRESHOLD = 5


def main():
    spark = (
        SparkSession.builder
        .appName("EpiScope-Privacy-Safe-Serving")
        .master("local[*]")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    try:
        daily = spark.read.parquet(str(INPUT_PATH))

        required = {
            "encounter_date",
            "district",
            "disease",
            "case_count",
        }
        missing = required - set(daily.columns)
        if missing:
            raise ValueError(
                f"Gold data is missing required columns: {sorted(missing)}"
            )

        # Never publish encounter-level IDs, ground-truth labels,
        # or other internal-only fields.
        public = daily.select(
            "encounter_date",
            "district",
            "disease",
            F.col("case_count").cast("long").alias("case_count"),
        )

        # Suppress counts 1-4. Keep zero counts visible.
        is_suppressed = (
            (F.col("case_count") > 0)
            & (F.col("case_count") < SUPPRESSION_THRESHOLD)
        )

        public = (
            public
            .withColumn("suppressed", is_suppressed)
            .withColumn(
                "published_case_count",
                F.when(
                    is_suppressed,
                    F.lit(None).cast("long"),
                ).otherwise(F.col("case_count")),
            )
            .drop("case_count")
            .withColumn(
                "suppression_reason",
                F.when(
                    F.col("suppressed"),
                    F.lit("Small count suppressed"),
                ).otherwise(F.lit(None).cast("string")),
            )
        )

        public.write.mode("overwrite").partitionBy("district").parquet(
            str(OUTPUT_PATH)
        )

        total_rows = public.count()
        suppressed_rows = public.filter(F.col("suppressed")).count()

        print(f"Published rows: {total_rows:,}")
        print(f"Rows with suppressed counts: {suppressed_rows:,}")
        print(f"Suppression threshold: counts below {SUPPRESSION_THRESHOLD}")
        print(f"Public dataset: {OUTPUT_PATH}")

        print("\n--- Sample published records ---")
        public.select(
            "encounter_date",
            "district",
            "disease",
            "published_case_count",
            "suppressed",
        ).show(20, truncate=False)

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
