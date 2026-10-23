# EpiScope: Big Data Analytics for Synthetic Disease Surveillance

<div class="IEEEkeywords">

Big data analytics, Apache Spark, data quality, disease surveillance, outbreak detection, forecasting, privacy-aware visualization

</div>

# 1. Introduction

Disease-surveillance workflows may involve large volumes of records from different sources and require reliable data preparation before analytical results can be presented. A useful analytics prototype should demonstrate data ingestion, validation, aggregation, analytical processing, and controlled publication of derived information.

EpiScope was developed as a big-data analytics project to demonstrate this workflow using synthetic encounter records. It combines layered data processing with baseline outbreak detection and forecasting, resource-allocation and preparedness-calendar outputs, and a browser-based dashboard. The project emphasizes end-to-end processing and documents limitations in evaluation and privacy checks.

The main contributions are:

- A Bronze–Silver–Gold processing workflow for synthetic encounter data.
- A documented large-input data-quality reconciliation and quarantine process.
- Baseline outbreak-detection and fixed-horizon forecasting evaluations.
- Experiments documenting pipeline runtime, Gold-stage scaling, and Spark configuration comparisons.
- A public-data preparation stage that suppresses tested small case counts before dashboard export.

The project does not claim clinical validity, real-world epidemiological accuracy, or formal privacy guarantees.

# 2. System Architecture

EpiScope separates data preparation, analytics, and dashboard serving. Synthetic encounter records are ingested into the Bronze layer. The Silver stage validates records and separates accepted rows from quarantined rows. The Gold stage creates aggregated analytical datasets for downstream processing.

The analytics modules provide outbreak detection, forecasting, resource allocation, and preparedness-calendar outputs. Public-data preparation is applied before dashboard datasets are exported as JSON for visualization.

Apache Spark handles data transformations, Parquet stores processed analytical data, and D3.js v7 renders dashboard visualizations. The recorded experiments used Google Colab with Spark running in local mode. Runtime therefore depends on available resources, storage, partitioning, caching, and Spark configuration.

# 3. Data and Processing Method

## 3.1 Synthetic Input

The encounter records and outbreak labels used in the recorded experiments are synthetic. The project includes a generator for creating encounter records at different scales. Weather-related fields, if present, must also be treated as synthetic or derived unless their provenance has been independently established.

The results should not be interpreted as evidence of performance on real hospital records, government surveillance data, or observed weather data.

## 3.2 Layered Processing

The pipeline uses three logical data layers:

- **Bronze:** ingestion of source encounter records.
- **Silver:** validation, cleaning, and quarantine of records that fail implemented checks.
- **Gold:** aggregated datasets for downstream analytics and serving.

The Silver stage aims to reconcile accepted and quarantined rows with the input count. Successful reconciliation demonstrates row-count consistency for a particular run, but does not independently establish that every validation rule is correct.

## 3.3 Analytics

The outbreak detector is evaluated at the district–disease–day level, requiring at least 14 baseline days. Forecasting uses a seven-day-average baseline computed before the test period and repeated across a fixed 28-day horizon. It does not update predictions daily throughout the forecast horizon.

Resource allocation and preparedness-calendar components demonstrate downstream analytical processing. Their outputs are not validated operational guidance.

## 3.4 Public Data and Privacy

A public-data preparation stage precedes dashboard JSON export. The documented policy suppresses exact case counts from one through four. A recorded check found no exposed values in this range in the tested public case export.

This is a limited check rather than a complete privacy audit. Disclosure may still be possible through geographic or temporal combinations, totals, linked views, or repeated queries.

# 4. Experimental Setup

The recorded experiments used Google Colab and Apache Spark in local mode. The documented full-scale processing input contained 25,000,000 rows. Synthetic-data generation is excluded from the reported 27.40-minute processing-stage total.

Forecast evaluation covered December 4–31, 2025, and reported 8,960 district–disease–day observations. Detection metrics were taken from the latest saved evaluation output.

The runtime, optimization, scaling, and data-quality measurements are recorded historical results. Raw timing logs were unavailable in the paths reviewed during documentation, limiting independent verification.

# 5. Results

## 5.1 Data Quality

Table 1 summarizes the documented reconciliation for the 25-million-row run.

**Table 1. Documented Silver-stage reconciliation**

| Measure | Rows |
|---|---:|
| Input | 25,000,000 |
| Clean output | 24,825,210 |
| Quarantined output | 174,790 |
| Clean + quarantined | 25,000,000 |
| Quarantine rate | 0.69916% |

The clean and quarantined counts sum to the documented input count. These values were transcribed from project documentation and were not independently recounted during report preparation.

## 5.2 Pipeline Runtime

Table 2 presents the recorded stage runtimes. The total is the sum of recorded stage measurements, not an independent end-to-end timing measurement.

**Table 2. Documented processing-stage runtime**

| Stage | Runtime (min) |
|---|---:|
| Bronze | 5.16 |
| Silver | 12.83 |
| Gold | 3.57 |
| Outbreak detection | 1.47 |
| Forecast generation | 0.94 |
| Resource allocation | 0.59 |
| Preparedness calendar | 0.57 |
| Public-data build | 0.50 |
| Dashboard export | 0.66 |
| Forecast evaluation | 0.86 |
| Detection evaluation | 0.75 |
| **Total measured stages** | **27.40** |

The documented total is below the project's 45-minute target. Synthetic-data generation, recorded separately at approximately 7.17 minutes, is excluded. These measurements are environment-specific, and raw timing logs were not available in the reviewed paths.

## 5.3 Outbreak Detection

Table 3 shows the latest saved detection evaluation.

**Table 3. Latest saved outbreak-detection evaluation**

| Metric | Value |
|---|---:|
| True positives (TP) | 190 |
| False positives (FP) | 25,336 |
| False negatives (FN) | 169 |
| True negatives (TN) | 554,145 |
| Sensitivity | 52.92% |
| False-positive rate | 4.37% |
| Precision | 0.74% |

Sensitivity indicates that the detector identifies approximately half of the positive evaluation observations. However, precision of 0.74% indicates that false-positive alerts substantially outnumber true-positive alerts. This limits the usefulness of the current detector without review and further tuning. It should not be used for unreviewed operational decisions.

## 5.4 Forecasting

The latest saved forecast evaluation contains 8,960 observations for December 4–31, 2025. The seven-day-average fixed-horizon baseline achieved an MAE of 2.0182 cases and an RMSE of 2.6986 cases.

MAE measures the average absolute difference between predicted and actual counts, while RMSE penalizes larger errors more strongly. These values describe the evaluated synthetic dataset and depend on the evaluation target and calendar-completion procedure.

Earlier project documentation reported MAE of approximately 5.9894 and RMSE of approximately 11.6049. The original run and configuration could not be independently verified, and the discrepancy remains unresolved. The latest saved output is reported as the current result; the earlier figures remain unverified historical results.

## 5.5 Optimization and Scaling

Documented Gold-stage experiments report 4.91 minutes with AQE disabled and 200 shuffle partitions, compared with 3.45 minutes with AQE enabled and 32 partitions. The latter is approximately 29.7% lower than the baseline.

These are historical single-run measurements without raw logs in the reviewed paths. They indicate a potential optimization, not a reliable general speedup.

Gold-stage runtimes were documented as 1.55 minutes for 6.25 million rows, 2.03 minutes for 12.5 million rows, and 3.45 minutes for 24,825,210 clean rows. The smaller datasets were generated using prefix or row-limit samples and may not preserve the full dataset distribution. These measurements cover the Gold stage only, not end-to-end pipeline scaling.

# 6. Discussion

EpiScope demonstrates an integrated workflow connecting large-input processing, data-quality reconciliation, baseline analytics, and dashboard-oriented export. The documented Silver-stage reconciliation provides evidence of row accounting for the recorded run. The runtime records suggest that the measured stages fit within the stated processing target in the recorded environment, although the absence of raw timing logs limits independent verification.

The analytical results illustrate why evaluation metrics must be considered together. Sensitivity of 52.92% may appear useful in isolation, but precision of 0.74% indicates a substantial false-alert burden. Similarly, the forecast errors do not establish real-world predictive utility because the evaluation data are synthetic and the baseline is intentionally simple.

The unresolved differences between historical and current evaluation metrics highlight the need for reproducible experiments, explicit input identification, and automated result capture.

# 7. Limitations and Future Work

Several limitations remain:

- **Synthetic data:** The results do not establish performance on real surveillance data.
- **Detection quality:** Low precision and a substantial false-positive count require investigation of label construction, thresholds, class imbalance, and evaluation logic.
- **Forecast baseline:** The fixed seven-day average does not adapt during the 28-day horizon and should be compared with additional baselines under a reproducible evaluation protocol.
- **Historical discrepancies:** Older detection and forecast figures differ from current saved outputs and remain unreconciled.
- **Benchmark evidence:** Historical runtime and optimization records lack raw logs in the reviewed paths and may be affected by caching and environment variability.
- **Privacy:** Small-count suppression is not a formal privacy guarantee. All public exports and cross-view inference risks require further testing.
- **Quality-rule evidence:** The implemented Silver validation rules and their test evidence must be inventoried from source code before claiming compliance with a required rule count.

Future work should include reproducible experiment logging, repeated benchmark runs, a source-derived data-quality rule inventory, expanded public-output privacy tests, alternative forecasting baselines, and detector threshold analysis. Application to real public-health decisions would require representative real data, domain-expert review, and appropriate governance.

# 8. Conclusion

EpiScope demonstrates a layered big-data pipeline for synthetic disease-surveillance analytics, including data cleaning and quarantine, aggregation, baseline detection and forecasting, and dashboard data preparation.

The documented large-input run reconciles 25 million input rows and reports 27.40 minutes across measured processing and evaluation stages, excluding data generation. The latest saved evaluations report 52.92% detection sensitivity but only 0.74% precision, and forecast MAE and RMSE of 2.0182 and 2.6986 on a synthetic 28-day test period.

These results are preliminary and subject to unresolved historical discrepancies and limitations in independent reproducibility. EpiScope should be regarded as an educational prototype rather than a validated public-health decision-support tool.

# References

[1] Apache Software Foundation, “Apache Spark Documentation.” [Online]. Available: https://spark.apache.org/docs/latest/

[2] Apache Software Foundation, “Apache Parquet Documentation.” [Online]. Available: https://parquet.apache.org/docs/

[3] M. Bostock, V. Ogievetsky, and J. Heer, “D³: Data-Driven Documents,” *IEEE Transactions on Visualization and Computer Graphics*, vol. 17, no. 12, pp. 2301–2309, Dec. 2011, doi: 10.1109/TVCG.2011.185.

[4] IEEE, “IEEE Reference Guide.” [Online]. Available: https://journals.ieeeauthorcenter.ieee.org/your-role-in-article-production/ieee-editorial-style-manual/
