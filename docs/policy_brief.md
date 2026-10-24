# EpiScope: Turning Disease Surveillance Data into Earlier, Better-Prepared Responses

**Policy Brief**

**Audience:** District health officials, public-health planners, and emergency-preparedness teams

**Prepared by:** Md. Samin Osman (0222220005101042), Robiul Hassan (0222220005101043), Walid Talal (0222220005101045), and Md. Mahafujul Alam (0222220005101066)

**Purpose:** Explain how EpiScope could support surveillance and preparedness, what its current experiments demonstrate, and what must happen before operational use.

## The Policy Problem

Public-health teams need to identify unusual disease activity early enough to investigate it and prepare staff, supplies, and services. However, surveillance data can be delayed, inconsistent, difficult to combine, or hard to translate into practical decisions. A dashboard alone does not solve these problems. Effective surveillance support also requires a repeatable data pipeline, interpretable signals, evaluated forecasts, and a clear process for validating and acting on results.

EpiScope is a prototype analytics pipeline designed to explore this workflow. It processes synthetic encounter records through Bronze, Silver, and Gold stages, applies data-quality checks, generates district–disease–day outbreak signals, produces short-term forecasts, and prepares resource-allocation and preparedness-calendar outputs. A browser dashboard presents selected results for review.

The project also includes a separate synthetic daily facility stock and bed-occupancy feed. It demonstrates incremental Bronze–Silver–Gold processing with replay protection, but it is not currently connected to the resource optimizer and does not represent live facility inventory.

**Policy message:** EpiScope is a prototype for testing surveillance and preparedness workflows, not a validated clinical or public-health warning system. Its outputs should be reviewed alongside local evidence and expert judgment.

## What EpiScope Provides

- **Structured data processing:** Bronze, Silver, and Gold layers separate ingestion, cleaning, and analytical outputs, making the workflow easier to inspect and reproduce.
- **Data-quality controls:** The Silver stage validates records and separates records that fail implemented checks for further review.
- **Outbreak signals:** The detector identifies district–disease–day observations that meet its alerting criteria.
- **Forecasting:** A seven-day-average baseline generates predictions for evaluation over a fixed 28-day horizon.
- **Preparedness support:** Resource-allocation and calendar outputs demonstrate how analytical results might inform planning activities.
- **Privacy-aware publication:** The documented serving policy suppresses exact case counts from 1 to 4, keeps zero counts visible, and publishes counts of 5 or more.

## What the Current Evaluation Shows

The latest saved evaluation outputs report the following results.

| Measure | Latest result | Policy interpretation |
|---|---:|---|
| Detection sensitivity | 52.92% | Approximately half of evaluated positive observations were detected. |
| Detection precision | 0.74% | Most generated alerts were false positives in the evaluated dataset. |
| False-positive rate | 4.37% | Approximately 4.37% of evaluated negative observations were flagged. |
| Forecast MAE | 2.0182 cases | Average absolute prediction error was approximately 2.02 cases per evaluated observation. |
| Forecast RMSE | 2.6986 cases | Larger prediction errors receive greater weight, producing an error measure of approximately 2.70 cases. |

The detection evaluation uses district–disease–day observations with at least 14 baseline days. The forecast evaluation covers 8,960 observations from December 4–31, 2025. Forecasting uses a simple baseline that repeats a seven-day average across the 28-day horizon; it does not update its predictions daily.

These results require caution. Detection precision of 0.74% indicates that the current detector would create a substantial review burden if every alert were sent directly to field teams. Sensitivity of 52.92% also indicates that many positive observations were missed. Neither result supports autonomous decisions.

Earlier documented metrics differ from the latest saved evaluation outputs and have not been reconciled. The results presented here therefore reflect the latest saved evaluation files, not independently verified performance on real surveillance data.

## Recommended Policy and Operational Approach

**1. Introduce human review before escalation.**

Treat alerts as prompts for investigation, not confirmed outbreaks. A trained surveillance officer should review recent counts, reporting completeness, local context, and possible data errors before escalating a signal.

**2. Improve alert quality before expanding use.**

Evaluate alternative thresholds and baseline methods using a held-out test period. Report sensitivity, precision, false-positive rate, and alert volume together. Work with district health teams to define an acceptable review workload before selecting an alert threshold.

**3. Validate forecasts against practical alternatives.**

Compare the current seven-day-average method with simple alternatives, including a seasonal-naïve baseline where appropriate. Evaluate errors by disease, district, and time period, and document where predictions perform poorly. Aggregate error values should not be assumed to represent every locality equally well.

**4. Link analytical outputs to feasible preparedness actions.**

Use resource-allocation and calendar outputs as planning aids rather than authoritative instructions. Check proposed allocations against current staffing, stock levels, service capacity, transport, and local protocols. The current experiments do not establish that these recommendations improve health outcomes.

**5. Protect privacy in published information.**

Keep encounter-level identifiers and internal labels out of public exports. Continue testing suppression at boundary values and assess whether totals, overlapping dates, district breakdowns, alerts, or related outputs could reveal suppressed counts indirectly. Small-count suppression reduces some disclosure risks but does not guarantee anonymity.

**6. Establish governance before live deployment.**

Assign responsibility for data quality, alert review, escalation, access control, audit logs, model monitoring, and incident response. Any real-world use requires appropriate authorization, secure infrastructure, data-protection review, and validation using representative, authorized real data.

## Limitations and Conditions for Use

EpiScope's synthetic data support controlled pipeline testing but cannot establish real-world detection accuracy, forecast usefulness, or public-health impact. Results may change substantially with actual reporting delays, missing records, disease prevalence, local seasonality, and data-quality problems. The current detection precision is particularly low and must be investigated before operational alerting is considered.

Some documented data-quality and performance figures are historical measurements that have not all been recomputed from raw logs. Runtime claims should identify the included stages and the environment in which they were measured.

The small-count suppression policy has undergone a documented boundary-rule check, but that test alone does not establish end-to-end protection against disclosure. Broader testing of public exports and linked outputs remains necessary.

## Decision Requested

**Approve further validation, not operational deployment.**

The next phase should:

1. Reconcile historical and current experiment records.
2. Verify the implemented data-quality rules against the source code and tests.
3. Test public outputs for direct and indirect disclosure.
4. Evaluate detection and forecasting on authorized, representative data.
5. Work with public-health staff to define acceptable alert workload and escalation criteria.

Only after these checks should a limited, supervised pilot be considered.

*Evidence note: Reported metrics come from the latest saved EpiScope detection and forecast evaluation outputs. They describe the current experimental dataset and should not be interpreted as validated performance on real-world surveillance data.*
