**Demo video:** Pending an accessible share link. Add the link after recording and verify it opens without sign-in.

**Google Colab runner:** [scripts/EpiScope_Colab_Run.ipynb](scripts/EpiScope_Colab_Run.ipynb)

# EpiScope: Public Health Surveillance and Preparedness Dashboard

EpiScope is a Big Data Analytics research prototype developed for **CSE 4345, Department of Computer Science and Engineering, Premier University, Chittagong, Spring 2026**. It demonstrates a large-scale data-processing workflow for disease surveillance, outbreak detection, case forecasting, resource planning, and public-facing visualization using Apache Spark, PySpark, Parquet, Python, and D3.js v7.

**Repository:** [mdrobiulhassan/EpiScore](https://github.com/mdrobiulhassan/EpiScore)

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

The diagram summarizes the overall workflow. Individual scripts may have additional input dependencies; consult their implementations for exact execution order.

## Repository Structure

| Path | Purpose |
|---|---|
| `generator/` | Synthetic encounter generation |
| `generator/generate_inventory_drop.py` | One-day synthetic facility stock and bed-occupancy input |
| `pipeline/bronze.py` | Bronze-layer ingestion |
| `pipeline/silver.py` | Validation, cleaning, and quarantine |
| `pipeline/gold.py` | Gold-layer aggregation |
| `pipeline/inventory.py` | Idempotent Bronze–Silver–Gold processing for incremental inventory snapshots |
| `analytics/detection/` | Outbreak detection and evaluation |
| `analytics/forecast/` | Forecast generation and evaluation |
| `analytics/optimise/` | Resource allocation |
| `analytics/calendar/` | Preparedness-calendar generation |
| `serving/` | Public-data preparation and dashboard export |
| `dashboard/` | D3.js dashboard and exported JSON datasets |
| `scripts/` | Spark diagnostics and utilities |
| `tests/` | Automated tests |
| `docs/` | Architecture, data, experiment, and limitation documentation |
| `requirements.txt` | Python dependency pins |
| `AI_USAGE.md` | AI assistance disclosure |
| `scripts/EpiScope_Colab_Run.ipynb` | Google Colab execution cells |
| `docs/REQUIREMENT_TRACEABILITY.md` | Assignment ID mapping and handover checklist |
| `docs/TEAM_ROLES_AND_CONTRIBUTION_DRAFT.md` | Balanced speaking plan and proposed team responsibilities |
| `docs/CONTRIBUTION_MATRIX_DRAFT.md` | Unsigned contribution matrix draft for team review |
| `docs/presentation.html` | Browser-based presentation slides |
| `docs/presentation_script.md` | Three-member speaking script |

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

The recorded pipeline and evaluation stages took approximately **27.40 minutes**, excluding encounter generation, which took approximately **7.17 minutes**.

The measurements were collected in a constrained research environment using Spark local mode. Runtime will vary with hardware, memory, storage, Spark configuration, and workload. Refer to [`docs/EXPERIMENTS.md`](docs/EXPERIMENTS.md) for the individual stage timings, optimization experiments, and evaluation caveats.

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

The evaluation unit was district–disease–day, with at least 14 baseline days required.

The low precision indicates that many generated alerts were false positives relative to the synthetic evaluation labels. These results should be interpreted as prototype performance, not evidence of operational readiness.

## Forecast Evaluation

The latest recorded forecast evaluation reported:

| Metric | Result |
|---|---:|
| Evaluation observations | 8,960 |
| Mean absolute error (MAE) | 2.0182 |
| Root mean squared error (RMSE) | 2.6986 |
| Test period | December 4–31, 2025 |
| Forecast model | Seven-day-average fixed 28-day horizon |

These metrics describe the recorded evaluation only. They do not establish superiority over a seasonal-naïve baseline or validate performance on real-world outbreaks.

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

The earlier dependency specification listed `pytest==8.3.5`, while this test run used pytest 8.4.2. The final environment should be checked against `requirements.txt` before release.

## Run the Dashboard Locally

From the repository root, run:

```bash
python -m http.server 8000 --directory dashboard
```

Then open [http://localhost:8000](http://localhost:8000).

This serves the existing dashboard and JSON files. It does not regenerate encounter data, rerun analytics, or refresh the exported datasets.

The hosted dashboard is available at:

[https://mdrobiulhassan.github.io/EpiScore/dashboard/](https://mdrobiulhassan.github.io/EpiScore/dashboard/)

GitHub Pages serves the published static files. New pipeline outputs must be exported and published before they appear in the hosted dashboard.

## Pipeline Execution

The project contains separate scripts for data generation, processing, analytics, and serving. Run them according to their actual dependencies and configured input/output paths.

For Google Colab, use [`scripts/EpiScope_Colab_Run.ipynb`](scripts/EpiScope_Colab_Run.ipynb). It contains the batch workflow and a separate incremental inventory-feed demonstration. `scripts/run_pipeline.py` is the batch encounter workflow; it does not process the incremental inventory feed. Run the notebook's incremental section after the batch run, then replay the same inventory snapshot to show that no duplicate facility/date keys are appended.

The inventory feed is synthetic and currently demonstrates ingestion, validation, quarantine, and district-level Gold aggregation. It is not yet an input to the resource-allocation optimizer, and corrected values for an already ingested snapshot key are not merged.

## Documentation

- [Project proposal](docs/proposal.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Data dictionary](docs/DATA_DICTIONARY.md)
- [Data quality and privacy](docs/DATA_QUALITY_AND_PRIVACY.md)
- [Experiments and evaluation](docs/EXPERIMENTS.md)
- [Limitations](docs/LIMITATIONS.md)
- [Policy brief draft](docs/policy_brief.md) · [LaTeX appendix used by the report](docs/policy_brief.tex)
- [AI usage disclosure](AI_USAGE.md)
- [Presentation slides](docs/presentation.html) · [speaking script](docs/presentation_script.md)

## Requirement Traceability

The initial requirement mapping is maintained in the project report and should be checked against the official course rubric and final implementation.

| Requirement group | Main implementation area |
|---|---|
| ING | `generator/`, `pipeline/` |
| DQ | `pipeline/silver.py` and data-quality outputs |
| AN-1 to AN-3 | `analytics/detection/` |
| AN-4 to AN-5 | `analytics/forecast/` |
| AN-6 to AN-8 | `analytics/optimise/` |
| AN-9 | `analytics/calendar/` |
| VIS | `serving/`, `dashboard/` |
| ENG | Execution, reproducibility, and benchmark evidence |

The exact mapping of individual requirement IDs to source files and report sections must follow the official rubric. A directory mapping alone does not prove that a requirement has been satisfied.

## Data Privacy and Research Limitations

- Encounter records and injected outbreak labels are synthetic.
- Public case counts from one through four are suppressed by the documented public-data preparation logic.
- Small-count suppression reduces direct disclosure risk but does not, by itself, prove that indirect disclosure is impossible.
- Detection and forecast metrics depend on the synthetic data, evaluation definitions, and tested time period.
- Resource-allocation and preparedness outputs are analytical demonstrations, not validated operational recommendations.
- Performance measurements reflect the recorded environment and should not be generalized without additional experiments.

## Release Information

The final submission should include the repository URL, IEEE report PDF, and accessible demonstration video. The repository release should use the required `v1.0` tag after the final code and documentation have been checked.

