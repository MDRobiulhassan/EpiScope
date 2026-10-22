<div class="IEEEkeywords">

big data analytics, Apache Spark, data quality, disease surveillance,
outbreak detection, forecasting, privacy-aware visualization

</div>

# Introduction

Disease-surveillance workflows may involve large volumes of records from
different sources and require reliable preparation before analytical
results can be presented. A useful analytics prototype should
demonstrate data ingestion, validation, aggregation, analytical
processing, and the controlled publication of derived information.

EpiScope was developed as a big-data analytics project to demonstrate
such a workflow on synthetic encounter records. It combines layered data
processing with simple detection and forecasting baselines,
resource-allocation and preparedness-calendar outputs, and a browser
dashboard. The project emphasizes an end-to-end data path and records
limitations in the evaluation and privacy checks.

The main contributions of this project are:

- a Bronze–Silver–Gold processing workflow for synthetic encounter data;

- a documented large-input data-quality reconciliation and quarantine
  process;

- baseline outbreak-detection and fixed-horizon forecasting evaluations;

- experiments documenting pipeline timing, Gold-stage scaling, and Spark
  configuration comparisons; and

- a public-data preparation step that suppresses tested small case
  counts before dashboard export.

The paper does not claim clinical validity, real-world epidemiological
accuracy, or formal privacy guarantees.

# System Architecture

EpiScope separates data preparation, analytics, and dashboard serving.
Synthetic encounter records are ingested into the Bronze layer. The
Silver stage validates records and separates accepted rows from
quarantined rows. The Gold stage creates aggregated analytical datasets.
Detection, forecasting, resource allocation, and preparedness-calendar
modules consume analytical outputs. Public-data preparation is then
applied before JSON datasets are exported to the D3.js dashboard.

Apache Spark is used for data transformations, Parquet for processed
analytical storage, and D3.js v7 for browser visualization. The project
runs in a Google Colab environment with Spark in local mode for the
recorded experiments. Consequently, measured runtimes depend on the
runtime allocation, storage, partitioning, caching, and Spark
configuration.

# Data and Processing Method

## Synthetic Input

The encounter records and outbreak labels used in the recorded
experiments are synthetic. The project includes a generator for creating
encounter records at different scales. Weather-related fields, if
present in a given generated schema, must likewise be treated as
synthetic or derived unless their provenance is independently
established. Results should not be interpreted as evidence of
performance on hospital records, government surveillance data, or real
weather observations.

## Layered Processing

The pipeline uses three logical data layers:

- **Bronze:** ingestion of source encounter records;

- **Silver:** validation, cleaning, and quarantine of records that fail
  implemented checks;

- **Gold:** aggregated datasets for downstream analytics and serving.

The Silver stage aims to preserve accounting between accepted and
quarantined rows. Reconciliation demonstrates count consistency but does
not independently prove that every validation rule is correct.

## Analytics

The outbreak detector is a prototype evaluated at the
district–disease–day level for observations with at least 14 baseline
days. Forecasting uses a simple seven-day-average baseline computed
before the test period and repeated as a fixed prediction across a
28-day horizon. This is not a rolling forecast that updates predictions
every day. Resource allocation and preparedness-calendar components are
included as analytical demonstrations; their outputs are not validated
operational guidance.

## Public Data and Privacy

A public-data preparation step precedes dashboard JSON export. The
documented policy suppresses exact case counts from one through four. A
recorded check of the public case export found no exposed values in that
range in the tested output. This is a limited check, not a complete
privacy audit: inference may still be possible through geographic and
temporal combinations, totals, linked views, or repeated queries.

# Experimental Setup

The recorded experiments were run in Google Colab using Spark in local
mode. The documented full-scale processing input contained 25,000,000
rows. Synthetic-data generation is excluded from the reported
27.40-minute processing-stage total. The report distinguishes current
saved evaluation outputs from historical results that could not be
independently reproduced from the audited artifacts.

Forecast evaluation used the test period from December 4 through
December 31, 2025, with 8,960 district–disease–day observations.
Detection metrics are taken from the latest saved evaluation output.
Timing, optimization, scaling, and data-quality counts are historical
documented measurements; raw timing logs were not available in the
audited paths.

# Results

## Data Quality

Table <a href="#tab:quality" data-reference-type="ref"
data-reference="tab:quality">1</a> summarizes the documented
reconciliation for the 25-million-row run.

<div id="tab:quality">

| Measure             |       Rows |
|:--------------------|-----------:|
| Input               | 25,000,000 |
| Clean output        | 24,825,210 |
| Quarantined output  |    174,790 |
| Clean + quarantined | 25,000,000 |
| Quarantine rate     |   0.69916% |

Documented Silver-Stage Reconciliation

</div>

The clean and quarantined counts sum to the input count. These values
were transcribed from the project’s documentation and were not
independently recounted during report preparation.

## Pipeline Runtime

Table <a href="#tab:runtime" data-reference-type="ref"
data-reference="tab:runtime">2</a> presents documented stage runtimes.
The total is a sum of recorded stages, not an independent timing
measurement.

<div id="tab:runtime">

| Stage                 | Runtime (min) |
|:----------------------|--------------:|
| Bronze                |          5.16 |
| Silver                |         12.83 |
| Gold                  |          3.57 |
| Outbreak detection    |          1.47 |
| Forecast generation   |          0.94 |
| Resource allocation   |          0.59 |
| Preparedness calendar |          0.57 |
| Public-data build     |          0.50 |
| Dashboard export      |          0.66 |
| Forecast evaluation   |          0.86 |
| Detection evaluation  |          0.75 |
| Total measured stages |         27.40 |

Documented Processing-Stage Runtime

</div>

The documented total is below the project’s 45-minute target.
Synthetic-data generation, recorded separately at approximately 7.17
minutes, is excluded. These measurements are environment-specific, and
the raw timing logs were not found in the audited paths.

## Outbreak Detection

Table <a href="#tab:detection" data-reference-type="ref"
data-reference="tab:detection">3</a> shows the latest saved detection
evaluation.

<div id="tab:detection">

| Metric               |   Value |
|:---------------------|--------:|
| True positives (TP)  |     190 |
| False positives (FP) |  25,336 |
| False negatives (FN) |     169 |
| True negatives (TN)  | 554,145 |
| Sensitivity          |  52.92% |
| False-positive rate  |   4.37% |
| Precision            |   0.74% |

Latest Saved Outbreak-Detection Evaluation

</div>

Sensitivity indicates that the detector identifies approximately half of
the positive evaluation cases. However, precision of 0.74% means that
false-positive alerts greatly outnumber true-positive alerts. This
substantially limits the usefulness of the current detector without
review and further tuning. It must not be used for unreviewed
operational decisions.

## Forecasting

The latest saved forecast evaluation contains 8,960 observations for
December 4–31, 2025. The seven-day-average fixed-horizon baseline
achieved MAE $=2.0182$ cases and RMSE $=2.6986$ cases. MAE expresses the
average absolute difference between predicted and actual counts; RMSE
weights larger errors more heavily. These values describe only the
current synthetic evaluation and depend on the evaluation target and
calendar-completion procedure.

Earlier project documentation reported MAE approximately 5.9894 and RMSE
approximately 11.6049. The original run and configuration for those
values were not independently verified, and the discrepancy remains
unresolved. The latest saved output is reported here as the current
result, while the earlier figures are retained as unverified historical
results.

## Optimization and Scaling

Documented Gold-stage experiments report 4.91 minutes for AQE disabled
with 200 shuffle partitions, compared with 3.45 minutes for AQE enabled
with 32 partitions. The latter is approximately 29.7% lower than the
4.91-minute baseline. Because these are historical single-run
measurements without raw logs in the audited paths, they should be
interpreted as indicative observations rather than a reliable general
speedup.

Gold-stage runtimes were documented as 1.55 minutes for 6.25 million
rows, 2.03 minutes for 12.5 million rows, and 3.45 minutes for
24,825,210 clean rows. The smaller datasets were generated using prefix
or row-limit samples and may not preserve the full dataset distribution.
These measurements describe the Gold stage only, not end-to-end pipeline
scaling.

# Discussion

The project demonstrates an integrated workflow that connects
large-input processing, data-quality reconciliation, baseline analytics,
and dashboard-oriented export. The documented Silver-stage
reconciliation provides evidence of row accounting for the recorded run.
The runtime records suggest that the pipeline stages fit within the
stated processing target in the measured environment, although the
absence of raw timing logs limits independent verification.

The analytical results also show why evaluation metrics must be
interpreted together. A sensitivity of 52.92% may appear useful in
isolation, but precision of 0.74% indicates a high false-alert burden.
Similarly, the forecast errors cannot establish real-world predictive
utility because the evaluation data are synthetic and the baseline is
intentionally simple. The unresolved difference between current and
historical forecast metrics further motivates stronger experiment
provenance and automated result capture.

# Limitations and Future Work

Several limitations remain:

- **Synthetic data:** results do not establish performance on real
  surveillance data.

- **Detection quality:** very low precision and a substantial
  false-positive count require investigation of label construction,
  thresholds, class imbalance, and evaluation logic.

- **Forecast baseline:** the fixed seven-day average does not adapt
  through the 28-day horizon and should be compared against additional
  baselines using a reproducible evaluation protocol.

- **Historical discrepancies:** older forecast and detection figures
  differ from current saved outputs and have not been reconciled.

- **Benchmark evidence:** historical runtime and optimization records
  lack raw logs in the audited paths, and the reported values may be
  affected by caching and environment variability.

- **Privacy:** suppressing small counts is not a formal privacy
  guarantee. All public exports and cross-view inference risks require
  further testing.

- **Quality-rule evidence:** the distinct implemented Silver validation
  rules and their test evidence should be inventoried from source code
  before claiming full compliance with a required rule count.

Future work should include reproducible experiment logging, repeated
benchmark runs, a source-derived data-quality rule inventory, expanded
public-output privacy tests, alternative forecasting baselines, and
detector threshold analysis. Any application to real public-health
decisions would require representative real data, domain-expert review,
and appropriate governance.

# Conclusion

EpiScope demonstrates a layered big-data pipeline for synthetic
disease-surveillance analytics, including data cleaning and quarantine,
aggregation, baseline detection and forecasting, and dashboard data
preparation. The documented large-input run reconciles 25 million input
rows and reports 27.40 minutes across measured processing and evaluation
stages, excluding data generation. The latest saved evaluations report
52.92% detection sensitivity but only 0.74% precision, and forecast
MAE/RMSE of 2.0182/2.6986 on a synthetic 28-day test period. These
results are preliminary and subject to unresolved historical
discrepancies and limitations in independent reproducibility. The system
should be regarded as an educational prototype rather than a validated
public-health decision-support tool.

<div class="thebibliography">

00 Apache Software Foundation, “Apache Spark Documentation.” \[Online\].
Available: <https://spark.apache.org/docs/latest/>

Apache Software Foundation, “Apache Parquet Documentation.” \[Online\].
Available: <https://parquet.apache.org/docs/>

M. Bostock, V. Ogievetsky, and J. Heer, “D$^3$: Data-Driven Documents,”
*IEEE Transactions on Visualization and Computer Graphics*, vol. 17, no.
12, pp. 2301–2309, Dec. 2011, doi: 10.1109/TVCG.2011.185.

IEEE, “IEEE Reference Guide.” \[Online\]. Available:
<https://journals.ieeeauthorcenter.ieee.org/your-role-in-article-production/ieee-editorial-style-manual/>

</div>
