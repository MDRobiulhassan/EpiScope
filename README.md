
# EpiScope: Public Health Surveillance and Preparedness Dashboard

EpiScope is a Big Data Analytics research prototype developed for **CSE 4345, Department of Computer Science and Engineering, Premier University, Chattogram, Spring 2026**. It demonstrates a large-scale data-processing workflow for disease surveillance, outbreak detection, case forecasting, resource planning, and public-facing visualization using Apache Spark, PySpark, Parquet, Python, and D3.js v7.

**Repository:** [mdrobiulhassan/EpiScope](https://github.com/mdrobiulhassan/EpiScope)

**Google Colab runner:** [scripts/EpiScope_Colab_Run.ipynb](scripts/EpiScope_Colab_Run.ipynb)

## Project Documents

- [Documentation index](docs/README.md)
- [Report - PDF](docs/report/EpiScope_Report.pdf)
- [Policy brief - PDF](docs/report/policy_brief.pdf)
- [Presentation slides](docs/report/EpiScope_Presentation_Slide.pptx)

The technical report and policy brief are separate documents. The policy brief is provided as a standalone PDF.

## Project Team

- Md. Samin Osman - 0222220005101042
- Robiul Hassan - 0222220005101043
- Walid Talal - 0222220005101045
- Md. Mahafujul Alam - 0222220005101066

**Important limitation:** Encounter records and injected outbreak labels are synthetic. The analytical results are experimental and do not establish effectiveness in real-world public-health surveillance. Weather-related fields must not be described as real weather-station observations unless independently verified.

## Project Features

- Generate synthetic encounter records for large-scale processing.
- Generate and ingest a one-day synthetic facility inventory/bed-occupancy snapshot with replay protection.
- Process encounter data through Bronze, Silver, and Gold layers.
- Validate and clean records and quarantine invalid data.
- Aggregate surveillance indicators for downstream analytics.
- Generate and evaluate outbreak-detection signals against synthetic ground truth.
- Generate and evaluate short-term case forecasts.
- Produce resource-allocation and preparedness-calendar outputs.
- Apply small-count suppression to public-facing case data.
- Export JSON datasets for an interactive D3.js dashboard.
- Measure pipeline runtime and evaluate Spark configuration performance.

## Architecture and Data Flow

```text
Synthetic Encounter Generation
             |
             v
      Bronze Ingestion
             |
             v
   Silver Validation and Cleaning
        |             |
        v             v
   Clean Records   Quarantine
        |
        v
    Gold Aggregation
        |
        +-------------------------+
        |            |            |
        v            v            v
    Detection    Forecasting   Other Analytics
        |            |            |
        +------------+------------+
                     |
                     v
          Resource and Calendar Outputs
                     |
                     v
       Public Data and Small-Count Suppression
                     |
                     v
             Dashboard JSON Export
                     |
                     v
             D3.js v7 Dashboard
```

The daily facility inventory feed follows a separate Bronze-Silver-Gold path. Its Gold aggregates do not feed the resource-allocation optimizer.

The diagram summarizes the overall workflow. Individual scripts may have additional input dependencies; consult their implementations for exact execution order.

## Repository Structure

| Path | Purpose |
|---|---|
| `generator/` | Synthetic encounter generation |
| `generator/generate_inventory_drop.py` | One-day synthetic facility stock and bed-occupancy input |
| `pipeline/bronze.py` | Bronze-layer ingestion |
| `pipeline/silver.py` | Validation, cleaning, and quarantine |
| `pipeline/gold.py` | Gold-layer aggregation |
| `pipeline/inventory.py` | Idempotent Bronze-Silver-Gold processing for incremental inventory snapshots |
| `analytics/detection/` | Outbreak detection and evaluation |
| `analytics/forecast/` | Forecast generation and evaluation |
| `analytics/optimise/` | Resource allocation |
| `analytics/calendar/` | Preparedness-calendar generation |
| `serving/` | Public-data preparation and dashboard export |
| `dashboard/` | D3.js dashboard and exported JSON datasets |
| `scripts/` | Spark diagnostics and utilities |
| `tests/` | Automated tests |
| `docs/` | Technical documentation, report, policy brief, and presentation deck |
| `requirements.txt` | Python dependency pins |
| `AI_USAGE.md` | AI assistance disclosure |
| `scripts/EpiScope_Colab_Run.ipynb` | Google Colab execution cells |
| `docs/technical/IMPLEMENTATION_MAP.md` | Assignment areas, implementation paths, and saved evidence |
| `docs/technical/REQUIREMENT_TRACEABILITY.md` | Assignment requirements mapped to implementation and repository evidence |
| `docs/report/EpiScope_Report.tex` | Technical report source |
| `docs/report/policy_brief.tex` | Standalone policy brief source |
| `docs/report/EpiScope_Presentation_Slide.pptx` | Four-member presentation slide deck |

## Technology Stack

- **Python and PySpark:** Data generation, processing, analytics, and evaluation.
- **Apache Spark:** Distributed data-processing framework used in local-mode experiments.
- **Parquet:** Columnar storage for processed datasets.
- **D3.js v7:** Interactive dashboard visualizations.
- **GitHub Pages:** Hosting for the static dashboard.
- **pytest:** Automated testing.

## Recorded Full-Scale Experiment

The recorded experiment processed **25,000,000 input rows**. The Silver-layer results reconciled as follows:

| Metric | Recorded result |
|---|---:|
| Input rows | 25,000,000 |
| Clean rows | 24,825,210 |
| Quarantined rows | 174,790 |
| Quarantine rate | 0.69916% |

The recorded pipeline and evaluation stages took approximately **27.90 minutes**, excluding encounter generation, which took approximately **7.17 minutes**.

The measurements were collected in a constrained research environment using Spark local mode. Runtime will vary with hardware, memory, storage, Spark configuration, and workload. Refer to [`docs/technical/EXPERIMENTS.md`](docs/technical/EXPERIMENTS.md) for the individual stage timings, optimization experiments, and evaluation caveats.

## Detection Evaluation

The latest recorded detection evaluation reported:

| Metric | Result |
|---|---:|
| True positives | 190 |
| False positives | 25,336 |
| False negatives | 169 |
| True negatives | 554,145 |
| Sensitivity | 52.92% |
| False-positive rate | 4.37% |
| Precision | 0.74% |

The evaluation unit was district-disease-day, with at least 14 baseline days required.

The low precision indicates that many generated alerts were false positives relative to the synthetic evaluation labels. These results should be interpreted as prototype performance, not evidence of operational readiness.

## Forecast Evaluation

The latest recorded forecast evaluation reported:

| Metric | Result |
|---|---:|
| Evaluation observations | 8,960 |
| Mean absolute error (MAE) | 2.0182 |
| Root mean squared error (RMSE) | 2.6986 |
| Test period | December 4-31, 2025 |
| Forecast model | Seven-day-average fixed 28-day horizon |

These metrics describe the recorded evaluation only. They do not establish superiority over a seasonal-naive baseline or validate performance on real-world outbreaks.

## Saved Dashboard Export Snapshot

The repository currently contains these dashboard JSON files:

| Export | Rows / value |
|---|---:|
| Weekly case records | 36,000 (all published; range 32-3,667) |
| Sum of published weekly counts | 10,011,332 |
| Outbreak-alert records | 17,063 |
| Forecast records | 8,960 |
| District allocations | 64; 100 units total |
| Preparedness-calendar rows | 3,840 |
| Combined JSON payload | 9.81 MiB |

These figures summarize the saved JSON files, not a new pipeline run. The cases and alerts files have later modification times than the forecast, resource, and calendar files, so this is a **mixed saved snapshot**, not a synchronized export run. The case counts are weekly aggregates, and suppression is applied to weekly totals; no weekly counts from 1 to 4 appear in this snapshot.

## Automated Tests

The recorded test run for `tests/test_validation.py` completed successfully:

```text
Platform: Linux
Python: 3.13.16
pytest: 8.4.2

tests/test_validation.py
2 passed
```

This confirms that the two tests in that file passed in the reported environment. It does not establish that every test, pipeline stage, or end-to-end execution path has been verified.

The recorded environment used pytest 8.4.2, while `requirements.txt` specifies pytest 8.3.5.

## Run the Dashboard Locally

From the repository root, run:

```bash
python -m http.server 8000 --directory dashboard
```

Then open [http://localhost:8000](http://localhost:8000).

This serves the existing dashboard and JSON files. It does not regenerate encounter data, rerun analytics, or refresh the exported datasets.

The hosted dashboard is available at:

[https://mdrobiulhassan.github.io/EpiScope/dashboard/](https://mdrobiulhassan.github.io/EpiScope/dashboard/)

GitHub Pages serves the published static files. New pipeline outputs must be exported and published before they appear in the hosted dashboard.

## Pipeline Execution

The project contains separate scripts for data generation, processing, analytics, and serving. Run them according to their actual dependencies and configured input/output paths.

For Google Colab, use [`scripts/EpiScope_Colab_Run.ipynb`](scripts/EpiScope_Colab_Run.ipynb). It contains the batch workflow and a separate incremental inventory-feed demonstration. `scripts/run_pipeline.py` is the batch encounter workflow; it does not process the incremental inventory feed. Run the notebook's incremental section after the batch run, then replay the same inventory snapshot to show that no duplicate facility/date keys are appended.

The inventory feed is synthetic and demonstrates ingestion, validation, quarantine, and district-level Gold aggregation. The optimizer does not consume this feed. Existing snapshot keys use first-write-wins behavior, so corrected values are not merged.

## Documentation

- [Project proposal](docs/technical/proposal.md)
- [Architecture](docs/technical/ARCHITECTURE.md)
- [Data dictionary](docs/technical/DATA_DICTIONARY.md)
- [Data quality and privacy](docs/technical/DATA_QUALITY_AND_PRIVACY.md)
- [Experiments and evaluation](docs/technical/EXPERIMENTS.md)
- [Limitations](docs/technical/LIMITATIONS.md)
- [AI usage disclosure](AI_USAGE.md)

## Implementation Map

The [implementation map](docs/technical/IMPLEMENTATION_MAP.md) gives a concise project overview; [requirement traceability](docs/technical/REQUIREMENT_TRACEABILITY.md) maps assignment areas to implementation and saved evidence.

## Data Privacy and Research Limitations

- Encounter records and injected outbreak labels are synthetic.
- Public case counts from one through four are suppressed by the documented public-data preparation logic.
- Small-count suppression reduces direct disclosure risk but does not, by itself, prove that indirect disclosure is impossible.
- Detection and forecast metrics depend on the synthetic data, evaluation definitions, and tested time period.
- Resource-allocation and preparedness outputs are analytical demonstrations, not validated operational recommendations.
- Performance measurements reflect the recorded environment and should not be generalized without additional experiments.
