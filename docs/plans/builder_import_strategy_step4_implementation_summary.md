## Stage 1 - Add import mapping storage for idempotency
- Changes:
  - Added import mapping tables to DB initialization in `app/db_init.py`:
    - `import_builder_map` (`source_builder_id` -> `project_id`)
    - `import_checkin_map` (`source_checkin_id`, `source_builder_id`, `week_of`, `project_id`)
  - Added indexes for lookup paths used by importer reruns.
  - Added `app/db_import_map.py` with read/upsert helpers for builder and check-in mappings.
- Verification:
  - Ran `python -m py_compile app/db_init.py app/db_import_map.py`.
- Notes:
  - Mapping tables are additive and isolated from product-facing tables, preserving existing app behavior.

## Stage 2 - Build deterministic source extraction + normalization pass
- Changes:
  - Added `app/builder_import_source.py` with:
    - source snapshot loader (`load_source_snapshot`)
    - latest-checkin selection per builder
    - source-house normalization with fallback to `Unassigned`
    - typed source records for builders/check-ins.
  - Added CLI scaffold `scripts/import_builder_snapshot.py` to run preview/dry-run style source summaries.
- Verification:
  - Ran `python -m py_compile app/builder_import_source.py scripts/import_builder_snapshot.py`.
  - Ran `python scripts/import_builder_snapshot.py --sample 3`.
- Notes:
  - Source extraction now provides normalized in-memory records for later deterministic write stages.
