# EpiScope Architecture

## Overview

EpiScope has two synthetic inputs: batch encounter records and a daily facility inventory/bed-occupancy snapshot. Apache Spark processes the inputs, Parquet stores the layered outputs, and D3.js v7 renders dashboard JSON exports.

## Logical Data Flow

```text
Batch encounter CSV                    Daily inventory CSV
         |                                      |
         v                                      v
Bronze encounter Parquet              Bronze inventory Parquet
         |                                      |
         v                                      v
Silver validation                    Silver validation
   /          \                         /          \\
Clean      Quarantine               Clean      Quarantine
   |                                      |
   v                                      v
Gold encounter aggregates          Gold district-day inventory
   |                                      |
   +-------------- Analytics ------------+
                         |
                         v
             Public-data preparation
             and small-count suppression
                         |
                         v
               Dashboard JSON export
                         |
                         v
                  D3.js dashboard
```

The inventory path is a separate incremental source. The resource-allocation optimizer does not consume these inventory aggregates; they demonstrate incremental ingestion and layered processing.

## Components

### Data generation

- `generator/generate_encounters.py` produces synthetic encounter rows and the facility registry.
- `generator/generate_inventory_drop.py` produces one synthetic daily stock and occupancy snapshot, defaulting to `2025-12-31`. It writes `data/incremental_drop/inventory_snapshot.csv` without replacing the batch encounter input.

### Encounter pipeline

- `pipeline/bronze.py` reads `data/bronze/encounters/encounters.csv` and writes Parquet to `data/bronze/encounters_parquet/`.
- `pipeline/silver.py` validates encounter rows, hashes patient IDs for clean output, and writes clean, quarantine, and quality-report data.
- `pipeline/gold.py` aggregates clean encounters for downstream analytics.

### Incremental inventory pipeline

`pipeline/inventory.py` reads the one-day CSV, appends unseen `(snapshot_date, facility_id)` keys to `data/bronze/inventory_snapshots/`, validates all stored snapshots into Silver clean/quarantine paths, and writes daily district stock and bed aggregates to Gold. Spark writes to local temporary folders first; completed outputs are copied to Drive and size-checked before replacing existing paths. Replaying the same date and facility keys appends zero rows. A corrected value for a key already present is treated as a replay, so late revisions/upserts are not supported.

### Analytics

- `analytics/detection/`: outbreak scoring and evaluation.
- `analytics/forecast/`: fixed-horizon forecast generation and evaluation.
- `analytics/optimise/`: illustrative resource-allocation logic and budget/equity outputs.
- `analytics/calendar/`: preparedness-calendar output.

These are prototype analytics over synthetic inputs. The current inventory-feed demonstration is not connected to the optimizer.

### Serving and visualization

- `serving/build_public_data.py` prepares public-facing data and applies the implemented small-count suppression.
- `serving/export_dashboard_data.py` writes the dashboard JSON payloads.
- `dashboard/index.html` and `dashboard/app.js` render the interactive D3.js dashboard.

## Storage and privacy

Encounter and inventory working data are stored separately from public dashboard JSON. Patient identifiers remain in restricted batch Bronze and encounter quarantine outputs; the clean encounter output uses a salted hash and drops the raw patient ID. Inventory snapshots contain no patient identifiers. Small-count suppression reduces direct exposure of low public counts but does not guarantee protection from inference across linked views.

## Colab execution

The Colab workflow is `scripts/EpiScope_Colab_Run.ipynb`. Its saved execution records the assignment-scale batch workflow and a successful two-pass inventory run. The inventory pipeline reports the number of appended rows on each pass; replaying the same keys appends zero rows.
