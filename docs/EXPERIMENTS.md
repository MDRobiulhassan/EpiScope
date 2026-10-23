# EpiScope Experiments, Performance, and Evaluation

## 1. Environment and Interpretation

The measurements in this document were recorded during Google Colab experiments using Apache Spark in local mode. They are observed runtimes, not guaranteed performance on other machines.

Synthetic encounter generation is excluded from the pipeline-runtime total unless explicitly stated.

## 2. Full-Scale Pipeline Performance

The recorded experiment used 25,000,000 input encounter rows.

| Stage | Recorded runtime |
|---|---:|
| Bronze ingestion | 5.16 min |
| Silver validation and cleaning | 12.83 min |
| Gold aggregation | 3.57 min |
| Outbreak detection | 1.47 min |
| Forecast generation | 0.94 min |
| Resource allocation | 0.59 min |
| Preparedness calendar | 0.57 min |
| Public-data preparation | 0.50 min |
| Dashboard export | 0.66 min |
| Forecast evaluation | 0.86 min |
| Detection evaluation | 0.75 min |
| **Total measured stages** | **27.40 min** |

The nine processing and serving stages took approximately 25.79 minutes. Including forecast and detection evaluation brings the total to approximately 27.40 minutes, below the 45-minute target.

The separate synthetic-data generation run took approximately 7.17 minutes and is excluded from the reported pipeline total.

These measurements reflect the recorded execution environment and should not be interpreted as guaranteed runtimes elsewhere.

## 3. Data Reconciliation

The recorded 25-million-input experiment produced the following results:

| Measure | Result |
|---|---:|
| Input rows | 25,000,000 |
| Silver clean rows | 24,825,210 |
| Quarantined rows | 174,790 |
| Quarantine rate | Approximately 0.69916% |
| Reconciliation | Clean + quarantine = input |

The counts reconcile exactly:

\[
24{,}825{,}210 + 174{,}790 = 25{,}000{,}000
\]

This confirms row-count reconciliation for the recorded run. It does not independently verify the correctness of every validation rule.

## 4. Spark Optimization Experiments

A Gold-stage benchmark compared Spark Adaptive Query Execution (AQE) and shuffle partition configurations using the same Silver input and isolated output locations.

| Configuration | Runtime |
|---|---:|
| AQE off, 200 shuffle partitions | 4.91 min |
| AQE on, 200 shuffle partitions | 3.52 min |
| AQE off, 64 shuffle partitions | 4.12 min |
| AQE on, 200 shuffle partitions, repeat | 3.63 min |
| AQE on, 64 shuffle partitions | 3.55 min |
| AQE on, 32 shuffle partitions | 3.45 min |

Compared with the 4.91-minute baseline:

- The first AQE-on, 200-partition run was approximately 28.3% faster.
- The AQE-on, 32-partition run was approximately 29.7% faster.
- The repeated AQE-on, 200-partition run took 3.63 minutes, illustrating run-to-run variability.

The difference between the 3.63-minute repeated 200-partition run and the 3.45-minute 32-partition run was relatively small. Because these are single-run observations rather than repeated statistical trials, they do not establish a universal performance improvement or an optimal partition count.

A separate exploratory microbenchmark recorded:

| Configuration | Runtime |
|---|---:|
| 2 shuffle partitions | 10.40 sec |
| 8 shuffle partitions | 11.36 sec |
| 16 shuffle partitions | 13.11 sec |
| AQE off, 2 partitions | 11.21 sec |
| AQE on, 2 partitions | 11.92 sec |

This microbenchmark is exploratory and should not be used as the primary evidence for optimization claims.

## 5. Gold-Stage Scaling Experiments

The following measurements cover the Gold stage only, not the full pipeline.

| Scale | Rows | Gold runtime |
|---|---:|---:|
| SF 0.25 | 6,250,000 | 1.55 min |
| SF 0.5 | 12,500,000 | 2.03 min |
| SF 1.0 | 24,825,210 clean rows | 3.45 min |

The smaller datasets were created using row limits or prefix samples. They may not preserve the original data distribution, so the measurements should be interpreted as observations of the tested subsets rather than a definitive scaling curve.

## 6. Forecast Evaluation

The latest recorded forecast evaluation reports the following results:

| Measure | Result |
|---|---:|
| Evaluation observations | 8,960 |
| Mean Absolute Error (MAE) | 2.0182 cases |
| Root Mean Squared Error (RMSE) | 2.6986 cases |
| Test period | December 4–31, 2025 |
| Model | Seven-day average, fixed 28-day horizon |

The baseline uses a seven-day average computed before the test window and repeats that forecast across the fixed 28-day horizon. It is not a rolling daily-updated forecast.

Evaluation output:

`data/gold/forecast_evaluation/overall/part-00000-278a3b6c-3c49-4ff5-b57b-7e60da834a78-c000.json`

Earlier documentation reported MAE of approximately 5.9894 and RMSE of approximately 11.6049. The original evaluation supporting those historical values could not be independently verified. They are therefore retained as historical results and are not treated as the current evaluation.

The discrepancy between the historical and latest metrics remains unresolved. The results should be interpreted in the target's units and within the synthetic dataset; they do not establish predictive performance on real-world surveillance data.

## 7. Outbreak Detection Evaluation

The latest recorded evaluation reports:

| Metric | Result |
|---|---:|
| True positives (TP) | 190 |
| False positives (FP) | 25,336 |
| False negatives (FN) | 169 |
| True negatives (TN) | 554,145 |
| Sensitivity | 52.92% |
| False-positive rate | 4.37% |
| Precision | 0.74% |

The evaluation unit is a district-disease-day, restricted to units with at least 14 baseline days.

Earlier documentation reported TP = 184, FP = 21,186, FN = 175, TN = 558,295, sensitivity of approximately 51.25%, and false-positive rate of approximately 3.66%. Those historical results have not been independently verified and are not substituted for the latest recorded evaluation. The discrepancy remains unresolved.

The low precision indicates that false-positive alerts substantially outnumber true-positive alerts in this evaluation. Sensitivity alone is therefore insufficient to establish operational usefulness.

## 8. Dashboard Privacy Check

The recorded public `dashboard/data/cases.json` contained 584,320 records. The recorded check found no exposed `published_case_count` values from 1 through 4, with approximately 246,000 records reported as suppressed.

This result documents the tested output at that time. It does not prove that all public datasets are free from disclosure risks or that small counts cannot be inferred from totals, linked views, or other published fields. The check should be repeated after rebuilding public data.

## 9. Reproducibility and Limitations

Interpretation of these experiments is limited by run-to-run variability, the recorded environment, incomplete historical evidence, and the use of synthetic data.

Where available, retain benchmark logs and configuration records containing:

- Runtime environment and Spark version.
- Input dataset and row count.
- Spark configuration for each benchmark.
- Command or script used and its exit status.
- Runtime measurement method.
- Output validation and resulting row counts.
- Repeated measurements or an explicit note that a result comes from a single run.

Historical metrics whose original evidence is unavailable should remain clearly identified as unverified. Performance and evaluation results should be reproducible from the submitted version before they are presented as definitive.
