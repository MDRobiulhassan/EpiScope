# EpiScope Presentation Script - Four Members

**Target:** 14-15 minutes including the Colab and dashboard demonstrations. Slides are in [presentation.html](presentation.html), with a PowerPoint export at [presentation.pptx](presentation.pptx).

The saved evaluation values below are read from the repository's current evaluation artifacts. Dashboard counts describe the saved JSON snapshot; the five files have differing modification times, so the counts do not represent a single synchronized export run.

## Robiul Hassan - Slides 1-4 (about 4 minutes)

### Slide 1 - Opening

“Hello. We are presenting EpiScope, our Big Data Analytics project. I’m Robiul Hassan, and my teammates are Md. Samin Osman, Walid Talal, and Md. Mahafujul Alam. EpiScope demonstrates a data workflow for synthetic disease surveillance. It takes encounter records through validation and aggregation, then produces analytical outputs and a dashboard. These are synthetic records, so our results do not establish how the system would perform with real patients or public-health data.”

### Slide 2 - System design

“The main batch path begins with a generated encounter CSV. Bronze ingests the source and records lineage. Silver applies validation rules, separates clean records from quarantine, and hashes patient identifiers in the clean output. Gold creates district and disease aggregates. Analytics use those aggregates for outbreak detection, forecasting, resource allocation, and preparedness-calendar outputs. Serving prepares selected data for the browser dashboard.

“There is also a separate daily facility inventory path for stock and bed occupancy. It has its own Bronze, Silver, and Gold outputs. It does not replace the encounter input, and the optimizer does not use its inventory totals.”

### Slide 3 - Data quality

“The documented large-scale run processed 25 million encounter rows. The Silver output retained 24,825,210 rows and quarantined 174,790. Those numbers reconcile to the input, with a quarantine rate of about 0.70 percent. Silver implements named checks for dates, required fields, codes, duplicates, measurements, and facility membership.

“A row can fail more than one check, so rule counts can overlap. This is evidence of row accounting for that run, not proof that every rule is correct. We should use final Colab output if it differs from these saved historical values.”

### Slide 4 - Incremental input and Colab cue

“The incremental example generates one synthetic stock snapshot per facility. The key is snapshot date plus facility ID. Bronze appends unseen keys; Silver validates the records; Gold aggregates stock and occupancy by district and date. Replaying the same snapshot should append zero new keys.

“I’ll show the actual Colab output now. We’ll read the observed first-run and replay counts from the screen. We should not claim an expected first-run count if the folder already contained some keys. This uses first-write-wins behavior, so corrections to an existing date and facility are not merged. The optimizer also does not use this inventory feed.”

**Demo cue:** Show the generation cell, first pipeline output, and replay output. Point to the actual “Rows appended this run” values. Do not substitute expected counts for the saved run output.

## Md. Samin Osman - Slides 5-6 (about 4 minutes)

### Slide 5 - Detection results

“The latest saved detection evaluation reports sensitivity of 52.92 percent, false-positive rate of 4.37 percent, and precision of 0.74 percent. There were 190 true positives, 25,336 false positives, 169 false negatives, and 554,145 true negatives. The evaluation unit is a district, disease, and day with at least fourteen baseline days.

“The detector finds about half of labelled positives, but its precision is very low: false alerts greatly outnumber true alerts. If every alert were escalated, that would create substantial review work. These are experimental signals, not confirmed outbreaks, and need human review and further threshold evaluation before any operational pilot.”

### Slide 6 - Forecast and planning

“The saved forecast evaluation contains 8,960 observations for December 4 through 31, 2025. The model repeats a seven-day average across a fixed 28-day horizon; it does not update its prediction each day. The reported mean absolute error is 2.0182 cases and root mean squared error is 2.6986 cases. These are results on synthetic data, and we have not shown that this baseline outperforms a seasonal-naive alternative.

“The project also produces an illustrative allocation across 64 districts under a 100-unit budget, plus a preparedness calendar. The optimizer uses forecast demand and a minimum district share. It does not consume the new inventory feed. These outputs demonstrate planning logic; they do not validate staffing or stock decisions or show improved health outcomes.”

## Md. Mahafujul Alam - Slide 7 (about 3 minutes)

### Slide 7 - Dashboard

“The dashboard reads exported JSON files rather than querying Spark directly. The local files currently contain 36,000 weekly case rows, 17,063 alert rows, 8,960 forecasts, 64 resource allocations, and 3,840 preparedness-calendar rows. Their combined payload is 9.81 MiB, below the notebook’s 10 MiB check. Their timestamps differ, so these figures describe a mixed saved snapshot rather than one synchronized export.

“I’ll select a district and disease and show how the case, alert, and forecast views respond. The z-score control filters alerts. The budget and equity controls recalculate the allocation scenario. These are static JSON exports: the browser does not rerun Spark, and the filters do not change the source data.”

**Dashboard cue:** Demonstrate one district/disease selection, a higher alert threshold, and a changed budget/equity floor.

## Walid Talal - Slides 8-9 (about 3 minutes)

### Slide 8 - Privacy and limitations

“The system uses synthetic encounter records, facility values, and outbreak labels. The clean Silver output uses a salted patient hash, while raw identifiers remain in restricted internal outputs. The public weekly case export suppresses counts from one to four. This reduces direct exposure of small counts, but it is not a formal privacy guarantee; linked totals and views can still create inference risk.

“Other limits include the detector’s low precision, the simple fixed forecast, the separate inventory path, and unresolved differences between historical results. The temperature and rainfall-like fields are synthetic too. EpiScope is an educational research prototype and should not direct care or public-health operations.”

### Slide 9 - Conclusion

“EpiScope demonstrates an inspectable workflow from synthetic input through quality checks and analytics to dashboard exports. Its current evidence supports continued validation, not operational deployment. The low alert precision, simple forecast baseline, and separate inventory path define important limits on how these outputs should be interpreted. Thank you.”
