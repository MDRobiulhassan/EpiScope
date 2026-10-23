# Requirement Traceability

This table maps assignment requirements to implementation and evidence. Run the Colab notebook before recording measured results.

| ID | Implementation | Evidence/output |
|---|---|---|
| ING-1 | `generator/generate_encounters.py` | encounter CSV, facility registry, separate outbreak truth |
| ING-2 | `pipeline/`, `analytics/` | PySpark transformations |
| ING-3 | `pipeline/bronze.py`, `pipeline/gold.py` | Parquet outputs |
| ING-4 | `scripts/run_pipeline.py` | repeated-run demonstration; incremental drop still requires dedicated input plumbing |
| DQ-1 | `pipeline/silver.py` | 15 validation rules and quarantine output |
| DQ-2 | `pipeline/silver.py` | Silver quality report |
| DQ-3 | `pipeline/bronze.py` | ingestion metadata; batch lineage should be extended before final submission |
| PRV-1 | `pipeline/silver.py`, `.env.example` | salted `patient_id_hash`; raw ID removed from clean output |
| PRV-2 | `serving/build_public_data.py` | counts 1-4 suppressed |
| AN-1/AN-2 | `analytics/detection/` | detector metrics and `detection_threshold_tradeoff` |
| AN-4/AN-5 | `analytics/forecast/` | forecasts, interval fields, rolling backtest output |
| AN-7/AN-8 | `analytics/optimise/` | PuLP allocation and `equity_budget_curve` |
| AN-9 | `analytics/calendar/` | preparedness calendar |
| VIS-1/2/3 | `dashboard/` | D3 dashboard, filters, chart panels, what-if controls |
| VIS-4 | `serving/export_dashboard_data.py` | dashboard payload-size check in Colab notebook |
| ENG-1 | `scripts/run_pipeline.py`, `scripts/EpiScope_Colab_Run.ipynb` | documented execution sequence |
| ENG-2 | Colab notebook scale cell | runtime and output-size records |
| ENG-4 | `tests/` | validation, generator-contract, hashing, and suppression tests |

## Final handover checklist

- Replace the video URL placeholder in `README.md`.
- Fill group number, member names, IDs, repository URL, and video URL in `docs/episcope_ieee_report.tex`.
- Export the report PDF into `docs/`.
- Complete and sign the contribution matrix and individual reflections.
- Add the accessible video link and timestamps.
- Run the Colab notebook and retain raw timing and evaluation outputs.
- Implement and demonstrate the instructor's hidden incremental drop before claiming ING-4 compliance.
- Create the final `v1.0` tag only after the report, dashboard, and results match the code.
