
from pathlib import Path

import pulp
from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FORECAST_PATH = PROJECT_ROOT / "data" / "gold" / "case_forecasts"
OUTPUT_PATH = PROJECT_ROOT / "data" / "gold" / "resource_allocations"

# Illustrative planning assumptions. Replace with documented assignment inputs.
TOTAL_RESOURCE_UNITS = 100
MINIMUM_PER_DISTRICT = 1
SEVERE_CASE_WEIGHT = 3.0
UNIT_COST = 1.0


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

        demand_rows = [row.asDict() for row in demand.collect()]
        district_count = len(demand_rows)
        if not demand_rows:
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

        total_priority = sum(float(row["priority_score"] or 0.0) for row in demand_rows)

        if total_priority <= 0:
            for row in demand_rows:
                row["priority_score"] = 1.0
            total_priority = float(district_count)

        model = pulp.LpProblem("episcope_resource_allocation", pulp.LpMinimize)
        allocation_variables = {
            row["district"]: pulp.LpVariable(
                f"allocation_{index}", lowBound=MINIMUM_PER_DISTRICT, cat="Integer"
            )
            for index, row in enumerate(demand_rows)
        }
        unmet_variables = {
            row["district"]: pulp.LpVariable(
                f"unmet_{index}", lowBound=0, cat="Continuous"
            )
            for index, row in enumerate(demand_rows)
        }
        model += pulp.lpSum(
            float(row["priority_score"] or 0.0) * unmet_variables[row["district"]]
            for row in demand_rows
        )
        model += pulp.lpSum(allocation_variables.values()) <= TOTAL_RESOURCE_UNITS
        for row in demand_rows:
            district = row["district"]
            demand_units = float(row["forecast_case_demand"] or 0.0)
            model += unmet_variables[district] >= demand_units - allocation_variables[district]
        if model.solve(pulp.PULP_CBC_CMD(msg=False)) != pulp.LpStatusOptimal:
            raise RuntimeError("The resource allocation model did not solve optimally.")

        allocation_rows = []
        for row in demand_rows:
            district = row["district"]
            allocated = int(round(allocation_variables[district].value() or 0))
            proportional = MINIMUM_PER_DISTRICT + int(
                round(
                    available_after_minimum
                    * float(row["priority_score"] or 0.0)
                    / total_priority
                )
            )
            allocation_rows.append(
                (
                    district,
                    float(row["forecast_case_demand"] or 0.0),
                    int(row["forecast_days"] or 0),
                    float(row["priority_score"] or 0.0),
                    allocated,
                    proportional,
                    max(0.0, float(row["forecast_case_demand"] or 0.0) - allocated),
                    "linear-programme-cbc",
                )
            )

        allocation = spark.createDataFrame(
            allocation_rows,
            [
                "district", "forecast_case_demand", "forecast_days",
                "priority_score", "allocated_units", "population_proportional_units",
                "unmet_demand", "allocation_method",
            ],
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
