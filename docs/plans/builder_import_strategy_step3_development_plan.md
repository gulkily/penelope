# Builder Import Strategy - Step 3 Development Plan

1. Stage 1 - Add import mapping storage for idempotency
- Goal: Persist deterministic links between source UUIDs and app project/check-in imports.
- Dependencies: Existing DB init/migration flow.
- Expected changes: Conceptually add `import_builder_map` and `import_checkin_map` tables; wire table creation into DB initialization.
- Planned signatures: `ensure_import_tables() -> None` (or equivalent init hook), `get_project_id_for_source_builder(source_builder_id: str) -> int | None`.
- Verification approach: Initialize DB twice and confirm mapping data remains stable across reruns.
- Risks/open questions:
  - Need clear ownership of these tables (new `app/db_import_map.py` vs existing module).
  - Keep migrations additive and safe on existing DBs.
- Shared components/API contracts: `app/db_init.py`, DB connection layer.

2. Stage 2 - Build deterministic source extraction + normalization pass
- Goal: Read SQLite source and produce normalized in-memory import records before any writes.
- Dependencies: Stage 1, source file access.
- Expected changes: Add importer module/CLI scaffold that reads builders + latest check-ins, resolves house joins, normalizes house to (`Unassigned`, `Actioners`, `SF2`), and marks missing progress cases.
- Planned signatures: `load_source_snapshot(sqlite_path: str) -> SourceSnapshot`, `normalize_house_name(source_house: str | None) -> str`.
- Verification approach: Dry-run over source DB and inspect printed sample rows/counts.
- Risks/open questions:
  - Unknown house names must fall back to `Unassigned` with warning.
  - Must preserve source IDs untouched for mapping tables.
- Shared components/API contracts: `app/house.py`, source SQLite reader utility/script.

3. Stage 3 - Implement deterministic write pass for projects + mapping tables
- Goal: Create/update residents in app DB with rerun-safe behavior.
- Dependencies: Stage 1-2.
- Expected changes: Upsert builder/project by `source_builder_id` via `import_builder_map`; write/update core resident fields (`name`, `house`, objective seed), and track latest check-in link in `import_checkin_map`.
- Planned signatures: `upsert_project_from_builder(record: BuilderRecord) -> int`, `upsert_checkin_mapping(record: CheckinRecord, project_id: int) -> None`.
- Verification approach: Run importer twice and confirm no duplicate residents/mappings.
- Risks/open questions:
  - Decide whether importer updates existing manually-edited fields or only empty/import-tagged fields.
  - Ensure transaction boundaries avoid partial writes.
- Shared components/API contracts: `app/db_projects.py`, new import map DB module, transaction boundaries via `app/db_connection.py`.

4. Stage 4 - Add section-item mapping for latest check-in content
- Goal: Materialize latest check-in narratives into app sections consistently.
- Dependencies: Stage 3.
- Expected changes: Map `positive_summary`/`blockers_text`/`traction_text`/`llm_summary` into `summary`/`challenges`/`milestones`/`opportunities`; add fallback to `questions` using `textual_data`; add no-checkin and missing-progress notes in `questions`.
- Planned signatures: `build_section_payloads(latest_checkin: CheckinRecord | None) -> SectionPayloads`.
- Verification approach: Manual spot-check for at least 3 residents spanning: full narrative, missing progress, no check-in.
- Risks/open questions:
  - Need rerun-safe item behavior (replace/update imported items without duplicating user-authored items).
  - Keep note prefixes standardized for later cleanup/reporting.
- Shared components/API contracts: `app/db_items.py`, `app/db_projects.py` (`questions` updates).

5. Stage 5 - Add LLM enrichment step using `openai/gpt-5.2`
- Goal: Improve narrative quality while keeping deterministic integrity.
- Dependencies: Stage 2-4 deterministic pipeline complete.
- Expected changes: Add optional enrichment mode that sends source narrative bundle to Dedalus API model `openai/gpt-5.2`, requires strict JSON-schema output, validates response, and falls back to deterministic text if invalid/low-confidence.
- Planned signatures: `enrich_checkin_text_with_llm(payload: LlmInput) -> LlmOutput`, `validate_llm_output(output: dict) -> ValidatedOutput`.
- Verification approach: Run dry-run with LLM enabled and disabled; compare transformed outputs and schema validation logs.
- Risks/open questions:
  - API failures/timeouts must not break deterministic import path.
  - Confidence threshold needs an initial default for manual review queueing.
- Shared components/API contracts: Dedalus client integration module, importer CLI flags/config.

6. Stage 6 - Implement dry-run/reporting contract
- Goal: Produce auditable import output before full writes.
- Dependencies: Stage 2-5.
- Expected changes: Emit standardized report metrics: builders/check-ins imported/updated/skipped, no-checkin count, missing progress count, house warnings, mapping errors, low-confidence LLM rows.
- Planned signatures: `run_import(..., dry_run: bool = True) -> ImportReport`, `render_import_report(report: ImportReport) -> str`.
- Verification approach: Execute dry-run and verify all required counters/sections are present.
- Risks/open questions:
  - Ensure report distinguishes deterministic failures vs LLM enrichment issues.
  - Keep output concise enough for operator review.
- Shared components/API contracts: importer CLI entrypoint and logging/report formatter.

7. Stage 7 - End-to-end validation + rollout checklist
- Goal: Confirm Phase 1 is safe for production execution.
- Dependencies: Stage 1-6.
- Expected changes: Add a focused validation script/runbook: sample row checks, rerun idempotency check, and pre/post counts.
- Verification approach: Perform one dry-run and one real-run on a non-production DB copy, then rerun to verify no duplicates.
- Risks/open questions:
  - If imported text quality is inconsistent, may need to tune prompt/schema before production.
  - Decide go/no-go threshold for low-confidence LLM rows.
- Shared components/API contracts: importer CLI/runbook docs, `docs/plans/builder_import_strategy_hybrid_notes.md` alignment.
