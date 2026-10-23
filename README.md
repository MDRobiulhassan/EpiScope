<!-- VIDEO_LINK: Replace with the final accessible video URL -->
**Demo video:** [https:youtube.com](https://www.youtube.com/)

# EpiScope

EpiScope is a Big Data Analytics project for exploring disease-surveillance workflows using Apache Spark, Parquet, and a D3.js v7 dashboard.

## Project capabilities

- Generate synthetic encounter data at large scale.
- Process data through Bronze, Silver, and Gold layers.
- Validate records and quarantine invalid data.
- Aggregate disease and geographic indicators.
- Prototype outbreak detection and short-term case forecasting.
- Produce resource-allocation recommendations and a preparedness calendar.
- Export public-facing dashboard data with small-count suppression.
- Evaluate analytical outputs and benchmark Spark execution.

**Important:** Encounter data and outbreak labels are synthetic. Weather-related fields must not be described as real observations unless independently verified. The analytical outputs are prototypes, not validated public-health predictions.

## Repository structure

| Path | Purpose |
|---|---|
| `generator/` | Synthetic encounter generation |
| `pipeline/bronze.py` | Bronze ingestion |
| `pipeline/silver.py` | Data validation, cleaning, and quarantine |
| `pipeline/gold.py` | Aggregated analytical data |
| `analytics/detection/` | Outbreak detection and evaluation |
| `analytics/forecast/` | Forecast generation and evaluation |
| `analytics/optimise/` | Resource allocation |
| `analytics/calendar/` | Preparedness calendar |
| `serving/` | Public-data preparation and dashboard export |
| `dashboard/` | D3.js v7 dashboard and JSON data |
| `scripts/` | Spark diagnostics |
| `tests/` | Automated tests for pipeline and analytics |
| `docs/` | Technical documentation |
| `AI_USAGE.md` | AI assistance disclosure |

## Processing workflow

1. Generate or provide the input encounter dataset.
2. Run Bronze ingestion.
3. Run Silver validation and cleaning.
4. Run Gold aggregation.
5. Run outbreak detection and its evaluation.
6. Run forecast generation and its evaluation.
7. Run resource allocation and preparedness-calendar generation.
8. Build privacy-filtered public data.
9. Export dashboard JSON files.
10. Open the dashboard using a local HTTP server or the configured hosting environment.

Check each script's arguments and path configuration before running it. Do not assume that running a script from a different working directory will resolve relative paths correctly. Run the pipeline stages in dependency order.

## Dashboard

The dashboard is in `dashboard/`, with `index.html`, `app.js`, and JSON files under `dashboard/data/`.

The expected exported datasets are:
- `cases.json`
- `alerts.json`
- `forecasts.json`
- `resources.json`
- `calendar.json`

Serve the directory over HTTP when required by the browser. Verify that all JSON requests succeed and that all dashboard views render after regenerating data.

## Reproducibility and performance

The recorded 25-million-input experiment completed the measured pipeline and evaluation stages in approximately 27.4 minutes, excluding encounter generation. See `docs/EXPERIMENTS.md` for stage timings and benchmark caveats.

The recorded Silver validation result was:
- Input rows: 25,000,000
- Clean rows: 24,825,210
- Quarantined rows: 174,790
- Quarantine rate: approximately 0.699%

These figures describe the recorded experiment, not a guarantee for every machine or execution.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Data dictionary](docs/DATA_DICTIONARY.md)
- [Data quality and privacy](docs/DATA_QUALITY_AND_PRIVACY.md)
- [Experiments and evaluation](docs/EXPERIMENTS.md)
- [Limitations](docs/LIMITATIONS.md)
- [AI usage disclosure](AI_USAGE.md)

## Prerequisites

- Python version: verify against the pinned dependencies before release.
- Java version: verify compatibility with the installed PySpark version.
- Git.
- A machine with sufficient memory and disk space for the selected dataset scale.

## Local run

The clean-clone, one-command pipeline runner is not yet verified.
Do not treat the following as the final ENG-1 command until it has
been implemented and tested:

```bash
python scripts/run_pipeline.py
```

## Run the dashboard locally

From the repository root, run:

```bash
python -m http.server 8000 --directory dashboard
```

Then open http://localhost:8000 in a browser. This serves the dashboard
and its existing JSON files; it does not regenerate the data.

## Hidden test drop

1. Place instructor-provided test inputs in the location specified by
   the instructor, without committing private test data.
2. Use the documented pipeline runner with the instructor's input path.
3. Check the generated quality report, quarantine output, analytics,
   and dashboard exports.
4. Record the command and results. Replace these generic steps with
   the instructor's exact hidden-test interface when it is provided.

## Requirement traceability

| Requirement ID | Implementation location | Report section |
|---|---|---|
| ING-1 to ING-3 | `generator/`, `pipeline/bronze.py`, `pipeline/silver.py`, `pipeline/gold.py` | Data and architecture |
| DQ-1 to DQ-3 | `pipeline/silver.py`, `data/silver/quality_report/` | Data quality |
| AN-1 to AN-3 | `analytics/detection/` | Outbreak detection and evaluation |
| AN-4 to AN-5 | `analytics/forecast/` | Forecasting and evaluation |
| AN-6 to AN-8 | `analytics/optimise/` | Resource allocation |
| AN-9 | `analytics/calendar/` | Preparedness calendar |
| VIS-1 to VIS-4 | `dashboard/`, `serving/export_dashboard_data.py` | Dashboard |
| ENG-1 | `scripts/run_pipeline.py` — verify or implement | Reproducibility |
| ENG-2 to ENG-3 | `docs/EXPERIMENTS.md` and benchmark evidence | Performance evaluation |

This is an initial mapping. Verify each ID against the official rubric
and the final report before submission.
