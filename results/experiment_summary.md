# Experiment Results Summary

Generated from existing project artifacts and docs/EXPERIMENTS.md.

## Provenance

- `current_saved_output`: read directly from a saved evaluation JSON.
- `historical_documented`: transcribed from experiment documentation.
- Historical benchmark timings have not been independently verified from raw logs.
- No Spark pipeline or evaluation job was executed by the results-packaging cell.

## Files

- `pipeline_timings.csv`: documented stage timings.
- `data_quality_metrics.json`: documented row reconciliation.
- `detection_metrics.json`: current saved output and historical documented metrics, kept separate.
- `forecast_metrics.json`: current saved output and historical documented metrics, kept separate.
- `optimization_benchmarks.csv`: documented Gold-stage benchmark timings.
- `scaling_results.csv`: documented Gold-stage scaling measurements.

## Saved dashboard export snapshot

These values were read from the existing JSON files in `dashboard/data/`; no Spark job was run to produce this summary.

| Export | Saved value |
|---|---:|
| Weekly cases | 36,000 rows; all publishable; counts 32–3,667 |
| Sum of weekly published counts | 10,011,332 |
| Alerts | 17,063 rows |
| Forecasts | 8,960 rows |
| Resource allocations | 64 districts; 100 units total |
| Preparedness calendar | 3,840 rows |
| Total JSON payload | 9.81 MiB |

The cases and alerts files were modified later than forecasts, resources, and calendar. These outputs are therefore recorded as a **mixed saved snapshot**, not asserted to be a single synchronized pipeline export. Regenerate all five JSON files together and rerun the dashboard payload check before using the snapshot as final assignment evidence.

The latest case export is weekly, unlike the older daily privacy export recorded in `docs/EXPERIMENTS.md`. The current file contains no weekly published counts from 1 through 4; that check does not establish protection against inference from linked views or totals.

## Critical validation issues

1. Current detection evaluation reports TP=190, FP=25336, FN=169,
   and TN=554145. Sensitivity is approximately 52.92%, false-positive
   rate is 4.37%, and precision is approximately 0.74%.
   Historical documented metrics differ and remain unverified.
2. Current forecast evaluation reports MAE=2.0181919643 and
   RMSE=2.6985711686 across 8960 observations for 2025-12-04
   through 2025-12-31. Historical documentation reports MAE≈5.9894
   and RMSE≈11.6049; the discrepancy remains unresolved.
3. Current metrics refer to the latest saved evaluation outputs.
   Historical metrics are retained separately for provenance and
   must not be presented as verified current results.
4. Detection evaluation uses district-disease-day observations with
   at least 14 baseline days. Forecast evaluation uses a 7-day average
   to predict a fixed 28-day horizon. Interpret results within the
   synthetic dataset and the implemented evaluation procedures.
5. The scaling experiment covers only the Gold stage; smaller inputs
   were prefix/limit samples and may not preserve the full data distribution.
6. Historical benchmark results lack raw timing evidence in the audited paths.

## Interpretation

Current detection and forecast metrics refer to the saved evaluation outputs named in the corresponding JSON files. Historical values are retained separately because their original artifacts and run configuration are unavailable for independent reconciliation. The synthetic data, evaluation windows, and baseline assumptions constrain interpretation of every result.
