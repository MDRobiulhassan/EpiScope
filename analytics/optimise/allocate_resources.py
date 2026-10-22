
from pathlib import Path

from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FORECAST_PATH = PROJECT_ROOT / "data" / "gold" / "case_forecasts"
OUTPUT_PATH = PROJECT_ROOT / "data" / "gold" / "resource_allocations"

# Illustrative planning assumptions. Replace with documented assignment inputs.
TOTAL_RESOURCE_UNITS = 100
MINIMUM_PER_DISTRICT = 1
SEVERE_CASE_WEIGHT = 3.0


def main():
    spark = (
        SparkSession.builder
        .appName("EpiScope-Resource-Allocation")
        .master("local[*]")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    try:
        forecasts = spark.read.parquet(str(FORECAST_PATH))

        # Aggregate predicted demand across all diseases and forecast days.
        demand = (
            forecasts
            .groupBy("district")
            .agg(
                F.sum("forecast_cases").alias("forecast_case_demand"),
                F.countDistinct("forecast_date").alias("forecast_days"),
            )
            .withColumn(
                "priority_score",
                F.col("forecast_case_demand") * SEVERE_CASE_WEIGHT,
            )
        )

        district_count = demand.count()
        if district_count == 0:
            raise ValueError("No forecast data available for allocation.")

        # This example assumes one minimum unit per district.
        available_after_minimum = (
            TOTAL_RESOURCE_UNITS
            - district_count * MINIMUM_PER_DISTRICT
        )

        if available_after_minimum < 0:
            raise ValueError(
                f"{TOTAL_RESOURCE_UNITS} resource units cannot provide "
                f"{MINIMUM_PER_DISTRICT} unit(s) to each of "
                f"{district_count} districts."
            )

        total_priority = demand.agg(
            F.sum("priority_score").alias("total")
        ).first()["total"] or 0.0

        if total_priority <= 0:
            demand = demand.withColumn(
                "priority_score", F.lit(1.0)
            )
            total_priority = float(district_count)

        # Allocate remaining units proportionally using the largest-remainder
        # method so the final integer allocations sum to the available total.
        allocation = (
            demand
            .withColumn(
                "_exact_extra",
                F.lit(float(available_after_minimum))
                * F.col("priority_score")
                / F.lit(float(total_priority)),
            )
            .withColumn(
                "_floor_extra",
                F.floor("_exact_extra").cast("int"),
            )
            .withColumn(
                "_fraction",
                F.col("_exact_extra") - F.col("_floor_extra"),
            )
        )

        allocated_floor = allocation.agg(
            F.sum("_floor_extra").alias("total")
        ).first()["total"] or 0

        remaining_units = available_after_minimum - int(allocated_floor)

        remainder_window = Window.orderBy(
            F.desc("_fraction"), F.asc("district")
        )

        allocation = (
            allocation
            .withColumn(
                "_remainder_rank",
                F.row_number().over(remainder_window),
            )
            .withColumn(
                "extra_unit",
                F.when(
                    F.col("_remainder_rank") <= remaining_units, 1
                ).otherwise(0),
            )
            .withColumn(
                "allocated_units",
                F.lit(MINIMUM_PER_DISTRICT)
                + F.col("_floor_extra")
                + F.col("extra_unit"),
            )
            .withColumn(
                "allocation_method",
                F.lit("minimum-plus-proportional-largest-remainder"),
            )
            .select(
                "district",
                "forecast_case_demand",
                "forecast_days",
                "priority_score",
                "allocated_units",
                "allocation_method",
            )
        )

        allocation.write.mode("overwrite").parquet(str(OUTPUT_PATH))

        total_allocated = allocation.agg(
            F.sum("allocated_units").alias("total")
        ).first()["total"]

        print(f"Districts: {district_count}")
        print(f"Resource budget: {TOTAL_RESOURCE_UNITS}")
        print(f"Resources allocated: {total_allocated}")
        print(f"Saved allocations to: {OUTPUT_PATH}")

        allocation.orderBy(
            F.desc("allocated_units"), "district"
        ).show(64, truncate=False)

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
