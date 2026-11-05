# F1 Pit Stop and Race Strategy Data

Validated canonical data for completed Formula 1 races from 1950 through 2026.

## Files

- `pit_events.csv`: One row per observed pit-lane visit, including stop order, lap, and available durations.
- `race_context.csv`: One row per race with circuit identity, race-start weather, race distance, and safety-car outcomes.
- `race_drivers.csv`: One row per driver and race, including grid position, official classification, and result status.
- `stints.csv`: One row per continuous tyre stint, including compound, lap boundaries, and tyre age.
- `weather_observations.csv`: Timestamped trackside weather observations recorded during race sessions.
- `coverage.csv`: Per-table season coverage and row counts; unavailable historical telemetry is not represented as zero.
- `data_quality_issues.csv`: Per-race validation findings, source limitations, normalization decisions, and publication treatment.
- `provenance.csv`: Compact source and retrieval metadata removed from the analysis-ready CSV files.
- `data_dictionary.csv`: Types, descriptions, feature timing, units, targets, and nullability.
- `validation_manifest.json`: Per-race build status, row counts, and validation issues.

## Quality policy

Canonical tables are admitted independently: a telemetry defect cannot delete an independently valid official race result. A table with an error-level issue remains excluded for that race, and every issue stays visible in the validation manifest. Repeated source URLs, retrieval timestamps, and validation fields are removed from the analysis-ready tables and preserved compactly in `provenance.csv`.

## Modelling boundary

Use `feature_time` in the data dictionary to separate `pre_race`, `live`, and `post_race` fields. Post-race fields must not be used as predictors for pre-race or live models.
