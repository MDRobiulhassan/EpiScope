# EpiScope: Public Health Surveillance and Preparedness Dashboard

**Course:** CSE 4345 – Big Data Analytics
**Institution:** Department of CSE, Premier University, Chittagong
**Semester:** Spring 2026
**Repository:** [https://github.com/mdrobiulhassan/EpiScore](https://github.com/mdrobiulhassan/EpiScore)

## 1. Problem and Stakeholders

EpiScope is a research prototype for district-level public health surveillance and preparedness in Bangladesh. It combines synthetic encounter records, administrative boundaries, population estimates, weather observations, facility information, and resource-stock data to demonstrate how large-scale data analytics can support early outbreak detection, short-term forecasting, and resource planning.

The primary stakeholders are public health authorities, district health officers, surveillance analysts, healthcare facilities, and emergency-preparedness planners. The system aims to help these users identify unusual disease activity, understand expected demand, and compare resource-allocation strategies. Since the encounter data are synthetic and the analytical methods are experimental, the outputs are intended for research and demonstration rather than clinical or operational decisions.

## 2. CEP Attribute Analysis and Design Conflicts

The project considers the following Complex Event Processing (CEP) attributes:

- **P1 – Timeliness:** detect emerging outbreaks promptly.
- **P2 – Accuracy:** limit false alerts while retaining sensitivity to genuine outbreaks.
- **P3 – Scalability:** process millions of encounters across Bangladesh's 64 districts.
- **P4 – Reliability:** support repeatable, incremental processing and traceable outputs.
- **P5 – Privacy:** protect individuals and suppress small public counts.
- **P6 – Usability:** communicate trends, uncertainty, alerts, and resource needs clearly.
- **P7 – Cost efficiency:** remain reproducible in a constrained research environment.

Five design conflicts guide implementation. **C1, sensitivity versus false alarms:** evaluate detection thresholds against injected outbreak ground truth. **C2, geographic detail versus privacy:** retain useful district-level summaries while suppressing counts from one to four. **C3, efficiency versus equity:** compare optimized resource allocation with population-proportional allocation. **C4, freshness versus computational cost:** balance update frequency with batch-processing cost. **C5, predictive accuracy versus interpretability:** evaluate forecasting performance against a seasonal-naïve baseline and document methodological limitations.

## 3. Architecture and Tools

EpiScope follows a layered data architecture:

1. **Generation and ingestion:** deterministic synthetic encounter generation and preparation of supporting datasets.
2. **Bronze:** immutable source records with ingestion metadata and batch identifiers.
3. **Silver:** cleaned, validated, and standardized records, with invalid records quarantined and reason-coded.
4. **Gold:** aggregated surveillance indicators, detection scores, forecasts, resource estimates, and preparedness outputs.
5. **Serving and visualization:** privacy-protected aggregated JSON files served to a D3.js v7 dashboard.

Apache Spark and PySpark perform large-scale transformations and analytics. Parquet provides columnar storage for processed datasets. Python supports generation, orchestration, evaluation, and export; D3.js provides interactive visualizations. GitHub maintains source control, while GitHub Pages hosts the static dashboard. The final implementation and its documentation will specify the exact environment, execution commands, and deployment process.

## 4. Data and Analytics Methods

The project uses six principal data categories: administrative boundaries, population estimates, historical weather, synthetic health encounters, synthetic healthcare facilities, and daily resource or bed-occupancy records. Synthetic data include controlled quality defects and injected outbreaks to evaluate pipeline behavior. Ground-truth outbreak labels are reserved for evaluation and must not be used as detector inputs.

The analytical workflow includes:

- Automated validation, quarantine, deduplication, and data-quality reporting.
- District- and disease-level outbreak detection using the implemented statistical detection method(s), evaluated against injected ground truth.
- Weekly forecasts for at least two configured disease groups, at one- to four-week horizons, with lagged weather features where supported by the implementation.
- Conversion of predicted cases into estimated bed, intravenous-fluid, and test-kit demand using documented assumptions.
- Linear or integer optimization of resource allocation under a fixed budget, compared with population-proportional allocation.
- Seasonal decomposition to prepare a division-level preparedness calendar.

Evaluation will report detection performance, forecast errors and prediction-interval coverage, allocation comparisons, runtime, output sizes, and Spark optimization results. Claims will be limited to experiments that can be reproduced from the final tagged repository.

## 5. Team Roles

Each member will lead a defined work area while contributing to integration, testing, documentation, and presentation. Final member names, student IDs, and agreed assignments must be recorded before submission.

- **Project coordination and architecture:** integration, requirement traceability, design decisions, and release management.
- **Data engineering:** synthetic data generation, ingestion, Spark transformations, data quality, and lineage.
- **Analytics:** outbreak detection, forecast evaluation, resource-demand estimation, optimization, and preparedness analysis.
- **Dashboard and serving:** public-data preparation, suppression checks, JSON exports, D3.js visualization, and usability evaluation.
- **Shared responsibilities:** testing, report preparation, risk management, code review, and the recorded presentation.

Actual responsibilities and contributions will be documented in the agreed contribution matrix.

## 6. Risk Register

| Risk                                                               | Mitigation                                                                                    |
| ------------------------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| Synthetic data may not represent real disease dynamics             | Document assumptions and avoid operational claims.                                            |
| Excessive false alerts may reduce usefulness                       | Evaluate threshold trade-offs and report false-alert rates.                                   |
| Small counts or related totals may reveal suppressed values        | Apply suppression consistently and test for indirect disclosure.                              |
| Late or duplicate records may distort trends                       | Test incremental idempotency, deduplication, and late-arrival handling.                       |
| Forecasts may perform poorly during unusual outbreaks              | Compare against a seasonal-naïve baseline and report uncertainty.                             |
| Resource optimization may favor high-population districts unfairly | Compare allocation strategies and evaluate efficiency–equity trade-offs.                      |
| Large workloads may exceed available compute resources             | Measure runtimes, optimize Spark operations, and document scaling limits.                     |
| Deployment may omit data files or expose sensitive information     | Validate published outputs, exclude raw records and secrets, and test the deployed dashboard. |

## 7. Expected Outcome

The expected deliverable is a reproducible research prototype that demonstrates a complete public-health analytics workflow, from data ingestion and validation through detection, forecasting, resource planning, and public-facing visualization. The final report will discuss the evidence, design trade-offs, ethical implications, limitations, and potential future improvements.
