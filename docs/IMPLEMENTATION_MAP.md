# Implementation Map

This map connects the assignment areas to the project code and the saved evidence in this repository.

| Area | Main implementation | Saved evidence |
|---|---|---|
| Synthetic encounter generation and ingestion | `generator/`, `pipeline/bronze.py` | 25,000,000-row documented run; source data is synthetic. |
| Validation, cleaning, and quarantine | `pipeline/silver.py` | `results/data_quality_metrics.json` records 24,825,210 clean rows and 174,790 quarantined rows from documented results. |
| Gold aggregation | `pipeline/gold.py` | Aggregated outputs feed the analytics modules. |
| Incremental inventory | `generator/generate_inventory_drop.py`, `pipeline/inventory.py` | Synthetic facility snapshots use `(snapshot_date, facility_id)` keys and replay protection. |
| Outbreak detection | `analytics/detection/` | `results/detection_metrics.json` contains current saved metrics and a separate historical record. |
| Forecasting | `analytics/forecast/` | `results/forecast_metrics.json` contains the saved 28-day evaluation and historical metrics. |
| Allocation and preparedness | `analytics/optimise/`, `analytics/calendar/` | Saved dashboard exports include district allocations and calendar rows. The optimizer does not use inventory-feed totals. |
| Public-data serving and dashboard | `serving/`, `dashboard/` | Five JSON exports are stored in `dashboard/data/`; their saved modification times differ. |
| Scaling and Spark experiments | `scripts/EpiScope_Colab_Run.ipynb`, `docs/EXPERIMENTS.md` | `results/pipeline_timings.csv`, `results/scaling_results.csv`, and `results/optimization_benchmarks.csv` record documented measurements. |
| Report and policy brief | `docs/episcope_ieee_report.tex`, `docs/policy_brief.tex` | PDFs are in `docs/episcope_ieee_report.pdf` and `docs/policy_brief.pdf`. |
| Presentation | `docs/presentation.html`, `docs/presentation.pptx`, `docs/presentation_script.md` | Nine-slide presentation with speaking sections for all four named members. |

## Saved evaluation values

The current detection evaluation reports 190 true positives, 25,336 false positives, 169 false negatives, and 554,145 true negatives. Sensitivity is 52.92%, false-positive rate is 4.37%, and precision is 0.74%.

The current forecast evaluation contains 8,960 observations for December 4–31, 2025. MAE is 2.0182 cases and RMSE is 2.6986 cases. The evaluated model repeats a seven-day average across a fixed 28-day horizon.

The current dashboard files contain 36,000 weekly case rows, 17,063 alert rows, 8,960 forecasts, 64 allocations, and 3,840 preparedness-calendar rows. Their combined saved payload is 9.81 MiB. Because modification times differ, these exports are described as a saved mixed snapshot rather than a single synchronized run.

All encounter, inventory, and injected outbreak-label data are synthetic. The saved metrics and historical experiment measurements describe the project artifacts and procedures documented here; they do not establish real-world health performance.
