# Data Quality and Privacy Controls

## Silver-layer validation

The Silver pipeline is implemented in `pipeline/silver.py`. It separates accepted clean records from quarantined records.

The recorded 25-million-row run produced:

| Measure | Result |
|---|---:|
| Input rows | 25,000,000 |
| Clean rows | 24,825,210 |
| Quarantined rows | 174,790 |
| Quarantine rate | 0.69916% approximately |
| Reconciliation | Clean + quarantined = input |

The recorded run reconciled exactly. This does not, by itself, prove that every validation rule is correct.

## Quality-rule inventory

The assignment requires at least 12 data-quality rules. For submission, create a precise inventory directly from the implementation in `pipeline/silver.py`. Do not count multiple descriptions of the same rule as separate rules.

Use this format:

| ID | Rule | Field(s) | Failure behavior | Test/evidence |
|---|---|---|---|---|
| Q01 | Copy exact implemented rule | Actual field | Reject, quarantine, repair, or other implemented behavior | Test or recorded result |
| Q02–Q12+ | Add each distinct implemented rule | Actual field(s) | Actual behavior | Evidence |

Verify at least the applicable categories: required values, type/format validity, date validity, permitted categories, numeric ranges, identifier consistency, duplicate handling, and cross-field constraints. These are categories to check, not claims that every one is already implemented.

Document how rules are applied, whether a row can fail multiple rules, and whether the reported counts represent rows or individual rule violations.

## Privacy and public-data suppression

`serving/build_public_data.py` is responsible for preparing public-facing data. The recorded check of `dashboard/data/cases.json` found no exact published case counts between 1 and 4.

The intended policy is to suppress small counts from 1 through 4. Verify how suppression is represented in the JSON, whether suppressed values can be reconstructed from other fields or views, and whether the same rule is applied consistently across all public outputs.

A single small-count check is not a complete privacy audit. Review geographic and temporal combinations, linked dashboard views, totals, and repeated queries for possible disclosure.

## Provenance and data minimization

- Keep synthetic data clearly identified as synthetic.
- Do not expose unnecessary record-level identifiers in public JSON.
- Document which fields are retained, aggregated, suppressed, or excluded.
- Separate internal analytical data from public-serving exports.
- Do not claim legal or regulatory compliance based only on count suppression.

## Revalidation checklist

- [ ] Inventory at least 12 distinct implemented rules.
- [ ] Verify clean and quarantine reconciliation.
- [ ] Inspect nulls, invalid values, and duplicates as applicable.
- [ ] Test small counts 1, 2, 3, and 4.
- [ ] Test a count of 5 to verify the intended threshold boundary.
- [ ] Search all public JSON outputs for unintended exact small counts.
- [ ] Confirm dashboard changes do not bypass public-data preparation.
