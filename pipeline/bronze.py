
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "bronze"
    / "encounters"
    / "encounters.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "bronze"
    / "encounters_parquet"
)


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input CSV not found: {INPUT_PATH}\n"
            "Run: python generator/generate_encounters.py --rows 10000"
        )

    spark = (
        SparkSession.builder
        .appName("EpiScope-Bronze-Ingestion")
        .master("local[*]")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")

    try:
        raw_df = (
            spark.read
            .option("header", True)
            .option("inferSchema", True)
            .csv(str(INPUT_PATH))
        )

        # Add ingestion metadata without modifying source fields.
        bronze_df = (
            raw_df
            .withColumn("_source_file", F.input_file_name())
            .withColumn("_ingested_at", F.current_timestamp())
        )

        (
            bronze_df.write
            .mode("overwrite")
            .parquet(str(OUTPUT_PATH))
        )

        saved_df = spark.read.parquet(str(OUTPUT_PATH))

        print(f"Input rows: {raw_df.count():,}")
        print(f"Bronze rows: {saved_df.count():,}")
        print(f"Saved to: {OUTPUT_PATH}")
        saved_df.printSchema()
        saved_df.show(5, truncate=False)

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
