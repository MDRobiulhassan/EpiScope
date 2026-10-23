# EpiScope Architecture

## Overview

EpiScope separates data preparation, analytics, and dashboard serving into distinct stages. Apache Spark processes encounter data, Parquet stores intermediate analytical datasets, and D3.js v7 renders the exported JSON datasets in the dashboard.

## Logical Data Flow

```text
Synthetic encounter generator / input data
                    |
                    v
             Bronze ingestion
                    |
                    v
       Silver validation and cleaning
             /             \
       Clean records     Quarantine
             |
             v
             Gold
       Aggregated data
             |
       +-----+-------------------+
       |             |           |
       v             v           v
  Detection      Forecasting   Other
                               analytics
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

The diagram represents the overall processing stages. Individual analytics may consume different datasets, and their exact dependencies are determined by the implementation.

## Components

### Data Generation

`generator/generate_encounters.py` generates synthetic encounter records for pipeline testing and scalable experiments.

### Bronze Layer

`pipeline/bronze.py` ingests the generated encounter CSV and stores the initial dataset in Parquet format.

### Silver Layer

`pipeline/silver.py` validates encounter records, separates clean records from quarantined records, and produces data-quality outputs for downstream processing.

### Gold Layer

`pipeline/gold.py` creates aggregated analytical datasets from the cleaned encounter data.

### Analytics

- `analytics/detection/detect_outbreaks.py`: implements the outbreak-detection prototype.
- `analytics/detection/evaluate_detection.py`: evaluates outbreak-detection performance.
- `analytics/forecast/forecast_cases.py`: generates baseline case forecasts.
- `analytics/forecast/evaluate_forecasts.py`: evaluates forecast performance.
- `analytics/optimise/allocate_resources.py`: implements resource-allocation logic.
- `analytics/calendar/preparedness_calendar.py`: generates the preparedness calendar.

### Serving and Visualization

- `serving/build_public_data.py`: prepares public-facing data and applies small-count suppression.
- `serving/export_dashboard_data.py`: exports datasets for dashboard consumption.
- `dashboard/index.html`: defines the dashboard page.
- `dashboard/app.js`: implements D3.js visualizations and interactions.
- `dashboard/data/`: contains the exported JSON datasets used by the dashboard.

## Storage and Privacy

Intermediate analytical datasets are stored in Parquet format, while dashboard datasets are exported as JSON. Public-facing data is prepared separately from internal analytical outputs so that privacy controls can be applied before publication.

Small-count suppression is intended to prevent exact publication of low case counts. Its effectiveness depends on the implementation and the possibility of indirect disclosure; suppression of individual counts alone does not guarantee complete protection against re-identification.

## Execution Environment

The recorded experiments used Google Colab with Apache Spark running in local mode. Execution time and resource requirements depend on the available CPU, memory, storage, Spark configuration, and dataset size.

Implementation-specific paths, input schemas, output locations, and execution details are defined in the corresponding Python source files. See `docs/EXPERIMENTS.md` for performance measurements and `docs/LIMITATIONS.md` for known limitations.
