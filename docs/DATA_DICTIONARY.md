# Data Dictionary and Provenance

## Purpose

This document describes the datasets used by EpiScope and explains how to verify their actual column names and types. The Python source and current Parquet schemas are authoritative; do not infer column names from dashboard labels.

## Dataset inventory

| Dataset | Location | Purpose |
|---|---|---|
| Source encounters | Input configured for `generator/generate_encounters.py` | Synthetic encounter-level records |
| Bronze encounters | `data/bronze/` | Ingested source records |
| Silver encounters | `data/silver/` | Validated clean records; quarantined records are kept separately according to pipeline configuration |
| Gold outputs | `data/gold/` | Aggregated analytical datasets |
| Public case data | Serving output configured by `build_public_data.py` | Privacy-filtered case information |
| Dashboard cases | `dashboard/data/cases.json` | Case trends and related dashboard views |
| Dashboard alerts | `dashboard/data/alerts.json` | Outbreak-detection output |
| Dashboard forecasts | `dashboard/data/forecasts.json` | Forecast output |
| Dashboard resources | `dashboard/data/resources.json` | Resource-allocation output |
| Dashboard calendar | `dashboard/data/calendar.json` | Preparedness-calendar output |

Actual output paths can differ if configured in the source code.

## Required field documentation

Before final submission, document every field in the encounter schema and every important Gold/dashboard schema using this table:

| Field | Data type | Meaning | Source or derivation | Validation / privacy |
|---|---|---|---|---|
| Use the exact field name from the schema | Exact Spark/JSON type | What the field represents | Source field or transformation | Rule, allowed values, or suppression behavior |

Include identifiers, event dates, disease/category fields, geographic fields, demographic fields, outcome/count fields, and any weather-related fields only when those fields actually exist in the schema.

## How to inspect Parquet schemas

Run this in Colab after mounting Google Drive and ensuring the paths exist:

```python
from pathlib import Path
from pyspark.sql import SparkSession

ROOT = Path(
    "/content/drive/MyDrive/University/8th Semester/BDA/episcope"
)

spark = (
    SparkSession.builder
    .appName("EpiScopeSchemaInspection")
    .getOrCreate()
)

for relative in ["data/bronze", "data/silver", "data/gold"]:
    path = ROOT / relative
    if not path.exists():
        print(f"Not found: {path}")
        continue

    print(f"\\n=== {relative} ===")
    try:
        df = spark.read.parquet(str(path))
        df.printSchema()
        print("Columns:", df.columns)
    except Exception as exc:
        print(f"Could not read as Parquet: {exc}")
```

Some directories may contain CSV files or nested output folders instead of Parquet directly. Inspect the configured paths in the pipeline scripts if the read fails.

For JSON, inspect representative records and types from each exported file. Do not expose sensitive records in documentation.

## Data provenance

The encounter dataset and outbreak labels used in the recorded experiment are synthetic. The weather-related fields must also be described as synthetic or derived unless their origin is independently established. Do not imply that synthetic observations are sourced from weather stations, hospitals, or government surveillance systems.

Record the generator configuration, scale factor, input row count, generation date, and relevant random seeds when available. Record transformations between Bronze, Silver, Gold, and public-serving outputs.
