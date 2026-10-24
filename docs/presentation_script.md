# EpiScope Presentation Script

**Target:** about 15 minutes total. Robiul speaks for about 4 minutes, Samin for about 5 minutes, and Mahafujul for about 5 minutes. Allow about one minute for Robiul's Colab demonstration. The slides are in [presentation.html](presentation.html).

The slides use saved evaluation values and the current local dashboard JSON summary. The dashboard files do not all have the same modification time, so do not describe the dashboard counts as one synchronized run until the five exports are regenerated together.

## Robiul Hassan — Slides 1–4

### Slide 1 — Opening

“Hello. We are presenting EpiScope, our Big Data Analytics project. I’m Robiul Hassan, with Md Samin Osman and Md Mahafujul Alam. EpiScope demonstrates a data workflow for synthetic disease surveillance. It takes encounter records through validation and aggregation, then produces analytical outputs and a dashboard. Our goal is to show the engineering process and its limits. These are synthetic records, so our results do not establish how the system would perform with real patients or public-health data.”

### Slide 2 — System design

“The main batch path begins with a generated encounter CSV. Bronze ingests the source and records lineage. Silver applies validation rules, separates clean records from quarantine, and hashes patient identifiers in the clean output. Gold creates district and disease aggregates. The analytics stages use those aggregates for outbreak detection, forecasting, resource allocation, and preparedness-calendar outputs. Serving prepares selected data for the browser dashboard.

“We also added a separate daily facility inventory path for stock and bed occupancy. It has its own Bronze, Silver, and Gold outputs. It does not replace the encounter input, and the optimizer does not use its inventory totals. Keeping these two paths separate helps us show what has actually been integrated.”

### Slide 3 — Data quality

“The documented large-scale run processed 25 million encounter rows. The documented Silver output retained 24,825,210 rows and quarantined 174,790. Those numbers reconcile to the input, with a quarantine rate of about 0.70 percent. The Silver implementation contains fifteen named checks covering dates, required fields, codes, duplicates, measurements, and facility membership.

“One caution: a row can fail more than one check, so individual rule counts can overlap. Row reconciliation confirms accounting for that run; it does not prove each rule is correct. We should use the actual final Colab output if it differs from the historical values shown here.”

### Slide 4 — Incremental input and live cue

“The incremental example generates one synthetic stock snapshot per facility. The key is the snapshot date together with the facility ID. Bronze appends unseen keys; Silver validates the records; Gold aggregates stock and occupancy by district and date. Replaying the same snapshot should append zero new keys.

“I’ll show the actual Colab output now. We should read the observed first-run and replay counts from the screen. We should not claim the expected first-run count if the folder already had some of those keys. This version uses first-write-wins behavior, so it does not merge corrections to an existing date and facility. The inventory feed is also not used by the optimizer.”

**Demo cue:** Show the generation cell, first pipeline output, and replay output. Point to the actual “Rows appended this run” values. Robiul’s section should end after the demo.

## Md Samin Osman — Slides 5–6

### Slide 5 — Detection results

“The latest saved detection evaluation reports sensitivity of 52.92 percent, a false-positive rate of 4.37 percent, and precision of 0.74 percent. The confusion counts are 190 true positives, 25,336 false positives, 169 false negatives, and 554,145 true negatives. The evaluation unit is a district, disease, and day with at least fourteen baseline days.

“These metrics need to be read together. The detector finds about half of the labelled positive observations, but its precision is very low: false alerts greatly outnumber true alerts. That would create a substantial review workload if every alert were escalated. The alerts are experimental signals, not confirmed outbreaks. They need human review and further threshold and baseline evaluation before anyone considers an operational pilot.”

“The confusion counts explain the precision result. Precision is true positives divided by all predicted positives: 190 divided by 190 plus 25,336. Sensitivity is true positives divided by all labelled positives: 190 divided by 190 plus 169. The false-positive rate uses the 25,336 false positives against all 579,481 labelled negatives. This also shows why a low false-positive rate alone can be misleading when the dataset contains many more negative than positive observations. We should report alert volume and precision alongside sensitivity.”

### Slide 6 — Forecast and planning

“The saved forecast evaluation contains 8,960 observations for December 4 through 31, 2025. The model repeats a seven-day average across a fixed 28-day horizon. It does not update its prediction each day. The reported mean absolute error is 2.0182 cases, and the root mean squared error is 2.6986 cases.

“These values describe the saved synthetic evaluation only. Earlier documentation contains different forecast metrics, and the discrepancy has not been resolved. We have not shown that this baseline outperforms a seasonal-naïve alternative.

“The project also produces an illustrative allocation across 64 districts under a 100-unit budget, plus a preparedness calendar. The optimizer uses forecast demand and a minimum district share. It does not consume the new inventory feed. These outputs demonstrate how planning logic can be connected to the pipeline; they do not validate staffing or stock decisions or show improved health outcomes.”

“The MAE and RMSE are both measured in cases, but RMSE gives more weight to larger errors. The model's repeated average is intentionally simple, so these values should be compared with alternatives before making claims about forecast quality. The planning stage has its own assumptions: a fixed illustrative budget, forecast-based demand, and a minimum district share. In a real planning system, the input would also need current stock, staff capacity, transport, reporting gaps, and local priorities.”

## Md Mahafujul Alam — Slides 7–9

### Slide 7 — Dashboard

“The dashboard reads exported JSON files rather than querying Spark directly. The local files currently contain 36,000 weekly case rows, 17,063 alert rows, 8,960 forecasts, 64 resource allocations, and 3,840 preparedness-calendar rows. Their combined payload is 9.81 MiB, below the notebook’s 10 MiB check.

“These are counts from the files currently in the repository. The case and alert files have later modification times than the forecast, resource, and calendar files, so we have not confirmed that all five came from one export run. Before the final recording, we should regenerate the dashboard exports together and rerun the payload check. In the interface, district and disease filter the case, alert, and forecast views. The alert z-score threshold filters alerts; the budget and equity controls recalculate the allocation scenario.”

**Dashboard demo cue (about 2 minutes):**

1. Select one district and one disease. Point out that the case, alert, and forecast panels respond to those filters.
2. Raise the alert z-score threshold and show that fewer alerts remain in the table.
3. Change the budget and equity floor. Point to the allocation summary and bars; the budget controls the total units, while the equity floor increases the minimum equal-share portion before the remaining units follow forecast demand.
4. Explain that these charts use static JSON exports. The browser does not rerun Spark, and a district/disease filter does not change the source data.

### Slide 8 — Privacy and limitations

“The system uses synthetic encounter records, facility values, and outbreak labels. The clean Silver output uses a salted patient hash, while raw identifiers remain in restricted internal outputs. The public weekly case export suppresses counts from one to four. That reduces direct exposure of small counts, but it is not a formal privacy guarantee. Linked totals and overlapping views can still create inference risk.

“The detector’s low precision, the simple fixed forecast, the separate inventory path, and the unresolved differences between historical results are all important limitations. Temperature and rainfall-like fields are also synthetic. This project is an educational research prototype and should not be used to direct care or public-health operations.”

### Slide 9 — Conclusion

“EpiScope demonstrates a connected workflow from synthetic input to quality checks, analytics, and dashboard export. The strongest evidence is that the processing stages and separate inventory path are implemented and can be inspected. The saved metrics also show why analytical outputs need careful evaluation: the detector has a high false-alert burden, and the forecast is a simple baseline.

“Before submission, we still need to synchronize and capture the final dashboard exports, retain the actual incremental replay output, finish the report PDF and policy-brief layout, agree on and sign the contribution matrix, and add an accessible video link. Our conclusion is that EpiScope supports further validation, not operational deployment. Thank you.”

## Before recording

1. Regenerate the five dashboard JSON files together, then rerun the payload check.
2. Run the inventory snapshot and replay in Colab; replace expected language with the actual counts shown.
3. Confirm the evaluation values against the saved results you plan to submit.
4. Record each member’s section and keep speaking time close to the targets above. Include both the Colab and dashboard demonstrations in the total presentation time.
5. Add the report PDF, signed contribution matrix and reflections, and accessible video link before calling the handover complete.
