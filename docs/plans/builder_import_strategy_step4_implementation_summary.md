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

## Stage 3 - Implement deterministic write pass for projects + mapping tables
- Changes:
  - Added `app/builder_import_pipeline.py` with:
    - deterministic project upsert flow based on source builder mappings,
    - mapping-table updates for builders and latest check-ins,
    - objective seeding from north-star metric metadata,
    - dry-run aware import report counters.
  - Extended `scripts/import_builder_snapshot.py` to initialize DB, run the deterministic import pipeline, and print import report metrics.
- Verification:
  - Ran `python -m py_compile app/builder_import_pipeline.py scripts/import_builder_snapshot.py`.
  - Ran `python scripts/import_builder_snapshot.py --sample 2` (dry-run).
- Notes:
  - Deterministic rerun behavior is now scaffolded before section-item and LLM enrichment stages.

## Stage 4 - Add section-item mapping for latest check-in content
- Changes:
  - Added `app/builder_import_transform.py` to map latest check-in fields into section payloads and import notes.
  - Added `app/db_import_content.py` to:
    - replace prior import snapshot items (`[Import Snapshot]...`) per project,
    - replace import-prefixed notes in `projects.questions` while preserving non-import questions.
  - Updated `app/builder_import_pipeline.py` to apply section-item writes and import notes during write mode.
- Verification:
  - Ran `python -m py_compile app/builder_import_transform.py app/db_import_content.py app/builder_import_pipeline.py`.
  - Ran `DATABASE_URL=sqlite:////tmp/builder_import_stage4.sqlite python scripts/import_builder_snapshot.py --sample 1 --write`.
  - Queried `/tmp/builder_import_stage4.sqlite` and confirmed imported snapshot items + import notes were present.
- Notes:
  - Imported section entries are tagged with `[Import Snapshot] {week_of}: ...` to support rerun-safe replacement.

## Stage 5 - Add LLM enrichment step using `openai/gpt-5.2`
- Changes:
  - Added `app/builder_import_llm.py` with structured-output enrichment flow using Dedalus `chat.completions.parse`.
  - Default enrichment model is `openai/gpt-5.2`, with confidence-based acceptance and deterministic fallback.
  - Updated `ImportConfig` / `ImportReport` in `app/builder_import_pipeline.py` to support optional enrichment and report LLM attempt/outcome counters.
  - Extended CLI options in `scripts/import_builder_snapshot.py`:
    - `--enable-llm`
    - `--llm-model` (default `openai/gpt-5.2`)
    - `--llm-confidence-threshold`
- Verification:
  - Ran `python -m py_compile app/builder_import_llm.py app/builder_import_pipeline.py scripts/import_builder_snapshot.py`.
  - Ran `python scripts/import_builder_snapshot.py --sample 1` (LLM disabled path).
- Notes:
  - LLM-enabled runtime was not executed in this environment because external API credentials/network are not guaranteed here.

## Stage 6 - Implement dry-run/reporting contract
- Changes:
  - Expanded `ImportReport` in `app/builder_import_pipeline.py` to cover:
    - builders scanned/imported/updated/skipped
    - builders without check-ins
    - latest check-ins created/updated/skipped
    - missing latest `north_star_value`
    - house warnings
    - LLM outcomes
    - validation/import errors.
  - Added deterministic check-in action classification (`created`/`updated`/`skipped`) using existing check-in mapping rows.
  - Added source-row validation guards for missing builder IDs/names.
  - Updated report rendering in `scripts/import_builder_snapshot.py` to print the full contract counters.
- Verification:
  - Ran `python -m py_compile app/builder_import_pipeline.py scripts/import_builder_snapshot.py`.
  - Ran `python scripts/import_builder_snapshot.py --sample 1`.
- Notes:
  - Dry-run output now distinguishes check-in mapping creation vs update vs skip, improving rerun auditability.
