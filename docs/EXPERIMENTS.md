# Experiments, Performance, and Evaluation

## Environment and interpretation

The following values are from the recorded Google Colab/Spark experiments. They are observed measurements, not guaranteed runtimes on other machines. Encounter generation time is excluded from the pipeline-runtime total.

## 25-million-input pipeline

| Stage | Recorded runtime |
|---|---:|
| Bronze | 5.16 min |
| Silver | 12.83 min |
| Gold | 3.57 min |
| Outbreak detection | 1.47 min |
| Forecast generation | 0.94 min |
| Resource allocation | 0.59 min |
| Preparedness calendar | 0.57 min |
| Public-data build | 0.50 min |
| Dashboard export | 0.66 min |
| Forecast evaluation | 0.86 min |
| Detection evaluation | 0.75 min |
| **Total measured stages** | **27.40 min** |

The nine main processing stages took approximately 25.79 minutes. Including both evaluation stages gives approximately 27.40 minutes, under the 45-minute target. The separate synthetic-data generation run took approximately 7.17 minutes and is excluded from this total.

## Data reconciliation

For the 25-million-input experiment:

- Input: 25,000,000 rows
- Silver clean output: 24,825,210 rows
- Quarantine: 174,790 rows
- Clean plus quarantine equals the input count.
- Quarantine rate: approximately 0.699%.

## Spark optimization experiments

A Gold-stage benchmark was run against the same Silver input using isolated output projects.

| Configuration | Runtime |
|---|---:|
| AQE off, 200 shuffle partitions | 4.91 min |
| AQE on, 200 shuffle partitions | 3.52 min |
| AQE off, 64 shuffle partitions | 4.12 min |
| AQE on, 200 shuffle partitions, repeat | 3.63 min |
| AQE on, 64 shuffle partitions | 3.55 min |
| AQE on, 32 shuffle partitions | 3.45 min |

The first AQE-on 200-partition run was approximately 28.3% faster than the 4.91-minute baseline. In the later comparison, the AQE-on 32-partition run was approximately 29.7% faster than that baseline. These are single-run observations, so runtime variability is a limitation. The later AQE-on 200-partition run took 3.63 minutes, indicating that the apparent improvement from lowering partitions from 200 to 32 was relatively small.

The experiment supports reporting AQE and shuffle partition configuration as investigated optimization techniques. It does not establish a universal speedup. Preserve the benchmark scripts/configuration and raw timing records where available.

A separate microbenchmark returned 10.40 seconds at 2 shuffle partitions, 11.36 seconds at 8, and 13.11 seconds at 16. AQE off/on timings at 2 partitions were 11.21 and 11.92 seconds. This microbenchmark is exploratory and should not be treated as the primary optimization evidence.

## Scaling experiments

These measurements are for the Gold stage only, not the entire pipeline.

| Scale | Rows | Gold runtime |
|---|---:|---:|
| SF 0.25 | 6,250,000 | 1.55 min |
| SF 0.5 | 12,500,000 | 2.03 min |
| SF 1.0 | 24,825,210 clean rows | 3.45 min |

The smaller datasets were created using row limits/prefix samples. They may not preserve the original data distribution. State this limitation when interpreting the scaling curve.

## Forecast evaluation

Latest verified evaluation metrics:

- Evaluation observations: 8,960
- MAE: 2.0182 cases
- RMSE: 2.6986 cases
- Test period: December 4–31, 2025
- Baseline: 7-day average computed before the test window and repeated across the fixed 28-day horizon.
- Evaluation output: `data/gold/forecast_evaluation/overall/part-00000-278a3b6c-3c49-4ff5-b57b-7e60da834a78-c000.json`

Historical documentation previously reported MAE approximately 5.9894 and RMSE approximately 11.6049. Their original evaluation could not be independently verified, so these values are retained as historical results rather than current results.

This is a simple fixed-horizon baseline, not a rolling daily-updated forecast. Error values should be interpreted in the units of the evaluated target and within the synthetic dataset only. The discrepancy between historical and current metrics remains unresolved.

## Outbreak detection evaluation

Latest verified evaluation:

| Metric | Result |
|---|---:|
| TP | 190 |
| FP | 25,336 |
| FN | 169 |
| TN | 554,145 |
| Sensitivity | 52.92% |
| False-positive rate | 4.37% |
| Precision | 0.74% |

Evaluation unit: district-disease-day with at least 14 baseline days.

These values come from the latest saved evaluation output. Historical documentation previously reported TP=184, FP=21,186, FN=175, TN=558,295, sensitivity approximately 51.25%, and false-positive rate approximately 3.66%. Those historical values have not been independently verified and are not substituted for the latest output. The discrepancy remains unresolved.

## Dashboard privacy check

The recorded public `cases.json` contained 584,320 records. The tested check found no exposed `published_case_count` values from 1 through 4, with approximately 246,000 records reported as suppressed. Repeat the check after every public-data rebuild.

## Reproducibility requirements

For the final submission, retain the raw benchmark outputs when available and record:
- Machine/runtime environment and Spark version.
- Exact input dataset and row count.
- Spark configuration for each benchmark.
- Command/script used and exit status.
- Runtime measurement method.
- Output validation and row counts.
- Repeated runs or a clear note when results are single-run observations.
