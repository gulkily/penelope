## Stage 1 - Expand source extraction from latest-only to full check-in history
- Changes:
  - Updated `app/builder_import_source.py` so each `SourceBuilderRecord` now includes a `checkins` list (all source check-ins) in deterministic chronological order.
  - Kept `latest_checkin` as a compatibility field derived from the ordered `checkins` list.
- Verification:
  - Ran `python -m py_compile app/builder_import_source.py`.
  - Ran `python scripts/import_builder_snapshot.py --source-db data/export_sebastian_ankita_amanda.db --sample 3 --no-progress` and confirmed `Weekly check-ins: 57` with per-builder check-in counts in sample output.
- Notes:
  - Ordering key uses `week_of`, `updated_at`, `created_at`, `source_checkin_id` for stable reruns.

## Stage 2 - Shift pipeline to per-checkin processing
- Changes:
  - Updated `app/builder_import_pipeline.py` to iterate all `builder.checkins` and process each check-in as a discrete import unit.
  - Added aggregate counters for all-checkin execution (`checkins_scanned/created/updated/skipped`, `missing_progress_checkins`).
  - Updated `scripts/import_builder_snapshot.py` report output to include the new check-in counters.
- Verification:
  - Ran `python -m py_compile app/builder_import_pipeline.py scripts/import_builder_snapshot.py`.
  - Verified dry-run output shows `Check-ins scanned: 57`.
- Notes:
  - `latest_checkin` counters were replaced with full check-in counters while preserving `missing_progress_latest` for visibility.

## Stage 3 - Define rerun-safe historical write strategy
- Changes:
  - Refactored `app/db_import_content.py` so `replace_import_snapshot_items` accepts all per-checkin payloads, rebuilds imported item sets deterministically, and preserves non-imported user items.
  - Updated pipeline writes to pass full payload lists and keep `replace_import_item_ids_for_project` as authoritative mapping for imported rows.
- Verification:
  - Ran isolated write flow:
    - `DATABASE_URL=sqlite:////tmp/builder_import_all_updates_stage4.sqlite python scripts/import_builder_snapshot.py --source-db data/export_sebastian_ankita_amanda.db --sample 2 --write --no-progress`
    - repeated the same command for rerun validation.
  - Queried isolated DB:
    - `SELECT COUNT(*) FROM import_item_map` => `678`
    - `SELECT project_id, COUNT(*), COUNT(DISTINCT created_at) ...` and confirmed multi-date histories per resident.
- Notes:
  - Import reruns replace imported rows deterministically; item IDs can rotate, while mapped row counts remain stable.

## Stage 4 - Add deterministic duplicate and near-duplicate controls
- Changes:
  - Added canonical normalization (`normalize_import_text`) and deterministic duplicate filtering in `app/db_import_content.py`.
  - Added rule-based near-duplicate detection with stable similarity thresholds and per-section filtering.
  - Added duplicate counters to import metrics (`exact_duplicates_skipped`, `near_duplicates_skipped`).
- Verification:
  - Write run output reported non-zero duplicate suppression:
    - `Exact duplicates skipped: 21`
    - `Near-duplicates skipped: 11`
- Notes:
  - Deterministic duplicate filtering runs before any optional LLM arbitration.

## Stage 5 - Add optional LLM arbitration for borderline duplicates
- Changes:
  - Added `classify_duplicate_pair_with_llm` in `app/builder_import_llm.py` for optional duplicate arbitration decisions (`keep`/`drop`).
  - Wired optional arbitration callback in pipeline write flow when LLM mode is enabled.
  - Added arbitration counters to report (`llm_duplicate_arbitration_attempted/kept/dropped`).
- Verification:
  - Compiled successfully with `python -m py_compile app/builder_import_llm.py app/builder_import_pipeline.py`.
  - Verified non-LLM runs keep arbitration counters at zero.
- Notes:
  - LLM arbitration is fallback-only for borderline pairs; deterministic duplicate filters remain primary.

## Stage 6 - Extend reporting and operator diagnostics
- Changes:
  - Extended import report rendering in `scripts/import_builder_snapshot.py` with new historical + duplicate metrics.
  - Updated preview output to include total weekly check-in count and per-builder check-in sample counts.
- Verification:
  - Dry-run command output included:
    - `Weekly check-ins: 57`
    - all new check-in and duplicate metrics lines.
- Notes:
  - Report now distinguishes builder-level outcomes from check-in-level outcomes.

## Stage 7 - End-to-end validation and rollout gate
- Changes:
  - Performed end-to-end dry-run and isolated write/rerun validations against the real source export DB.
  - Confirmed imported residents now receive multi-date imported items rather than single-date latest snapshots only.
- Verification:
  - Dry-run:
    - `python scripts/import_builder_snapshot.py --source-db data/export_sebastian_ankita_amanda.db --sample 3 --no-progress`
  - Write + rerun on isolated DB:
    - `DATABASE_URL=sqlite:////tmp/builder_import_all_updates_stage4.sqlite python scripts/import_builder_snapshot.py --source-db data/export_sebastian_ankita_amanda.db --sample 2 --write --no-progress`
    - same command repeated
  - Post-run DB spot checks on `/tmp/builder_import_all_updates_stage4.sqlite`:
    - imported map count stable at `678`
    - per-project imported rows show multiple distinct `created_at` dates.
- Notes:
  - LLM arbitration path is implemented but not exercised in this environment to avoid external dependency variance.
