# Requirement Traceability

This document maps the assignment areas to the EpiScope implementation and the evidence currently stored in the repository.

| Assignment area | Implementation | Repository evidence and scope |
|---|---|---|
| Batch synthetic encounters | `generator/generate_encounters.py` | The Colab notebook documents the 25-million-row batch run. The generated full dataset is not stored in this repository. |
| Bronze-Silver-Gold encounter processing | `pipeline/bronze.py`, `pipeline/silver.py`, `pipeline/gold.py` | Layered Spark processing. Saved data-quality counts record the documented 25-million-row reconciliation. |
| Incremental source feed | `generator/generate_inventory_drop.py`, `pipeline/inventory.py` | Synthetic daily facility stock and occupancy snapshot. Bronze ingestion is keyed by `(snapshot_date, facility_id)` and supports replay protection. |
| Encounter data quality | `pipeline/silver.py` | The implementation contains named validation checks and separates clean records from quarantine. `results/data_quality_metrics.json` contains documented row counts; it does not recount a source dataset. |
| Inventory data quality | `pipeline/inventory.py` | Validates snapshot date, facility and district values, nonnegative stock and bed fields, positive capacity, and occupancy not exceeding capacity. |
| Privacy controls | `pipeline/silver.py`, `serving/build_public_data.py` | Clean Silver output hashes patient identifiers; public case data applies small-count suppression. These controls do not establish a formal privacy guarantee. |
| Outbreak detection and evaluation | `analytics/detection/` | `results/detection_metrics.json` contains current saved evaluation metrics and a separate historical record. Current precision is low (0.74%), so alerts require human review. |
| Forecasting and evaluation | `analytics/forecast/` | `results/forecast_metrics.json` contains the current saved 28-day forecast evaluation and historical metrics. The evaluated baseline repeats a seven-day average. |
| Allocation and preparedness | `analytics/optimise/`, `analytics/calendar/` | Produces illustrative resource and calendar outputs. The optimizer uses forecast demand and does not consume the incremental inventory feed. |
| Dashboard and serving | `serving/`, `dashboard/` | Five saved JSON exports are in `dashboard/data/`. Their modification times differ; the saved values are a mixed snapshot rather than one synchronized export run. |
| Scalability and Spark experiments | `scripts/EpiScope_Colab_Run.ipynb`, `docs/technical/EXPERIMENTS.md` | Historical timing, scaling, and optimization measurements are stored under `results/`. They describe the documented environment and procedures. |
| Technical report | `docs/report/EpiScope_Report.tex` | `docs/report/EpiScope_Report.pdf`. The technical report and policy brief are separate documents. |
| Policy brief | `docs/report/policy_brief.tex` | Standalone PDF: `docs/report/policy_brief.pdf`. |
| Presentation | `docs/report/EpiScope_Presentation_Slide.pptx` | PowerPoint slide deck for the four-member project team. |

## Saved evaluation results

The saved detection evaluation reports 190 true positives, 25,336 false positives, 169 false negatives, and 554,145 true negatives. Sensitivity is 52.92%, false-positive rate is 4.37%, and precision is 0.74%.

The saved forecast evaluation contains 8,960 observations from December 4 through 31, 2025. Mean absolute error is 2.0182 cases and root mean squared error is 2.6986 cases. These results are limited to the synthetic data and implemented evaluation procedure. Historical documented values are retained separately because they have not been reconciled against the current saved output.

Encounter records, inventory records, and injected outbreak labels are synthetic. The system is a research prototype; saved evaluation results do not establish real-world public-health performance.
