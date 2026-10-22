# Limitations

## 1. Synthetic Data and External Validity

EpiScope is an educational big-data analytics prototype evaluated primarily
using synthetic disease-surveillance encounter data. Its results demonstrate
pipeline execution and analytical behavior on the generated dataset; they do
not establish performance on real clinical or public-health surveillance data.

Synthetic data may not reproduce real disease prevalence, reporting delays,
seasonality, demographic differences, missingness, geographic variation, or
operational data-quality problems. Consequently, the detection and forecasting
results must not be interpreted as evidence of clinical validity or operational
readiness.

Weather-related or other contextual fields should not be interpreted as
verified real-world observations unless their provenance has been independently
established.

## 2. Outbreak Detection Performance

The latest saved detection evaluation reports the following confusion matrix:

| Metric | Latest saved result |
|---|---:|
| True positives (TP) | 190 |
| False positives (FP) | 25,336 |
| False negatives (FN) | 169 |
| True negatives (TN) | 554,145 |
| Sensitivity (recall) | 52.92% |
| False-positive rate (FPR) | 4.37% |
| Precision | 0.74% |

The evaluation unit is district-disease-day, with at least 14 baseline days
required. The saved evaluation output is located at:

`data/gold/detection_evaluation/part-00000-d8fdf23b-e479-43f4-8978-0cdc8bfaf662-c000.json`

The results show a substantial false-positive burden: the detector identifies
some positive cases but many alerts are false positives. Its 0.74% precision
means that fewer than 1 in 100 predicted positives in this evaluation are true
positives. The detector should therefore be treated as an experimental
screening component, not a reliable alerting system for real-world use.

Sensitivity is also incomplete, so the detector misses some positive
district-disease-day observations. Performance may change with the baseline
definition, thresholds, disease frequency, synthetic data-generation process,
and evaluation unit.

Previously documented detection metrics (TP=184, FP=21,186, FN=175, TN=558,295;
sensitivity=51.25%, FPR=3.66%, precision=0.86%) are retained as historical,
unverified results. They have not been reconciled with the latest saved
evaluation and should not be presented as equivalent or interchangeable
measurements.

## 3. Forecasting Limitations

The latest saved forecast evaluation reports:

| Metric | Latest saved result |
|---|---:|
| Evaluation observations | 8,960 |
| Mean absolute error (MAE) | 2.0182 |
| Root mean squared error (RMSE) | 2.6986 |
| Test period | 2025-12-04 to 2025-12-31 |
| Forecast method | 7-day average, fixed 28-day horizon |

The saved evaluation output is located at:

`data/gold/forecast_evaluation/overall/part-00000-278a3b6c-3c49-4ff5-b57b-7e60da834a78-c000.json`

The method uses a 7-day average and repeats it across a fixed 28-day forecast
horizon. This is a simple baseline, not a model that learns changing trends,
seasonality, weather effects, or other external drivers. Forecast accuracy may
deteriorate when patterns change or when applied outside the evaluated period
and synthetic dataset.

The MAE and RMSE are expressed in the scale of the evaluated target. They
should not be interpreted as relative errors or compared across datasets with
different scales without additional analysis.

Older documented forecast results (MAE approximately 5.9894 and RMSE
approximately 11.6049) remain historical and unverified. They differ from the
latest saved evaluation and have not been reconciled. Other previously recorded
forecast figures should likewise not be treated as current unless reproduced
from a clearly identified evaluation output.

## 4. Data Quality and Quarantine

Historical documentation records 25,000,000 input rows, 24,825,210 clean rows,
and 174,790 quarantined rows, corresponding to a quarantine rate of
approximately 0.69916%. The clean and quarantined counts reconcile to the
documented input total.

These figures are documented measurements and have not necessarily been
recomputed during the latest documentation update. Their validity depends on
the pipeline version, input data, and run that produced them.

The complete set of Silver-layer quality rules should be verified against the
current implementation. A documented list alone does not establish that every
rule is implemented, tested, or triggered correctly.

## 5. Privacy and Small-Count Suppression

The public-data preparation process is intended to suppress small published
counts, particularly counts from 1 through 4. A previous check of
`cases.json` found no exact `published_case_count` values from 1 through 4,
but this limited check does not establish that every public output is safe.

Suppression must be tested for counts 1, 2, 3, 4, and 5 and checked across all
published files and relevant derived fields. Counts can potentially be inferred
from totals, differences, repeated releases, or related dimensions even when
individual small values are suppressed.

Small-count suppression alone is not a formal privacy guarantee. This prototype
has not established differential privacy, resistance to linkage attacks, or
comprehensive protection against re-identification. It should not be described
as formally privacy-preserving without additional analysis.

## 6. Performance and Scalability

The experiment documentation records a total of approximately 27.40 minutes
for the measured pipeline stages, including detection and forecast evaluation,
on a 25-million-row input. Data generation, documented separately at
approximately 7.17 minutes, is excluded from that total.

The reported timings are environment-dependent and should not be treated as
guaranteed production performance. Historical optimization experiments report
improvements from Adaptive Query Execution and partition tuning, but the raw
benchmark logs are unavailable for independent verification. Run-to-run
variation, runtime configuration, available resources, and data layout can
affect the results.

Gold-stage scaling experiments used smaller prefix or limit samples for some
runs. These samples may not preserve the full dataset's distribution and are
not sufficient by themselves to establish linear scalability.

## 7. Operational Readiness

EpiScope is a prototype, not a deployed public-health decision-support system.
It has not been established as suitable for clinical decisions, real outbreak
declarations, staffing decisions, or resource allocation without expert review.

Before real-world use, the system would require evaluation on representative
real data, independent validation, threshold calibration, monitoring for
distribution shift, alert-review procedures, security and privacy assessment,
failure handling, and documented operational ownership.

Resource-allocation recommendations and preparedness calendars inherit the
limitations of their input forecasts, detection outputs, and assumptions.
Their presence in the pipeline does not demonstrate that the recommendations
improve real-world outcomes.

## 8. Reproducibility and Metric Provenance

The current detection and forecast figures above refer to specific saved
evaluation outputs. Historical figures are preserved for traceability but
remain unreconciled. Comparisons should identify the exact source output,
evaluation period, dataset, configuration, and code version.

Performance tables and quality counts transcribed from historical documentation
should be distinguished from measurements independently reproduced from raw
logs or data. Future experiments should retain run configuration, Spark
settings, timestamps, raw logs, input identifiers, and generated output paths
so results can be independently reproduced.

## 9. Recommended Future Work

1. Reconcile historical and current detection and forecast metrics by rerunning
   evaluators against explicitly identified inputs and configurations.
2. Improve detector precision while monitoring sensitivity and false-positive
   rate, and report threshold-dependent precision-recall trade-offs.
3. Compare the fixed-average forecast baseline with stronger baselines and
   evaluate across multiple time windows.
4. Audit and test all Silver-layer quality rules, including invalid, missing,
   duplicate, inconsistent, and out-of-range values where applicable.
5. Test small-count suppression at boundary values and inspect every public
   output for direct and indirect disclosure.
6. Repeat benchmark experiments with raw logs and documented configurations,
   and evaluate representative data rather than prefix samples alone.
7. Validate the system on appropriate real-world data before making claims
   about public-health effectiveness or operational deployment.
