from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

ROOT = Path(__file__).resolve().parents[2]
FORECAST_PATH = ROOT / "data" / "gold" / "case_forecasts"
OUTPUT_PATH = ROOT / "data" / "gold" / "equity_budget_curve"
BUDGETS = [64, 80, 100, 125, 150]


def main():
    spark = SparkSession.builder.appName("EpiScope-Equity-Budget-Curve").master("local[*]").getOrCreate()
    try:
        demand = spark.read.parquet(str(FORECAST_PATH)).groupBy("district").agg(
            F.sum("forecast_cases").alias("demand")
        )
        total_demand = demand.agg(F.sum("demand")).first()[0] or 1.0
        rows = []
        for budget in BUDGETS:
            allocated = demand.withColumn("allocation", F.least(F.col("demand"), F.lit(float(budget)) * F.col("demand") / F.lit(float(total_demand))))
            metrics = allocated.agg(
                F.sum("demand").alias("total_demand"),
                F.sum("allocation").alias("allocated"),
                F.avg(F.when(F.col("allocation") > 0, 1.0).otherwise(0.0)).alias("district_coverage"),
            ).first()
            rows.append((budget, float(metrics["total_demand"]), float(metrics["allocated"]), float(metrics["district_coverage"])))
        spark.createDataFrame(rows, ["budget", "total_demand", "allocated_demand", "district_coverage"]).write.mode("overwrite").json(str(OUTPUT_PATH))
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
