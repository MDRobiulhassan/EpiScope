# EpiScope Data Dictionary and Provenance

## Purpose

This document describes EpiScope's datasets, their roles in the processing pipeline, and their provenance. Exact field names and data types must match the current source code, Spark schemas, and exported JSON files.

## Dataset Inventory

| Dataset | Location | Purpose |
|---|---|---|
| Source encounters | `data/bronze/encounters/encounters.csv` | Synthetic encounter-level input records |
| Bronze encounters | `data/bronze/encounters_parquet/` | Source records ingested and stored in Parquet format |
| Silver encounters | `data/silver/encounters/` | Validated and cleaned encounter records |
| Silver quarantine | `data/silver/` | Records that fail validation, stored separately according to the pipeline configuration |
| Gold outputs | `data/gold/` | Aggregated analytical datasets used by downstream processing |
| Public case data | `data/public/daily_cases/` | Case data prepared for public-facing use, with small-count suppression |
| Dashboard cases | `dashboard/data/cases.json` | Case trends and related dashboard views |
| Dashboard alerts | `dashboard/data/alerts.json` | Outbreak-detection alerts |
| Dashboard forecasts | `dashboard/data/forecasts.json` | Forecast results |
| Dashboard resources | `dashboard/data/resources.json` | Resource-allocation results |
| Dashboard calendar | `dashboard/data/calendar.json` | Preparedness-calendar results |

The listed paths reflect the project's documented layout. The current source code determines the exact output paths and schemas.

## Field Definitions

The data dictionary should document the fields in the encounter schema and the important Gold and dashboard datasets.

| Field | Data type | Meaning | Source or derivation | Validation / privacy |
|---|---|---|---|---|
| Exact field name from schema | Exact Spark or JSON type | Description of the field | Source field or transformation | Validation rule, allowed values, or suppression behavior |

Field definitions must be based on the actual implementation. Document identifiers, dates, disease categories, geographic attributes, demographic attributes, outcomes, counts, and weather-related variables only when they exist in the relevant schema.

For dashboard JSON, document the published field names and types separately when they differ from the underlying Parquet schema.

## Data Provenance

EpiScope uses synthetic encounter data and synthetic outbreak labels in its recorded experiments. These data support controlled testing and evaluation; they must not be presented as real patient records or actual public-health surveillance observations.

Weather-related fields must be identified as synthetic or derived unless their external source has been independently established.

The provenance record should identify:

- **Generation:** Generator configuration, scale factor, random seed, generation date, and input row count when available.
- **Bronze processing:** Source input and ingestion transformations.
- **Silver processing:** Validation rules, cleaning operations, quarantine criteria, and data-quality outputs.
- **Gold processing:** Aggregations and derived analytical datasets.
- **Analytics:** Transformations used to produce detection, forecast, resource-allocation, and preparedness-calendar outputs.
- **Public serving:** Transformations and privacy controls applied before dashboard publication.
- **Dashboard export:** The relationship between internal outputs and the exported JSON datasets.

## Schema Verification

Parquet schemas should be verified using Spark's schema inspection facilities. Dashboard JSON schemas should be checked against representative exported records and the dashboard code.

If a dataset cannot be read from its documented path, consult the corresponding pipeline script to identify the configured input or output location and storage format. Do not infer field names or types from dashboard labels.

## Privacy Considerations

Public-facing datasets are separated from internal analytical outputs so privacy controls can be applied before publication. Small-count suppression is intended to prevent exact publication of low case counts. It does not, by itself, guarantee protection against indirect disclosure or re-identification.

Privacy checks should be repeated after changes to data transformations, suppression rules, or dashboard exports.
