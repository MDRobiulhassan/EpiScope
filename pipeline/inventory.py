"""Idempotently ingest and layer daily facility inventory snapshots."""

from pathlib import Path
import shutil
import tempfile

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "incremental_drop" / "inventory_snapshot.csv"
BRONZE_PATH = ROOT / "data" / "bronze" / "inventory_snapshots"
SILVER_PATH = ROOT / "data" / "silver" / "inventory_snapshots"
QUARANTINE_PATH = ROOT / "data" / "silver" / "inventory_quarantine"
GOLD_PATH = ROOT / "data" / "gold" / "daily_inventory_by_district"
LOCAL_ROOT = Path(tempfile.gettempdir()) / "episcope_inventory_pipeline"
LOCAL_BRONZE = LOCAL_ROOT / "bronze"
LOCAL_SILVER = LOCAL_ROOT / "silver"
LOCAL_QUARANTINE = LOCAL_ROOT / "quarantine"
LOCAL_GOLD = LOCAL_ROOT / "gold"

KEY_COLUMNS = ["snapshot_date", "facility_id"]
VALUE_COLUMNS = [
    "total_beds",
    "occupied_beds",
    "iv_saline_units",
    "ns1_test_kits",
    "ors_sachets",
    "antimalarial_courses",
]
SOURCE_COLUMNS = [
    "snapshot_date",
    "facility_id",
    "district",
    *VALUE_COLUMNS,
    "source",
]


def remove_path(path):
    path = Path(path)
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def copy_verified_directory(source, destination):
    """Copy a local Spark output to Drive and replace only after verification."""
    source = Path(source)
    destination = Path(destination)
    temporary = destination.with_name(destination.name + ".__tmp__")
    remove_path(temporary)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, temporary)

    source_files = {
        path.relative_to(source): path.stat().st_size
        for path in source.rglob("*")
        if path.is_file()
    }
    copied_files = {
        path.relative_to(temporary): path.stat().st_size
        for path in temporary.rglob("*")
        if path.is_file()
    }
    if source_files != copied_files:
        remove_path(temporary)
        raise RuntimeError(
            f"Copied files do not match the local output for {destination}. "
            "The previous destination has not been replaced."
        )

    empty_parquet = [
        path for path in temporary.rglob("*.parquet")
        if path.stat().st_size == 0
    ]
    if empty_parquet:
        remove_path(temporary)
        raise RuntimeError(
            f"Found {len(empty_parquet)} zero-byte Parquet files in {destination}."
        )

    remove_path(destination)
    temporary.rename(destination)
    print(f"Copied and size-verified: {destination}")


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Incremental inventory CSV not found: {INPUT_PATH}\n"
            "Run generator/generate_inventory_drop.py first."
        )

    spark = (
        SparkSession.builder
        .appName("EpiScope-Incremental-Inventory")
        .master("local[*]")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    try:
        remove_path(LOCAL_ROOT)
        incoming = spark.read.option("header", True).option(
            "inferSchema", True
        ).csv(str(INPUT_PATH))

        missing = set(SOURCE_COLUMNS) - set(incoming.columns)
        if missing:
            raise ValueError(
                f"Inventory input is missing columns: {sorted(missing)}"
            )

        incoming = (
            incoming.select(*SOURCE_COLUMNS)
            .withColumn("snapshot_date", F.to_date("snapshot_date"))
            .withColumn("facility_id", F.trim(F.col("facility_id")))
            .withColumn("district", F.trim(F.col("district")))
            .withColumn("_source_file", F.input_file_name())
            .withColumn("_ingested_at", F.current_timestamp())
            .dropDuplicates(KEY_COLUMNS)
        )

        incoming_count = incoming.count()
        if BRONZE_PATH.exists():
            existing = spark.read.parquet(str(BRONZE_PATH))
            existing_keys = existing.select(*KEY_COLUMNS).dropDuplicates()
            new_rows = incoming.join(existing_keys, KEY_COLUMNS, "left_anti")
            existing_count = existing.count()
        else:
            existing = None
            new_rows = incoming
            existing_count = 0

        appended_count = new_rows.count()
        if appended_count:
            bronze = (
                existing.unionByName(new_rows)
                if existing is not None
                else new_rows
            )
            bronze.write.mode("overwrite").parquet(str(LOCAL_BRONZE))
            local_bronze = spark.read.parquet(str(LOCAL_BRONZE))
            if local_bronze.count() != existing_count + appended_count:
                raise RuntimeError("Local Bronze output row count did not reconcile.")
            copy_verified_directory(LOCAL_BRONZE, BRONZE_PATH)
            bronze = local_bronze
        else:
            bronze = existing if existing is not None else incoming

        bronze_count = bronze.count()

        numeric_nonnegative = F.lit(True)
        for column in VALUE_COLUMNS:
            numeric_nonnegative = numeric_nonnegative & F.col(column).isNotNull() & (
                F.col(column) >= 0
            )

        valid = (
            F.col("snapshot_date").isNotNull()
            & F.col("facility_id").isNotNull()
            & (F.col("facility_id") != "")
            & F.col("district").isNotNull()
            & (F.col("district") != "")
            & numeric_nonnegative
            & (F.col("total_beds") > 0)
            & (F.col("occupied_beds") <= F.col("total_beds"))
        )

        checked = bronze.withColumn("_is_valid", valid)
        clean = checked.filter(F.col("_is_valid")).drop("_is_valid")
        quarantine = checked.filter(~F.col("_is_valid")).drop("_is_valid")

        bronze_count = checked.count()
        clean_count = clean.count()
        quarantine_count = quarantine.count()
        if clean_count + quarantine_count != bronze_count:
            raise RuntimeError("Inventory clean and quarantine counts do not reconcile.")

        clean.write.mode("overwrite").parquet(str(LOCAL_SILVER))
        quarantine.write.mode("overwrite").parquet(str(LOCAL_QUARANTINE))
        gold = (
            clean.groupBy("snapshot_date", "district")
            .agg(
                F.countDistinct("facility_id").alias("facility_count"),
                F.sum("total_beds").alias("total_beds"),
                F.sum("occupied_beds").alias("occupied_beds"),
                F.sum("iv_saline_units").alias("iv_saline_units"),
                F.sum("ns1_test_kits").alias("ns1_test_kits"),
                F.sum("ors_sachets").alias("ors_sachets"),
                F.sum("antimalarial_courses").alias("antimalarial_courses"),
            )
            .withColumn(
                "bed_occupancy_rate",
                F.when(
                    F.col("total_beds") > 0,
                    F.col("occupied_beds") / F.col("total_beds"),
                ),
            )
        )
        gold.write.mode("overwrite").parquet(str(LOCAL_GOLD))

        copy_verified_directory(LOCAL_SILVER, SILVER_PATH)
        copy_verified_directory(LOCAL_QUARANTINE, QUARANTINE_PATH)
        copy_verified_directory(LOCAL_GOLD, GOLD_PATH)

        print(f"Input snapshot rows: {incoming_count:,}")
        print(f"Rows appended this run: {appended_count:,}")
        print(f"Bronze inventory rows: {bronze_count:,}")
        print(f"Silver clean rows: {clean_count:,}")
        print(f"Silver quarantined rows: {quarantine_count:,}")
        print(f"Gold district-day rows: {gold.count():,}")
        print(f"Bronze: {BRONZE_PATH}")
        print(f"Silver: {SILVER_PATH}")
        print(f"Quarantine: {QUARANTINE_PATH}")
        print(f"Gold: {GOLD_PATH}")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
