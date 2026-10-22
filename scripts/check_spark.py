
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "data" / "gold" / "smoke_test"


def main():
    spark = (
        SparkSession.builder
        .appName("EpiScope-Initial-Spark-Test")
        .master("local[*]")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")

    try:
        # Temporary sample data to verify Spark.
        records = [
            ("Chattogram", "Dengue", 120),
            ("Chattogram", "Dengue", 80),
            ("Dhaka", "Dengue", 250),
            ("Dhaka", "Diarrhoea", 90),
            ("Sylhet", "Malaria", 40),
        ]

        columns = ["district", "disease", "cases"]

        df = spark.createDataFrame(records, columns)

        print("\n--- Input records ---")
        df.show()

        # Aggregate records by district and disease.
        gold_df = (
            df.groupBy("district", "disease")
            .agg(F.sum("cases").alias("total_cases"))
            .orderBy("district", "disease")
        )

        print("\n--- Gold-layer sample output ---")
        gold_df.show()

        # Write actual Parquet files.
        (
            gold_df.write
            .mode("overwrite")
            .parquet(str(OUTPUT_PATH))
        )

        # Read the saved Parquet files to verify persistence.
        saved_df = spark.read.parquet(str(OUTPUT_PATH))

        print(f"\nSaved Parquet data to: {OUTPUT_PATH}")
        print(f"Output rows: {saved_df.count()}")
        saved_df.show()

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
