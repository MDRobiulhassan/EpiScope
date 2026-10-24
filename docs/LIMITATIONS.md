# EpiScope Limitations

## 1. Synthetic Data and External Validity

EpiScope is an educational big-data analytics prototype evaluated primarily using synthetic disease-surveillance encounter data. Its results demonstrate pipeline execution and analytical behavior on the generated dataset; they do not establish performance on real clinical or public-health surveillance data.

Synthetic data may not reproduce real disease prevalence, reporting delays, seasonality, demographic differences, missingness, geographic variation, or operational data-quality problems. Detection and forecasting results must therefore not be interpreted as evidence of clinical validity or operational readiness.

Weather-related and other contextual fields should not be interpreted as verified real-world observations unless their provenance has been independently established.

## 2. Outbreak Detection Performance

The latest saved detection evaluation reports:

| Metric | Latest saved result |
|---|---:|
| True positives (TP) | 190 |
| False positives (FP) | 25,336 |
| False negatives (FN) | 169 |
| True negatives (TN) | 554,145 |
| Sensitivity (recall) | 52.92% |
| False-positive rate (FPR) | 4.37% |
| Precision | 0.74% |

The evaluation unit is district-disease-day, with at least 14 baseline days required. The saved output is:

`data/gold/detection_evaluation/part-00000-d8fdf23b-e479-43f4-8978-0cdc8bfaf662-c000.json`

The results indicate a substantial false-positive burden. Precision of 0.74% means fewer than one in 100 predicted positives are true positives in this evaluation. Sensitivity of 52.92% also indicates that some positive observations are missed. The detector should therefore be treated as an experimental screening component, not a reliable real-world alerting system.

Performance may change with baseline definitions, thresholds, disease frequency, synthetic data-generation assumptions, and the evaluation unit.

Previously documented metrics (TP = 184, FP = 21,186, FN = 175, TN = 558,295; sensitivity = 51.25%, FPR = 3.66%, precision = 0.86%) remain historical and unverified. They have not been reconciled with the latest saved evaluation and should not be treated as interchangeable results.

## 3. Forecasting Limitations

The latest saved forecast evaluation reports:

| Metric | Latest saved result |
|---|---:|
| Evaluation observations | 8,960 |
| Mean absolute error (MAE) | 2.0182 |
| Root mean squared error (RMSE) | 2.6986 |
| Test period | 2025-12-04 to 2025-12-31 |
| Forecast method | 7-day average, fixed 28-day horizon |

The saved output is:

`data/gold/forecast_evaluation/overall/part-00000-278a3b6c-3c49-4ff5-b57b-7e60da834a78-c000.json`

The method computes a seven-day average before the test window and repeats it across a fixed 28-day horizon. It is a simple baseline rather than a model that explicitly learns changing trends, seasonality, weather effects, or other external drivers. Accuracy may deteriorate when patterns change or when the method is applied outside the evaluated period and synthetic dataset.

MAE and RMSE are expressed in the scale of the evaluated target. They should not be interpreted as relative errors or compared across datasets with different scales without additional analysis.

Previously documented forecast results (MAE approximately 5.9894 and RMSE approximately 11.6049) remain historical and unverified. Their discrepancy with the latest saved evaluation has not been resolved.

## 4. Data Quality and Quarantine

Historical documentation records 25,000,000 input rows, 24,825,210 clean rows, and 174,790 quarantined rows, corresponding to a quarantine rate of approximately 0.69916%. The clean and quarantined counts reconcile exactly to the documented input total.

These are recorded measurements and have not necessarily been recomputed during the latest documentation update. Their validity depends on the pipeline version, input dataset, and execution that produced them.

The complete set of Silver-layer quality rules must be verified against the implementation. A documented rule inventory alone does not establish that each rule is implemented, tested, or triggered correctly.

The incremental inventory feed is synthetic and runs as a parallel Bronze–Silver–Gold path. The current resource optimizer does not consume its Gold outputs. Replay protection is first-write-wins for `(snapshot_date, facility_id)`; corrected values for an existing key are ignored rather than merged. The new Colab demonstration must be run and its output recorded before claiming execution evidence.

## 5. Privacy and Small-Count Suppression

The public-data preparation process is intended to suppress exact published counts from 1 through 4. A previous check of `cases.json` found no exact `published_case_count` values in this range, but this limited result does not establish that every public output is safe.

Suppression must be evaluated across all published files and relevant derived fields, including boundary values of 1, 2, 3, 4, and 5. Counts may potentially be inferred from totals, differences, repeated releases, or related geographic and temporal dimensions.

Small-count suppression alone is not a formal privacy guarantee. EpiScope has not established differential privacy, resistance to linkage attacks, or comprehensive protection against re-identification. The prototype should not be described as formally privacy-preserving without additional analysis.

## 6. Performance and Scalability

Recorded experiments report approximately 27.40 minutes for the measured pipeline stages, including detection and forecast evaluation, on a 25-million-row input. Synthetic-data generation, recorded separately at approximately 7.17 minutes, is excluded from that total.

These runtimes depend on the execution environment, available resources, Spark configuration, and data layout. They are not guaranteed production runtimes.

Historical optimization experiments indicate potential improvements from Adaptive Query Execution and shuffle-partition tuning. However, raw benchmark logs are unavailable for independent verification, and run-to-run variation limits the conclusions that can be drawn from individual measurements.

Some Gold-stage scaling experiments used smaller prefix or limit samples. These samples may not preserve the original data distribution and are insufficient by themselves to establish linear scalability.

## 7. Operational Readiness

EpiScope is a prototype, not a deployed public-health decision-support system. It has not been established as suitable for clinical decisions, real outbreak declarations, staffing decisions, or resource allocation without expert review.

Before real-world use, the system would require evaluation on representative real data, independent validation, threshold calibration, monitoring for distribution shift, alert-review procedures, security and privacy assessments, failure handling, and clearly defined operational ownership.

Resource-allocation recommendations and preparedness calendars inherit the limitations of their input data, forecasts, detection outputs, and assumptions. Their presence in the pipeline does not demonstrate improved real-world outcomes.

## 8. Reproducibility and Metric Provenance

The current detection and forecast figures refer to specific saved evaluation outputs. Historical results remain unreconciled and should be clearly labelled as unverified.

Meaningful comparisons require the exact source output, evaluation period, dataset, configuration, and code version to be identified. Historical measurements transcribed from documentation should be distinguished from results independently reproduced using raw logs or data.

Future experiments should retain run configurations, Spark settings, timestamps, raw logs, input identifiers, and generated output paths to support independent reproduction.

## 9. Recommended Future Work

1. Reconcile historical and current detection and forecast metrics by rerunning evaluators against explicitly identified inputs and configurations.
2. Improve detector precision while monitoring sensitivity and false-positive rate; report threshold-dependent precision-recall trade-offs.
3. Compare the fixed-average forecast baseline with stronger baselines across multiple evaluation windows.
4. Test the Silver-layer quality rules against missing, invalid, duplicate, inconsistent, and out-of-range values where applicable.
5. Test small-count suppression at boundary values and inspect every public output for direct and indirect disclosure.
6. Repeat benchmark experiments with retained raw logs and documented configurations, using representative datasets where possible.
7. Validate the system on appropriate real-world data before making claims about public-health effectiveness or operational deployment.
