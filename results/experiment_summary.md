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

## Recommended next validation

- Preserve the latest detection and forecast evaluation outputs and their
  exact source paths in the corresponding metrics JSON files.
- Investigate the historical metric discrepancies only if the original
  evaluation artifacts or run configuration become available.
- Verify that docs/EXPERIMENTS.md and the IEEE report use the current
  metrics consistently and identify historical values as unverified.
- Clearly document dataset limitations, evaluation windows, and baseline
  model assumptions in the final report.
