import os
import pytest
import sys
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)

@pytest.fixture(scope="session")
def spark():
    spark_session = (
        SparkSession.builder
        .appName("EpiScope-Validation-Tests")
        .master("local[*]")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    yield spark_session
    spark_session.stop()

def test_age_boundaries(spark):
    schema = ["encounter_id", "age"]
    data = [
        (1, 25),   # Valid
        (2, -5),   # Invalid (too low)
        (3, 150),  # Invalid (too high)
        (4, None)  # Invalid (null)
    ]
    df = spark.createDataFrame(data, schema)
    
    valid_df = df.filter(
        (F.col("age").isNotNull()) &
        (F.col("age") >= 0) &
        (F.col("age") <= 120)
    )
    
    results = [row.encounter_id for row in valid_df.collect()]
    assert results == [1]

def test_temperature_boundaries(spark):
    schema = ["encounter_id", "temperature_c"]
    data = [
        (1, 37.0),  # Valid
        (2, 99.9),  # Invalid (too high)
        (3, -25.0)  # Invalid (too low)
    ]
    df = spark.createDataFrame(data, schema)
    
    valid_df = df.filter(
        (F.col("temperature_c").isNotNull()) &
        (F.col("temperature_c") >= -20) &
        (F.col("temperature_c") <= 60)
    )
    
    results = [row.encounter_id for row in valid_df.collect()]
    assert results == [1]
