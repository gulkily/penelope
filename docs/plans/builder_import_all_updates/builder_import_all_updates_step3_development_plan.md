# Builder Import All Updates - Step 3 Development Plan

1. Stage 1 - Expand source extraction from latest-only to full check-in history
- Goal: Produce deterministic per-builder check-in sequences instead of a single latest record.
- Dependencies: Existing source loader and house normalization flow.
- Expected changes: Extend source snapshot contract to include all check-ins ordered by `week_of`, then timestamp tie-breakers; keep current latest-checkin helpers for compatibility where needed.
- Planned signatures: `load_source_snapshot(sqlite_path: str) -> SourceSnapshot`, `SourceBuilderRecord.checkins: list[SourceCheckinRecord]`.
- Verification approach: Dry-run output confirms expected check-in counts per builder and stable ordering across repeated runs.
- Risks/open questions:
  - Ordering must be deterministic when `week_of` ties occur.
  - Memory footprint should remain safe for larger source exports.
- Shared components/API contracts: `app/builder_import_source.py`, import CLI preview/report output.

2. Stage 2 - Shift pipeline to per-checkin processing
- Goal: Process each weekly update as a discrete import unit.
- Dependencies: Stage 1.
- Expected changes: Update import orchestration to iterate per builder and per check-in chronologically; keep builder/project mapping flow intact.
- Planned signatures: `run_import(config: ImportConfig, ...) -> ImportReport`, `build_section_payloads(builder, checkin) -> SectionPayloads`.
- Verification approach: For a sample builder with multiple check-ins, confirm multiple import write attempts are emitted in chronological order.
- Risks/open questions:
  - Ensure no regression for builders with zero check-ins.
  - Ensure import duration remains acceptable with larger historical volume.
- Shared components/API contracts: `app/builder_import_pipeline.py`, `app/builder_import_transform.py`, `app/db_import_map.py`.

3. Stage 3 - Define rerun-safe historical write strategy
- Goal: Persist historical imported items without duplicate growth across reruns.
- Dependencies: Stage 2.
- Expected changes: Replace latest-snapshot-only write behavior with deterministic historical reconciliation (stable imported set per resident after each run) while preserving non-imported user-authored items.
- Planned signatures: `replace_import_snapshot_items(project_id: int, payloads: list[SectionPayloads]) -> None` (or equivalent historical import writer).
- Verification approach: Run write twice on unchanged source; confirm imported row counts and content hashes are unchanged.
- Risks/open questions:
  - Must avoid deleting manual/non-imported items.
  - Need clear rule for handling source edits to older weeks.
- Shared components/API contracts: `app/db_import_content.py`, `app/db_import_map.py`, `items` import-tag/mapping behavior.

4. Stage 4 - Add deterministic duplicate and near-duplicate controls
- Goal: Prevent exact duplicates and suppress obvious near-duplicates before persistence.
- Dependencies: Stage 3.
- Expected changes: Add canonical text normalization and rule-based similarity checks scoped to resident + section + import history; keep decisions deterministic.
- Planned signatures: `normalize_import_text(text: str) -> str`, `is_near_duplicate(candidate: str, existing: str) -> bool`.
- Verification approach: Fixture-based dry-run validates duplicate collapse and stable outcomes across repeated runs.
- Risks/open questions:
  - Similarity thresholds may over-collapse short items.
  - Must preserve meaningfully distinct updates in consecutive weeks.
- Shared components/API contracts: `app/db_import_content.py`, import report counters in pipeline output.

5. Stage 5 - Add optional LLM arbitration for borderline duplicates
- Goal: Use LLM only when deterministic checks are inconclusive.
- Dependencies: Stage 4 and existing LLM integration.
- Expected changes: Route borderline candidate pairs through LLM classifier/decision helper; default to deterministic fallback when unavailable, low confidence, or error.
- Planned signatures: `classify_duplicate_pair(candidate: str, existing: str, ...) -> DuplicateDecision`.
- Verification approach: Run with LLM enabled/disabled and confirm deterministic fallback parity on failures/timeouts.
- Risks/open questions:
  - Latency/cost from per-pair arbitration on noisy datasets.
  - Need confidence threshold defaults and report visibility.
- Shared components/API contracts: `app/builder_import_llm.py`, `ImportConfig` flags, CLI options in `scripts/import_builder_snapshot.py`.

6. Stage 6 - Extend reporting and operator diagnostics
- Goal: Make duplicate handling and historical import coverage auditable.
- Dependencies: Stage 2-5.
- Expected changes: Add report counters for check-ins processed, items inserted, exact duplicates skipped, near-duplicates skipped, LLM arbitration attempts/outcomes.
- Planned signatures: `ImportReport` fields for duplicate/arbitration metrics, `render_import_report(report) -> str`.
- Verification approach: Dry-run and write-run outputs include all new counters and non-zero values on crafted duplicate fixtures.
- Risks/open questions:
  - Keep report concise enough for operational review.
  - Ensure metric definitions are stable across versions.
- Shared components/API contracts: `app/builder_import_pipeline.py`, `scripts/import_builder_snapshot.py`.

7. Stage 7 - End-to-end validation and rollout gate
- Goal: Prove full-history import correctness and safety before implementation rollout.
- Dependencies: Stage 1-6.
- Expected changes: Add targeted validation checklist for historical coverage, dedupe behavior, and rerun idempotency against an isolated DB.
- Verification approach: Execute dry-run + write-run + rerun on isolated DB and verify:
  - multi-week builders show historical entries,
  - duplicate counters behave as expected,
  - rerun produces no net growth on unchanged source.
- Risks/open questions:
  - If duplicate suppression is too aggressive, thresholds may need tuning.
  - If historical volume harms UX, we may need a follow-up filtering/display feature.
- Shared components/API contracts: importer runbook and docs in `docs/plans/`.
