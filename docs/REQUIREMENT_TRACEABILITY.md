# Requirement Traceability and Handover

This is a project-side mapping to the assignment brief. A listed implementation path is not proof of a requirement; use run output, report evidence, and the rubric to confirm completion.

| Assignment area | Implementation | Evidence and current status |
|---|---|---|
| Batch synthetic encounters | `generator/generate_encounters.py` | Colab notebook records the 25-million-row batch run. The current project copy does not include the full generated dataset. |
| Bronze–Silver–Gold encounter processing | `pipeline/bronze.py`, `pipeline/silver.py`, `pipeline/gold.py` | Layered Spark processing; recorded row counts are historical project results and should be confirmed from the final Colab run before submission. |
| Incremental source feed | `generator/generate_inventory_drop.py`, `pipeline/inventory.py` | One-day facility stock/bed snapshot; Bronze is append-only by `(snapshot_date, facility_id)`, Silver validates/quarantines, Gold aggregates by district and date. Run twice in Colab; the replay should append zero rows. |
| Encounter data quality | `pipeline/silver.py` | Source currently implements 15 named checks. The printed quality report counts rule failures, which may overlap. Confirm behavior against current run output and tests before claiming all checks passed. |
| Inventory data quality | `pipeline/inventory.py` | Checks snapshot date, facility and district values, nonnegative stock and bed fields, positive capacity, and occupancy not exceeding capacity. |
| Privacy controls | `pipeline/silver.py`, `serving/build_public_data.py` | Salted patient hash in clean Silver output and small-count suppression in public case data. This is not a formal privacy guarantee. |
| Outbreak detection and evaluation | `analytics/detection/` | Saved evaluation metrics exist; latest documented precision is low (0.74%), so the detector is not suitable for unreviewed operational alerts. |
| Forecasting and evaluation | `analytics/forecast/` | Seven-day-average fixed 28-day baseline and saved evaluation. No claim of beating a seasonal-naive baseline. |
| Allocation and preparedness | `analytics/optimise/`, `analytics/calendar/` | Illustrative outputs. Current optimizer uses forecast demand and fixed assumptions; it does not consume the new inventory feed. |
| D3 dashboard and serving | `serving/`, `dashboard/` | Saved JSON exports contain 36,000 weekly case rows, 17,063 alerts, 8,960 forecast rows, 64 allocations, and 3,840 calendar rows; total payload is 9.81 MiB. File modification times differ, so regenerate all outputs together and capture a synchronized final snapshot. Record a fresh walkthrough for the final video. |
| Scalability and Spark experiments | `scripts/EpiScope_Colab_Run.ipynb`, `docs/EXPERIMENTS.md` | Notebook contains historical execution records. Capture fresh output and preserve run configuration if using the figures as submission evidence. |
| Report, policy brief, and video | `docs/episcope_ieee_report.tex`, `docs/policy_brief.md`, presentation files | Draft report and policy brief exist. Export the final report PDF, include the policy brief as a two-page appendix, and add an accessible video link. |

## Colab incremental-feed steps

The `One-day incremental inventory feed` section in `scripts/EpiScope_Colab_Run.ipynb` performs these steps without editing or replacing `pipeline/bronze.py`:

1. Generate `data/incremental_drop/inventory_snapshot.csv` for one snapshot date.
2. Run `pipeline/inventory.py` to append unseen facility/date keys and rebuild Silver and Gold inventory outputs.
3. Run the same pipeline again. It should append zero rows because the snapshot keys already exist.

The daily feed is synthetic. The first version uses first-write-wins behavior: corrected or late revisions to an existing facility/date key are not merged. This limitation must remain explicit in the presentation and report.

## Final handover checklist

- [ ] Confirm group number and any required cover-page details.
- [ ] Review `docs/episcope_ieee_report.tex`; export the final IEEE report PDF.
- [ ] Include `policy_brief.tex` as the two-page nontechnical policy-brief appendix when exporting the report; confirm the resulting PDF page count/layout.
- [ ] Add the signed contribution matrix and individual reflections to the report appendices.
- [ ] Review and sign `docs/CONTRIBUTION_MATRIX_DRAFT.md` only after the proposed roles and shares match actual work.
- [ ] Run the incremental section in Colab and retain its real console output. Confirm first ingestion adds the expected facilities and the replay adds zero.
- [ ] Replace the demo-video placeholder in `README.md` and the report with an accessible link; include video timestamps.
- [ ] Record a 15–20 minute presentation. Each member should explain their assigned section and appear in the video for at least the duration required by the brief.
- [ ] Regenerate the five dashboard JSON outputs together and verify the payload size and charts from that synchronized snapshot.
- [ ] Check that report, slides, video, and saved metrics describe the same code version and experiment.
- [ ] Create the required `v1.0` tag only after final materials are aligned.

## Suggested team division

The speaker assignments and proposed work areas are in `docs/TEAM_ROLES_AND_CONTRIBUTION_DRAFT.md`. Use the signed contribution matrix to report actual work and agreed shares; update the draft if it does not match what each person did.
