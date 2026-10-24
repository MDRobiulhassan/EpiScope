# EpiScope Presentation Script (Three Speakers)

**Target duration:** about 15 minutes, plus a short live dashboard/Colab view if needed. The script gives each member approximately five minutes. Rehearse once and shorten pauses before cutting one member's section.

The slides are in [`presentation.html`](presentation.html). Use the sections below by slide number. Keep the incremental-feed wording conditional until the new Colab cells have actually been run and their output captured.

## Speaker 1 — Robiul Hassan (Slides 1–4, about 5 minutes)

### Slide 1 — EpiScope

“Hello. We are presenting EpiScope, our Big Data Analytics project for CSE 4345. I’m Robiul Hassan, and with me are Md Samin Osman and Md Mahafujul Alam. EpiScope is a research prototype for organizing synthetic disease-surveillance data, identifying possible outbreak signals, producing short-term forecasts, and presenting planning outputs in a dashboard. The data are synthetic, so the results show how the workflow behaves; they do not demonstrate performance on real patient or government surveillance records.”

### Slide 2 — The problem

“The project brief describes a practical challenge: health, climate, and supply data may arrive in different formats and at different times. Analysts need a way to check the data, identify unusual patterns, estimate near-term demand, and communicate useful summaries to national and district users. The engineering task is to connect those steps in a reproducible pipeline. The project also has to balance early detection against false alerts, useful geographic detail against privacy, and detailed processing against the compute available in a student environment.”

### Slide 3 — Pipeline architecture

“The main batch path starts with generated encounter records. Bronze stores the ingested records in Parquet and adds source and ingestion metadata. Silver applies validation rules, hashes patient identifiers for clean output, and separates invalid rows into quarantine. Gold aggregates clean encounters into district and disease summaries used by the analytics modules. Detection, forecasting, resource allocation, and calendar generation then produce outputs for serving. Public data is prepared and exported to JSON before the D3.js dashboard reads it. Keeping these stages separate makes it easier to identify where a result came from. It does not automatically prove every rule or analysis is correct, so the report keeps the limits visible.”

“The encounter generator creates a large synthetic batch and also creates the facility registry and a separate outbreak-label file. The label file is for evaluation; a detector should not use the ground-truth label as an input feature. Silver currently declares fifteen checks, including date ranges, disease-code consistency, duplicate encounter IDs, and facility membership. Rows may fail more than one check, which is why per-rule counts do not add up to the number of unique quarantined rows. We use Parquet between stages so the Spark pipeline can read columnar outputs, while the public browser gets smaller JSON files.”

### Slide 4 — Incremental inventory feed

“The assignment also describes facility stock and bed occupancy as a daily incremental source. We added a separate synthetic snapshot generator and pipeline for that input. It creates one row per facility for one snapshot date, then writes the input to its own Bronze path. Silver checks the date, facility fields, stock values, and bed capacity. Gold summarizes stock and occupancy by district and date. The idempotency key is the combination of snapshot date and facility ID. When the same daily file is processed again, existing keys should be skipped. This is a separate demonstration; it does not overwrite the batch encounter input and it is not currently used by the resource optimizer. We’ll show the actual two-pass output from Colab here.”

“The sample registry contains six hundred synthetic facilities, so the first run on an empty inventory Bronze folder should add six hundred records. If this folder already contains the same date, the first run can add fewer or zero; we should explain the exact observed output rather than force a number. The important replay check is that the second pass adds zero rows and the Bronze row count does not grow. We also rebuild Silver and Gold from Bronze after each pass, so the downstream snapshot remains available. This example is first-write-wins: if a facility reports a correction for the same date later, this version skips it. Supporting corrections would require a merge or revision policy.”

**Live view cue:** show the first `pipeline/inventory.py` output and the replay output. Point out `Rows appended this run` and use the actual values shown by Colab.

## Speaker 2 — Md Samin Osman (Slides 5–6, about 5 minutes)

### Slide 5 — Evaluation results

“This slide summarizes the latest recorded evaluation values in the project documentation. The detection evaluation reports sensitivity of 52.92 percent, false-positive rate of 4.37 percent, and precision of 0.74 percent. The low precision means false alerts greatly outnumber true alerts in this synthetic evaluation. That matters because a real team could face a large review burden. We should show sensitivity and precision together instead of presenting the detector as simply successful because it finds some positive cases. The forecast uses a seven-day average repeated across a fixed 28-day horizon. Its latest saved evaluation reports MAE 2.0182 and RMSE 2.6986 over 8,960 observations. These are historical saved results from synthetic data, not results from a newly rerun evaluation today. They do not establish that the forecast beats a seasonal baseline or works on real outbreaks.”

“The saved confusion counts are 190 true positives, 25,336 false positives, 169 false negatives, and 554,145 true negatives. That makes the precision result easier to interpret: most observations that the detector flagged were not labeled as outbreak positives in this evaluation. Sensitivity also matters because about half of the positive observations were detected. These measurements use district–disease–day observations with at least fourteen baseline days. The dataset is synthetic, and choices in how labels and evaluation units are constructed affect the numbers. The results should guide tuning and further checks, not be presented as field performance.”

“For forecasting, MAE summarizes typical absolute error, while RMSE weighs larger errors more heavily. We report both because one number alone can hide large misses. The fixed forecast repeats a pre-test seven-day average for the whole four-week horizon, so it does not adapt daily. We have not shown that it beats a seasonal-naïve alternative. There are older forecast metrics in the project history that differ from the latest saved values; the report flags that discrepancy instead of combining the two.”

### Slide 6 — Planning outputs and trade-offs

“The project also generates resource-allocation and preparedness-calendar outputs. The allocation stage uses forecast demand and an illustrative resource budget with a minimum allocation per district. These assumptions make the optimization visible and reproducible, but they are not a substitute for current inventory, transport, staffing, or local policy. The new daily inventory input creates a useful district-level stock and occupancy summary, but the optimizer does not consume that summary yet. That boundary matters: we should not imply that the current recommendations use live or updated stock. Our next improvement would connect validated inventory snapshots to the allocation logic, then compare efficiency and minimum district coverage across budget settings. Until then, these outputs are planning demonstrations that require human review.”

“The code reports allocated units, a population-proportional comparison, and unmet demand under the fixed illustrative budget. The equity-curve output varies the budget so a reviewer can consider how broader coverage changes as more units become available. These are useful ways to expose assumptions, but they do not validate that the chosen objective matches health priorities. The calendar is also a planning prompt generated from the project’s synthetic analytical outputs. If a district officer were using a real system, the stock snapshot would need timestamps, source checks, missing-feed handling, and clear treatment of stale reports. Our current demonstration only proves a small, deterministic daily feed can pass through the layered storage path after it is run in Colab.”

## Speaker 3 — Md Mahafujul Alam (Slides 7–10, about 5 minutes)

### Slide 7 — Dashboard

“The dashboard is the presentation layer for cases, alerts, forecasts, resources, and preparedness timing. It uses D3.js and reads exported JSON files, which keeps the browser view separate from the Spark processing. The interface is intended to help users move from an overall view to a district or disease view and inspect different analytical outputs. In the recorded notebook, the JSON payload check reports a total below the documented ten-megabyte limit. During the video, we should show the dashboard itself and demonstrate the filters and coordinated views that are implemented. We should avoid implying the dashboard is connected to a continuously updating service: it displays the exported files, so new pipeline results must be exported before they appear.”

“During the recording, filter cases by disease or district, inspect alerts, then show forecasts, resources, and the calendar. Demonstrate only controls that actually respond. The payload check is a size check, not a user study, and new results appear only after the export is rerun.”

### Slide 8 — Privacy and limitations

“The encounter data and outbreak labels are synthetic. Raw patient identifiers are hashed before the clean Silver output and are removed from that clean dataset; Bronze and quarantine outputs still contain identifiers and should remain restricted. Public case counts from one to four are suppressed by the serving logic. That reduces direct disclosure of small counts, but it is not a formal privacy guarantee: related totals or views could still reveal information. The analytics also have real limitations. The detector's recorded precision is very low, the forecast is a simple fixed baseline, and the inventory feed is synthetic and not connected to the optimizer. These are reasons to keep human review and further validation in the workflow.”

“The temperature and rainfall-like fields are synthetic, not weather-station observations. Raw patient IDs remain in restricted Bronze and quarantine data. Small-count suppression also cannot rule out inference from linked totals and views, so we describe it as a risk reduction rather than a guarantee of anonymity.”

### Slide 9 — Proposed team split

“We divided the speaking sections so each member has close to the same time. Robiul covers the core architecture and incremental pipeline. Samin explains evaluation and planning logic. I cover the dashboard, privacy, limitations, and recommendations. The project-role split shown here is a draft to help organize the handover. Our signed contribution matrix must reflect actual work completed and agreed percentages, rather than assuming that the presentation split is the same as the project contribution split.”

“Our unsigned draft puts Robiul as the lead for the core pipeline, Samin on evaluation review, and Mahafujul on dashboard and presentation preparation. A 60/20/20 share is only a proposal based on Robiul's description; the team must agree on actual contributions and sign the final matrix. We have balanced speaking time even though project effort was not equal.”

### Slide 10 — Conclusion

“EpiScope demonstrates a connected data workflow, from synthetic input and data-quality processing to analytics and a public-facing dashboard. The incremental inventory path extends that workflow with a replayable daily input and separate Bronze, Silver, and Gold outputs. The current evidence supports continued validation and demonstration, not operational deployment. Before such use, the system would need authorized representative data, stronger alert performance, validated forecasts, integration with real stock and capacity sources, and review by public-health specialists. Thank you.”

“Next, we’ll capture the incremental replay in Colab, align the report and slides with the actual outputs, finish the policy brief and signed matrix, and add an accessible video link. A future version should accept authorized inventory data and connect it to allocation after expert review. This concludes our presentation. Thank you; we’re ready for questions.”

## Before recording

1. Run the Colab incremental section and replace the live-view cue with the actual console output.
2. Confirm the dashboard and final JSON files correspond to the code/results being presented.
3. Add the final video URL to the README and report after upload, and test that it opens without sign-in.
4. Keep speaker times close to one another and ensure each member explains their own assigned section in their own words.
