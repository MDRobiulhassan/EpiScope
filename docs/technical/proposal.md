# EpiScope: Public Health Surveillance and Preparedness Dashboard

**Course:** CSE 4345 - Big Data Analytics  
**Institution:** Department of Computer Science and Engineering, Premier University, Chittagong  
**Semester:** Spring 2026  
**Repository:** [EpiScope on GitHub](https://github.com/mdrobiulhassan/EpiScope)

## 1. Problem and Stakeholders

EpiScope is a research prototype for district-level public-health surveillance and preparedness in Bangladesh. It uses synthetic encounter records to demonstrate how large-scale data analytics can support outbreak-signal generation, short-term forecasting, and resource planning.

The intended stakeholders include public-health authorities, district health officers, surveillance analysts, healthcare facilities, and emergency-preparedness planners. The system explores how these users might identify unusual disease activity, estimate future demand, and compare resource-allocation strategies.

Because the encounter data are synthetic and the analytical methods are experimental, EpiScope is intended for research and demonstration rather than clinical or operational decision-making.

## 2. CEP Attributes and Design Conflicts

The project considers seven Complex Event Processing (CEP) attributes:

- **P1 - Timeliness:** Identify emerging outbreak signals promptly.
- **P2 - Accuracy:** Limit false alerts while retaining sensitivity to genuine outbreaks.
- **P3 - Scalability:** Process millions of encounter records across Bangladesh's 64 districts.
- **P4 - Reliability:** Support repeatable processing, traceable outputs, and testing of incremental-processing behavior.
- **P5 - Privacy:** Protect individual-level information and suppress small public counts.
- **P6 - Usability:** Communicate trends, alerts, forecasts, and resource needs clearly.
- **P7 - Cost efficiency:** Keep experiments reproducible within a constrained research environment.

Five design conflicts guide the project:

- **C1 - Sensitivity versus false alarms:** Evaluate detection performance and threshold trade-offs against synthetic outbreak ground truth.
- **C2 - Geographic detail versus privacy:** Preserve useful district-level summaries while suppressing exact public case counts from one through four.
- **C3 - Efficiency versus equity:** Compare resource-allocation strategies with population-proportional allocation and examine their trade-offs.
- **C4 - Freshness versus computational cost:** Consider update frequency alongside batch-processing time and resource requirements.
- **C5 - Predictive accuracy versus interpretability:** Evaluate the forecasting baseline against appropriate alternatives and document its methodological limitations.

These attributes and conflicts provide a framework for discussing system design and evaluation. They do not, by themselves, establish that every requirement has been fully satisfied.

## 3. Architecture and Tools

EpiScope follows a layered data-processing architecture:

1. **Generation and ingestion:** Generate synthetic encounter records and prepare the required input datasets.
2. **Bronze:** Ingest source records for downstream processing.
3. **Silver:** Validate and clean records, standardize supported fields, and quarantine records that fail implemented checks.
4. **Gold:** Produce aggregated analytical datasets for detection, forecasting, resource estimation, and preparedness outputs.
5. **Serving and visualization:** Prepare public-facing datasets, apply documented small-count suppression, export JSON files, and present selected outputs through a D3.js v7 dashboard.

The incremental inventory demonstration is a separate source path: it generates one daily facility stock and bed-occupancy snapshot, appends unseen `(snapshot_date, facility_id)` keys to Bronze, validates and quarantines records in Silver, and aggregates district-day totals in Gold. It is currently a parallel pipeline; the resource-allocation optimizer does not consume these inventory aggregates, and corrected values for an existing key are not merged.

Apache Spark and PySpark perform data transformations and analytical processing. Parquet provides columnar storage for processed datasets. Python supports data generation, analytics, evaluation, and export. D3.js provides interactive visualizations, while GitHub supports source control and GitHub Pages hosts the static dashboard.

The final tagged repository and its documentation are the authoritative references for actual implementation details, execution commands, dependencies, and deployment behavior.

## 4. Data and Analytics Methods

The project focuses on synthetic health-encounter records and supporting information required by the implemented pipeline. Depending on the generated schema and available inputs, supporting fields may represent administrative geography, population, weather, healthcare facilities, or resource availability. The provenance of each dataset must be documented, and synthetic or derived values must not be presented as observed real-world measurements.

The analytical workflow covers the following areas:

- **Data quality:** The delivered Silver implementation declares 15 named encounter checks and separates invalid records into quarantine. The recorded batch counts reconcile, and the Colab notebook records a two-pass inventory replay. The current unit tests cover selected age and temperature boundaries, not every Silver rule. Inventory replay is first-write-wins; corrections to an existing `(snapshot_date, facility_id)` are not merged.
- **Outbreak detection:** Generate district-disease-day signals using the implemented detection method. Evaluate performance against synthetic ground-truth labels without exposing those labels to the detector as input.
- **Forecasting:** The delivered baseline repeats a seven-day average over a fixed 28-day horizon and has a saved synthetic evaluation. Additional disease-specific analysis, shorter forecast horizons, weather-lag features, and seasonal-naive comparisons are proposed extensions, not part of the reported evaluation.
- **Resource estimation:** Demonstrate how predicted case counts may be translated into estimated resource demand using explicitly documented assumptions.
- **Resource allocation:** Explore resource-allocation outputs and compare them with an appropriate baseline where the necessary implementation and evaluation evidence are available.
- **Preparedness planning:** Generate preparedness-calendar outputs as an analytical demonstration, without treating them as validated operational recommendations.

Evaluation should cover detection sensitivity, precision, false-positive rate, forecast errors, allocation comparisons, processing runtime, and relevant optimization experiments. Prediction-interval coverage, incremental-processing behavior, and additional forecasting comparisons should be reported only if implemented and tested.

All performance claims must correspond to identifiable outputs and reproducible experiments in the final tagged repository.

## 5. Team Roles and Contributions

The four-member team and documented project roles are:

| Member | Student ID | Documented work areas |
|---|---|---|
| Md. Samin Osman | 0222220005101042 | Data generation, Silver validation, analytics, dashboard, tests, and execution materials. |
| Robiul Hassan | 0222220005101043 | Pipeline and incremental inventory work, dashboard-data updates, documentation, and integration. |
| Walid Talal | 0222220005101045 | Member-reported report writing and submission preparation. |
| Md. Mahafujul Alam | 0222220005101066 | Presentation and project-material preparation. |

These work areas summarize repository and member-reported evidence; they do not assign effort percentages. Testing, documentation, integration, and presentation preparation were team-wide activities.

The four-member presentation assigns Robiul Hassan (0222220005101043) the pipeline narrative, Md. Samin Osman (0222220005101042) evaluation and planning, Md. Mahafujul Alam (0222220005101066) the dashboard, and Walid Talal (0222220005101045) privacy, limitations, and recommendations. These assignments describe presentation sections.

## 6. Risk Register

| Risk | Mitigation |
|---|---|
| Synthetic data may not represent real disease dynamics. | Document assumptions and avoid unsupported operational claims. |
| Excessive false alerts may reduce usefulness. | Evaluate detection thresholds and report precision, sensitivity, and false-positive rates together. |
| Small counts or related totals may reveal suppressed values. | Apply suppression consistently and test for indirect disclosure across public outputs. |
| Late or duplicate records may distort trends. | Test deduplication, idempotency, and late-arrival handling before claiming support. |
| Forecasts may perform poorly during unusual outbreaks. | Compare against appropriate baselines and report limitations and uncertainty where evaluated. |
| Resource allocation may favor high-population districts unfairly. | Compare allocation strategies and examine efficiency-equity trade-offs. |
| Large workloads may exceed available compute resources. | Measure runtime, evaluate Spark configurations, and document scaling limitations. |
| Deployment may omit required files or expose sensitive information. | Validate published outputs, exclude raw records and secrets, and test the deployed dashboard. |
| Historical experiment results may be inconsistent or difficult to reproduce. | Record configurations, input versions, timestamps, outputs, and evaluation metrics systematically. |

## 7. Expected Outcome

The expected deliverable is a reproducible research prototype demonstrating an end-to-end public-health analytics workflow, from data ingestion and validation through outbreak detection, forecasting, resource-planning demonstrations, and dashboard visualization.

The final submission should document the implementation, evaluation evidence, design trade-offs, privacy considerations, ethical implications, limitations, and future improvements. EpiScope should be treated as an educational analytics prototype until its methods have been validated using representative, authorized real-world data and reviewed by relevant public-health experts.
