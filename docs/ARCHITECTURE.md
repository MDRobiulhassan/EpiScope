# EpiScope Architecture

## Overview

EpiScope separates data preparation, analytics, and dashboard serving into distinct stages. Apache Spark handles large-scale transformations, Parquet stores processed data, and D3.js v7 renders the exported dashboard datasets.

## Logical data flow

```text
Synthetic encounter generator / input data
                    |
                    v
              Bronze layer
                    |
                    v
       Silver validation and cleaning
             /             \
       Clean records     Quarantine
             |
             v
             Gold
             |
       +-----+-------------------+
       |             |           |
       v             v           v
  Detection      Forecasts    Aggregates
       |             |           |
       +-------------+-----------+
                     |
          Resource allocation
          Preparedness calendar
                     |
                     v
         Public-data preparation
         and small-count suppression
                     |
                     v
            Dashboard JSON export
                     |
                     v
             D3.js v7 dashboard
```

This diagram describes the intended logical flow. Verify exact dependencies and output paths against the current scripts before changing the implementation.

## Components

### Data generation
`generator/generate_encounters.py` produces synthetic encounter records for scalable experiments.

### Bronze
`pipeline/bronze.py` ingests the source data into the initial processing layer.

### Silver
`pipeline/silver.py` validates records, separates clean and quarantined records, and prepares data for downstream processing.

### Gold
`pipeline/gold.py` creates aggregated data for analytics and serving.

### Analytics
- `analytics/detection/detect_outbreaks.py`: outbreak-detection prototype.
- `analytics/detection/evaluate_detection.py`: detection evaluation.
- `analytics/forecast/forecast_cases.py`: baseline forecasting.
- `analytics/forecast/evaluate_forecasts.py`: forecast evaluation.
- `analytics/optimise/allocate_resources.py`: resource-allocation logic.
- `analytics/calendar/preparedness_calendar.py`: preparedness calendar generation.

### Serving and visualization
- `serving/build_public_data.py`: prepares public-facing data.
- `serving/export_dashboard_data.py`: exports dashboard datasets.
- `dashboard/index.html`: dashboard page.
- `dashboard/app.js`: D3 visualization and interaction logic.
- `dashboard/data/`: exported JSON datasets.

## Storage and privacy

Processed analytical data is stored in Parquet. Dashboard datasets are JSON. Public-facing outputs must be treated separately from internal analytical outputs so privacy controls can be applied before data is exposed.

The recorded public-data check verified that published case counts from 1 through 4 were not exposed as exact counts in the tested `cases.json`. This check should be repeated after every export change.

## Execution environment

The recorded experiments used a Google Colab environment with Spark running in local mode. Exact runtime depends on available CPU, memory, storage, Spark configuration, and data layout.

For implementation-specific paths, arguments, and schemas, consult the Python source files. This document intentionally avoids assuming that all scripts accept the same command-line arguments.
