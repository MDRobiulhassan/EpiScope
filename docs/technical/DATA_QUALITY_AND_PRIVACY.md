# EpiScope Data Quality and Privacy Controls

## Silver-Layer Validation

The Silver pipeline, implemented in `pipeline/silver.py`, validates encounter records and separates accepted clean records from quarantined records.

The recorded 25-million-row run produced the following results:

| Measure | Result |
|---|---:|
| Input rows | 25,000,000 |
| Clean rows | 24,825,210 |
| Quarantined rows | 174,790 |
| Quarantine rate | Approximately 0.69916% |
| Reconciliation | Clean + quarantined = input |

The counts reconcile exactly:

\[
24{,}825{,}210 + 174{,}790 = 25{,}000{,}000
\]

These results demonstrate count reconciliation for the recorded run. They do not independently establish that every validation rule behaves correctly.

## Data-Quality Rules

The Silver pipeline is responsible for applying data-quality checks before records are passed to downstream processing. The rules below list their implemented conditions and failure behavior.

The source in `pipeline/silver.py` declares and applies the following 15 named checks.

| Rule | Implemented check |
|---|---|
| DQ01 | Missing encounter ID |
| DQ02 | Invalid encounter date |
| DQ03 | Encounter date outside 2021-2025 |
| DQ04 | Missing district |
| DQ05 | Disease outside the configured categories |
| DQ06 | Missing or out-of-range age (0-120) |
| DQ07 | Severity outside `mild`, `moderate`, `severe` |
| DQ08 | Missing or out-of-range temperature (-20 to 60) |
| DQ09 | Missing, negative, or over-1000 rainfall |
| DQ10 | Encounter ID occurs more than once |
| DQ11 | Encounter ID is non-positive |
| DQ12 | Missing disease or severity |
| DQ13 | Missing onset/report date or onset after report |
| DQ14 | Disease and ICD-10 code do not match configured pairs |
| DQ15 | Missing or unregistered facility ID |

The rule conditions can overlap: a record can fail multiple checks. The quality report's `failed_records` values count affected rows per rule, not unique quarantined rows, so adding rule counts can exceed the quarantine count.

The separate incremental inventory path applies date/key/district checks, nonnegative stock and bed values, positive bed capacity, and a check that occupied beds do not exceed capacity. These checks are implemented in `pipeline/inventory.py`, and the Colab workflow records a successful two-pass execution.

The validation rules may overlap: one record can fail multiple checks. Per-rule failure counts describe affected rows for each rule and are not additive unique quarantine totals.

## Privacy and Public-Data Suppression

`serving/build_public_data.py` prepares public-facing case data before it is exported for dashboard use.

The recorded check of `dashboard/data/cases.json` found no exact published case counts between 1 and 4. The intended suppression policy hides exact counts in this range.

Suppression behavior must remain consistent across public-facing outputs. A suppressed value should not be exposed through an alternative field or be trivially recoverable from linked views, totals, or other published values.

Small-count suppression reduces one form of disclosure risk, but it does not guarantee complete privacy. Geographic and temporal combinations, linked dashboard views, repeated queries, and aggregate totals can create additional disclosure risks.

## Provenance and Data Minimization

EpiScope uses synthetic data in its recorded experiments. Synthetic records must remain clearly identified as synthetic and must not be represented as real patient or surveillance records.

The public-serving layer should:

- Exclude unnecessary record-level identifiers.
- Retain only fields required for the intended public-facing purpose.
- Apply aggregation and suppression before publication.
- Keep internal analytical datasets separate from public dashboard exports.
- Document transformations and privacy controls applied to published fields.

Count suppression alone does not establish compliance with any legal or regulatory privacy framework.

## Validation and Regression Testing

Data-quality and privacy controls should be tested whenever validation logic, data transformations, or dashboard exports change.

Important checks include:

- Confirming that clean and quarantined row counts reconcile with the input.
- Testing distinct implemented quality rules against valid and invalid examples.
- Checking nulls, invalid values, and duplicates where applicable.
- Testing suppression at counts of 1, 2, 3, and 4.
- Testing the threshold boundary at a count of 5.
- Searching all public JSON datasets for unintended exact small counts.
- Confirming that dashboard changes do not bypass public-data preparation.

A passing boundary check is useful evidence, but it is only one part of data-quality and privacy assurance. The checks above describe the validation coverage expected for these data paths.
