# EpiScope: Turning Disease Surveillance Data into Earlier, Better-Prepared Responses

**Policy brief | Audience:** District health officials, public-health planners, and emergency-preparedness teams  
**Purpose:** Explain how EpiScope could support surveillance and preparedness, what its current experiments show, and what must happen before operational use.

## The policy problem

Public-health teams need to identify unusual disease activity early enough to investigate it and prepare staff, supplies, and services. Yet surveillance data can be delayed, inconsistent, difficult to combine, or hard to translate into practical decisions. A dashboard alone does not solve these problems: officials need a repeatable data pipeline, interpretable signals, forecasts, and a clear process for validating and acting on them.

EpiScope is a prototype data-analytics pipeline designed to explore that workflow. It processes encounter-style data through Bronze, Silver, and Gold stages; applies data-quality checks; generates district- and disease-level outbreak signals; produces short-term forecasts; and prepares resource-allocation and preparedness-calendar outputs. A dashboard presents selected outputs to support review.

**Policy message:** EpiScope is a decision-support prototype for testing surveillance workflows—not a validated clinical or public-health warning system. Its outputs should be reviewed alongside local evidence and expert judgment.

## What EpiScope provides

- **A structured data pipeline:** Bronze, Silver, and Gold layers separate ingestion, cleaning, and analytical outputs, making processing easier to inspect and repeat.
- **Data-quality handling:** The Silver stage applies validation and separates records that fail checks for further review rather than silently treating all input as reliable.
- **Outbreak-signal generation:** The detector identifies district–disease–day observations that meet its alerting criteria.
- **Forecasting:** A simple seven-day-average baseline produces forecasts for evaluation over a fixed 28-day horizon.
- **Preparedness support:** Resource-allocation and preparedness-calendar outputs help demonstrate how analytical signals might be translated into planning tasks.
- **Privacy-aware public outputs:** Daily counts from 1 to 4 are suppressed in the public serving layer; zero counts remain visible, and counts of 5 or more are published.

## What the current evaluation shows

The latest saved evaluation outputs report the following results:

| Component | Latest reported result | Interpretation |
|---|---:|---|
| Outbreak detection sensitivity | 52.92% | Detected about half of evaluated positive district–disease–day observations. |
| Outbreak detection precision | 0.74% | Most generated alerts were false positives in the evaluated data. |
| False-positive rate | 4.37% | About 4.37% of evaluated negative observations were flagged. |
| Forecast MAE | 2.0182 | Mean absolute error was about 2.02 cases per evaluated observation, in the dataset’s count units. |
| Forecast RMSE | 2.6986 | Root mean squared error was about 2.70 cases per evaluated observation, penalizing larger errors more heavily. |

The detection evaluation is based on district–disease–day observations with at least 14 baseline days. The forecast evaluation reports 8,960 observations over the test dates 4–31 December 2025. The forecast is a simple baseline, not evidence that a more complex model would perform better.

These results require caution. Detection precision of 0.74% means the current detector would create a substantial review burden if every alert were sent directly to field teams. Sensitivity of 52.92% also means that many positive observations were missed. Neither metric supports autonomous decisions. Earlier documented metrics differ from the latest saved outputs and have not been reconciled; the figures in this brief therefore use the latest saved evaluation files.

## Recommended policy and operational approach

**1. Use a human-in-the-loop review process.** Treat alerts as prompts for verification, not confirmed outbreaks. A trained surveillance officer should review recent counts, reporting completeness, local context, and possible data errors before escalating a signal.

**2. Improve alert quality before expanding use.** Evaluate alternative thresholds and baseline methods using a held-out period. Report sensitivity, precision, false-positive rate, and alert volume together. Define an acceptable operational workload with district health teams before choosing a threshold.

**3. Validate forecasts against practical baselines.** Compare the current seven-day-average method with simple alternatives, including a seasonal-naïve baseline where appropriate. Evaluate performance by disease, district, and time period, and document where the model performs poorly. Do not assume aggregate error describes every locality equally well.

**4. Connect signals to feasible preparedness actions.** Use resource and calendar outputs as planning aids. Any proposed allocation should be checked against current staffing, stock levels, service capacity, transport, and local protocols. EpiScope does not establish that its recommendations improve health outcomes.

**5. Protect privacy in published data.** Keep encounter-level identifiers and internal labels out of public exports. Continue testing suppression at boundary values, and assess whether totals, overlapping dates, district breakdowns, alerts, or other related outputs could reveal suppressed small counts indirectly. Suppression is a risk-reduction measure, not a guarantee of anonymity.

**6. Establish governance before any live deployment.** Assign responsibility for data quality, alert review, escalation, access control, audit logs, model monitoring, and incident response. Any real-world use requires appropriate authorization, secure infrastructure, data-protection review, and validation with representative real data.

## Limitations and conditions for use

The project’s synthetic data enables controlled pipeline testing but cannot establish real-world detection accuracy, forecast usefulness, or public-health impact. Results may change substantially with actual reporting delays, missingness, disease prevalence, local seasonality, and data-quality problems. The reported detection precision is especially low and must be improved before operational alerting is considered.

Some documented data-quality and performance figures are historical measurements that have not all been recomputed from raw logs. Runtime claims should specify which stages are included and the environment in which they were measured. Small-count suppression has passed a boundary-rule test for counts 0 through 6, but that test alone does not prove end-to-end protection against disclosure.

## Decision requested

**Approve further validation, not operational deployment.** The next phase should reconcile experiment records, verify the implemented data-quality rules, test public outputs for indirect disclosure, and evaluate detection and forecasting on authorized, representative data. Public-health staff should help define acceptable alert workload and escalation criteria. Only after these checks should a limited, supervised pilot be considered.

*Evidence note: Metrics are taken from the latest saved EpiScope detection and forecast evaluation outputs. They describe the current experimental dataset and should not be interpreted as validated performance on real-world surveillance data.*
