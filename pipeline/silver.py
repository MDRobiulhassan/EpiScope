
from pathlib import Path
import shutil

from pyspark import StorageLevel
from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = ROOT / "data" / "bronze" / "encounters_parquet"
CLEAN_PATH = ROOT / "data" / "silver" / "encounters"
QUARANTINE_PATH = ROOT / "data" / "silver" / "quarantine"
REPORT_PATH = ROOT / "data" / "silver" / "quality_report"

LOCAL_ROOT = Path("/content/episcope_silver")
LOCAL_CLEAN = LOCAL_ROOT / "encounters"
LOCAL_QUARANTINE = LOCAL_ROOT / "quarantine"
LOCAL_REPORT = LOCAL_ROOT / "quality_report"

VALID_DISEASES = [
    "Dengue",
    "Diarrhoea",
    "Malaria",
    "Respiratory Infection",
    "Typhoid",
]

VALID_SEVERITIES = ["mild", "moderate", "severe"]

RULES = [
    ("DQ01", "Missing encounter ID"),
    ("DQ02", "Invalid encounter date"),
    ("DQ03", "Date outside 2021-2025"),
    ("DQ04", "Missing district"),
    ("DQ05", "Unknown disease"),
    ("DQ06", "Invalid age"),
    ("DQ07", "Invalid severity"),
    ("DQ08", "Invalid temperature"),
    ("DQ09", "Invalid rainfall"),
    ("DQ10", "Duplicate encounter ID"),
    ("DQ11", "Non-positive encounter ID"),
    ("DQ12", "Missing disease or severity"),
]


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def remove_path(path):
    """Remove a file or directory if it exists."""
    path = Path(path)

    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def copy_verified_directory(source, destination):
    """
    Copy a completed local output into a temporary Drive directory.
    Verify file sizes before replacing the existing destination.
    """
    source = Path(source)
    destination = Path(destination)
    temporary = destination.with_name(destination.name + ".__tmp__")

    remove_path(temporary)
    destination.parent.mkdir(parents=True, exist_ok=True)

    shutil.copytree(source, temporary)

    source_files = {
        p.relative_to(source): p.stat().st_size
        for p in source.rglob("*")
        if p.is_file()
    }

    copied_files = {
        p.relative_to(temporary): p.stat().st_size
        for p in temporary.rglob("*")
        if p.is_file()
    }

    if source_files != copied_files:
        remove_path(temporary)
        raise RuntimeError(
            f"Copied files do not match source files for {destination}. "
            "The existing destination has not been replaced."
        )

    empty_parquet = [
        p for p in temporary.rglob("*.parquet")
        if p.stat().st_size == 0
    ]

    if empty_parquet:
        remove_path(temporary)
        raise RuntimeError(
            f"Found {len(empty_parquet)} zero-byte Parquet files "
            f"while copying {destination}. Existing destination "
            "has not been replaced."
        )

    # Replace the destination only after the copy has been checked.
    remove_path(destination)
    temporary.rename(destination)

    print(f"Copied and size-verified: {destination}")


# ---------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------

def main():
    spark = (
        SparkSession.builder
        .appName("EpiScope-Silver-Validation")
        .master("local[*]")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")

    cached_frames = []

    try:
        # 1. Read Bronze data.
        print("Reading Bronze data...")

        raw = spark.read.parquet(str(INPUT_PATH))

        required_columns = {
            "encounter_id",
            "encounter_date",
            "district",
            "disease",
            "age",
            "severity",
            "temperature_c",
            "rainfall_mm",
            "synthetic_outbreak",
            "source",
        }

        missing = required_columns - set(raw.columns)

        if missing:
            raise ValueError(
                f"Bronze data is missing required columns: "
                f"{sorted(missing)}"
            )

        # 2. Normalize and cast columns.
        df = (
            raw
            .withColumn(
                "encounter_id",
                F.col("encounter_id").cast("long"),
            )
            .withColumn(
                "encounter_date",
                F.to_date(F.col("encounter_date").cast("string")),
            )
            .withColumn(
                "district",
                F.trim(F.col("district").cast("string")),
            )
            .withColumn(
                "disease",
                F.trim(F.col("disease").cast("string")),
            )
            .withColumn(
                "age",
                F.col("age").cast("int"),
            )
            .withColumn(
                "severity",
                F.lower(F.trim(F.col("severity"))),
            )
            .withColumn(
                "temperature_c",
                F.col("temperature_c").cast("double"),
            )
            .withColumn(
                "rainfall_mm",
                F.col("rainfall_mm").cast("double"),
            )
            .withColumn(
                "synthetic_outbreak",
                F.col("synthetic_outbreak").cast("boolean"),
            )
            .withColumn(
                "source",
                F.trim(F.col("source").cast("string")),
            )
        )

        # 3. Detect duplicate encounter IDs.
        id_window = Window.partitionBy("encounter_id")

        df = df.withColumn(
            "_id_count",
            F.count(F.lit(1)).over(id_window),
        )

        # 4. Define all 12 quality-rule conditions.
        conditions = [
            # DQ01: Missing encounter ID
            F.col("encounter_id").isNull(),

            # DQ02: Invalid encounter date
            F.col("encounter_date").isNull(),

            # DQ03: Date outside 2021-2025
            F.col("encounter_date").isNotNull()
            & (
                (
                    F.col("encounter_date")
                    < F.lit("2021-01-01").cast("date")
                )
                | (
                    F.col("encounter_date")
                    > F.lit("2025-12-31").cast("date")
                )
            ),

            # DQ04: Missing district
            F.col("district").isNull()
            | (F.col("district") == ""),

            # DQ05: Unknown disease
            F.col("disease").isNull()
            | (~F.col("disease").isin(VALID_DISEASES)),

            # DQ06: Invalid age
            F.col("age").isNull()
            | (F.col("age") < 0)
            | (F.col("age") > 120),

            # DQ07: Invalid severity
            F.col("severity").isNull()
            | (~F.col("severity").isin(VALID_SEVERITIES)),

            # DQ08: Invalid temperature
            F.col("temperature_c").isNull()
            | (F.col("temperature_c") < -20)
            | (F.col("temperature_c") > 60),

            # DQ09: Invalid rainfall
            F.col("rainfall_mm").isNull()
            | (F.col("rainfall_mm") < 0)
            | (F.col("rainfall_mm") > 1000),

            # DQ10: Duplicate encounter ID
            F.col("_id_count") > 1,

            # DQ11: Non-positive encounter ID
            F.col("encounter_id").isNotNull()
            & (F.col("encounter_id") <= 0),

            # DQ12: Missing disease or severity
            F.col("disease").isNull()
            | F.col("severity").isNull(),
        ]

        # 5. Build the quality-error array.
        error_array = F.array(
            *[
                F.when(condition, F.lit(rule_id))
                for (rule_id, _), condition
                in zip(RULES, conditions)
            ]
        )

        # 6. Classify and cache records.
        checked = (
            df
            .withColumn(
                "_quality_errors",
                F.filter(
                    error_array,
                    lambda item: item.isNotNull(),
                ),
            )
            .withColumn(
                "_is_valid",
                F.size("_quality_errors") == 0,
            )
        ).persist(StorageLevel.MEMORY_AND_DISK)

        cached_frames.append(checked)

        input_count = checked.count()

        clean = (
            checked
            .filter(F.col("_is_valid"))
            .drop("_id_count", "_quality_errors", "_is_valid")
            .persist(StorageLevel.MEMORY_AND_DISK)
        )

        quarantine = (
            checked
            .filter(~F.col("_is_valid"))
            .persist(StorageLevel.MEMORY_AND_DISK)
        )

        cached_frames.extend([clean, quarantine])

        # 7. Count records and verify accounting.
        clean_count = clean.count()
        quarantine_count = quarantine.count()

        print("\nRecord counts before writing:")
        print(f"Input:      {input_count:,}")
        print(f"Clean:      {clean_count:,}")
        print(f"Quarantine: {quarantine_count:,}")
        print(f"Total:      {clean_count + quarantine_count:,}")

        if clean_count + quarantine_count != input_count:
            raise RuntimeError(
                "Record accounting failed: clean + quarantine "
                "does not equal input."
            )

        # 8. Calculate all 12 rule counts in one aggregation.
        # Rule counts can overlap if a record violates multiple rules.
        rule_counts = checked.agg(
            *[
                F.sum(
                    F.when(condition, 1).otherwise(0)
                ).alias(rule_id)
                for (rule_id, _), condition
                in zip(RULES, conditions)
            ]
        ).first()

        report_rows = [
            (
                rule_id,
                description,
                int(rule_counts[rule_id] or 0),
            )
            for rule_id, description in RULES
        ]

        report = spark.createDataFrame(
            report_rows,
            ["rule_id", "description", "failed_records"],
        )

        # 9. Write outputs to local disk, NOT directly to Google Drive.
        print("\nPreparing local output directory...")
        remove_path(LOCAL_ROOT)
        LOCAL_ROOT.mkdir(parents=True, exist_ok=True)

        print("Writing clean records locally...")
        clean.write.mode("overwrite").parquet(str(LOCAL_CLEAN))

        print("Writing quarantine records locally...")
        quarantine.write.mode("overwrite").parquet(
            str(LOCAL_QUARANTINE)
        )

        print("Writing quality report locally...")
        (
            report.coalesce(1)
            .write.mode("overwrite")
            .option("header", True)
            .csv(str(LOCAL_REPORT))
        )

        # 10. Verify that local Parquet files are readable.
        print("\nVerifying local Parquet outputs...")

        local_clean_count = spark.read.parquet(
            str(LOCAL_CLEAN)
        ).count()

        local_quarantine_count = spark.read.parquet(
            str(LOCAL_QUARANTINE)
        ).count()

        local_total = local_clean_count + local_quarantine_count

        print(f"Local clean:      {local_clean_count:,}")
        print(f"Local quarantine: {local_quarantine_count:,}")
        print(f"Local total:      {local_total:,}")

        if local_clean_count != clean_count:
            raise RuntimeError(
                "Local clean output count does not match "
                "the pre-write count."
            )

        if local_quarantine_count != quarantine_count:
            raise RuntimeError(
                "Local quarantine output count does not match "
                "the pre-write count."
            )

        if local_total != input_count:
            raise RuntimeError(
                "Local output total does not match input count."
            )

        # Also ensure local Parquet files are not zero bytes.
        for folder in [LOCAL_CLEAN, LOCAL_QUARANTINE]:
            empty_files = [
                p for p in folder.rglob("*.parquet")
                if p.stat().st_size == 0
            ]

            if empty_files:
                raise RuntimeError(
                    f"Found {len(empty_files)} zero-byte Parquet "
                    f"files in local output: {folder}"
                )

        # 11. Copy verified local outputs to Drive.
        print("\nCopying verified outputs to Google Drive...")

        copy_verified_directory(LOCAL_CLEAN, CLEAN_PATH)
        copy_verified_directory(LOCAL_QUARANTINE, QUARANTINE_PATH)
        copy_verified_directory(LOCAL_REPORT, REPORT_PATH)

        # 12. Final verification: read the copied outputs from Drive.
        print("\nVerifying copied Google Drive outputs...")

        drive_clean_count = spark.read.parquet(
            str(CLEAN_PATH)
        ).count()

        drive_quarantine_count = spark.read.parquet(
            str(QUARANTINE_PATH)
        ).count()

        drive_total = drive_clean_count + drive_quarantine_count

        print(f"Drive clean:      {drive_clean_count:,}")
        print(f"Drive quarantine: {drive_quarantine_count:,}")
        print(f"Drive total:      {drive_total:,}")

        if (
            drive_clean_count != clean_count
            or drive_quarantine_count != quarantine_count
            or drive_total != input_count
        ):
            raise RuntimeError(
                "Google Drive verification failed. "
                "Drive counts do not match the verified local outputs."
            )

        # 13. Success summary.
        print("\nSilver pipeline completed successfully.")
        print(f"Input:      {input_count:,}")
        print(f"Clean:      {drive_clean_count:,}")
        print(f"Quarantine: {drive_quarantine_count:,}")
        print(f"Total:      {drive_total:,}")
        print(f"Quality report: {REPORT_PATH}")

        print("\nData quality report:")
        report.orderBy("rule_id").show(20, truncate=False)

    finally:
        # Release persisted data only after all dependent actions finish.
        for frame in reversed(cached_frames):
            frame.unpersist()

        spark.stop()


if __name__ == "__main__":
    main()
