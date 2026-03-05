# Builder Import All Updates - Step 2 Feature Description

Problem: The current builder import only surfaces each resident's latest check-in, which hides historical weekly updates and makes imported timelines look incomplete.

User stories:
- As a program lead, I want all historical weekly check-ins imported so that each resident timeline reflects full source history.
- As a coach, I want imported section items to reflect when updates occurred so that I can understand progression over time.
- As an operator, I want rerunning imports to stay safe and deterministic so that repeated runs do not create duplicate or conflicting records.

Core requirements:
- Import all available weekly check-ins per builder from the source dataset, not only the latest check-in.
- Process updates per check-in (discrete units) rather than combining all history into one merged payload.
- Preserve chronological ordering of imported updates so older updates appear before newer updates.
- Enforce deterministic dedupe first (exact duplicates and rule-based near-duplicates) before writes.
- Use LLM duplicate arbitration only for borderline near-duplicate cases, with deterministic fallback on errors/timeouts.
- Keep import behavior idempotent across reruns (same source data produces stable app results).
- Preserve the current behavior for builders with no check-ins (builder still appears in app data).
- Continue showing imported content in existing resident sections without breaking existing manual editing workflows.

Shared component inventory:
- Import CLI workflow (`scripts/import_builder_snapshot.py`): extend the existing import run path; no new operator entry point needed.
- Import pipeline and mapping surfaces (`builder_import_*`, `db_import_*`): extend canonical import surfaces rather than adding a separate historical importer.
- LLM enrichment surface (`builder_import_llm.py`): reuse as optional per-checkin duplicate-arbitration support, not as primary dedupe logic.
- Dashboard section lists (Summary, Challenges, Opportunities, Milestones): reuse existing rendering surfaces for imported items; no new section UI.
- Item date display in dashboard: reuse current item date display behavior so imported historical items are visible in the same list patterns.

Simple user flow:
1. Operator runs the builder import against a source export.
2. The import processes each builder and each weekly check-in in chronological order.
3. Deterministic duplicate filters run before write, with optional LLM arbitration for borderline near-duplicates.
4. The dashboard shows residents with imported section entries spanning multiple weeks.
5. Operator reruns import and confirms data remains stable without duplicate history.

Success criteria:
- For a builder with multiple source check-ins, the app contains imported entries representing more than one check-in week.
- Borderline duplicate content is either merged/skipped consistently or explicitly reported; LLM failures do not block import completion.
- A full import rerun does not increase imported row counts when source data is unchanged.
- Builders with no source check-ins are still present in app projects.
- Coaches can visually confirm date diversity in imported section entries for residents with historical data.
