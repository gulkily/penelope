# Builder Import Strategy (SQLite -> App, Hybrid + LLM Enrichment)

## Dataset Reviewed
- Source DB (example placeholder): `data/builder_import_source.db`
- Tables: `builders`, `community_architects`, `houses`, `weekly_checkins`, `builder_nps_schedule`, `frontend_evaluations`, `frontend_eval_schedule`
- Key counts:
  - `builders`: 21
  - `weekly_checkins`: 57 (18 builders with check-ins; 3 builders with none)
  - Check-in range: `2026-01-12` to `2026-02-09`
- Data profile:
  - No duplicate `(builder_id, week_of)` rows.
  - `north_star_value` missing in 35/57 rows (61.4%).
  - Latest 3 weeks are fully missing `north_star_value`.
  - Narrative fields are mostly present and usable.

## App Constraints (Important for Import Design)
- App `projects.id` is integer autoincrement, so source UUIDs cannot be reused as resident IDs.
- App house values are fixed and normalized (`Unassigned`, `Actioners`, `SF2`).
- App progress model is integer percentage (`progress`/`progress_history`), not raw north-star metric values.

## Final Strategy
Hybrid import remains the right path.

1. Phase 1 (implement now): latest-per-builder snapshot
- Import all builders.
- Import one check-in per builder (max `week_of`).
- Prioritize deterministic, idempotent writes.
- Use LLM only for text reformat/enrichment (not identity or key decisions).

2. Phase 2 (optional later): historical backfill
- Backfill remaining weekly rows after Phase 1 validation.
- Optionally prioritize historical rows where `north_star_value` exists.

## Idempotency and Source Mapping
To make reruns safe:
- Add `import_builder_map`:
  - `source_builder_id TEXT PRIMARY KEY`
  - `project_id INTEGER UNIQUE NOT NULL`
  - `imported_at TEXT NOT NULL`
  - `updated_at TEXT NOT NULL`
- Add `import_checkin_map`:
  - `source_checkin_id TEXT PRIMARY KEY`
  - `source_builder_id TEXT NOT NULL`
  - `week_of TEXT NOT NULL`
  - `project_id INTEGER NOT NULL`
  - `imported_at TEXT NOT NULL`
  - `updated_at TEXT NOT NULL`
  - `UNIQUE(source_builder_id, week_of)`

Upsert policy:
- Builder upsert key: `source_builder_id`.
- Check-in upsert key: `source_checkin_id` with `(source_builder_id, week_of)` guard.

## Field Mapping (Phase 1)
Builder -> project:
- Name: `builders.full_name`
- House: `builders.ca_id -> community_architects.house_id -> houses.name`, normalized to fixed app list (`Actioners`, `SF2`, fallback `Unassigned`)
- Objective seed: from builder north-star metadata, e.g. `north_star_metric_name` + `north_star_metric_unit`
- Optional notes: email/CA metadata appended to `questions` only if needed

Latest check-in -> app content:
- `positive_summary` -> `summary` section item
- `blockers_text` -> `challenges` section item
- `traction_text` -> `milestones` section item
- `llm_summary` -> `opportunities` section item
- `textual_data` -> append to `questions` only if all mapped text fields are empty

Builders with no check-ins:
- Still import builder/project.
- Add `questions` note: `[Import] No weekly check-ins available in source dataset.`

## Progress Handling (Phase 1)
- Do not write numeric `progress` or `progress_history` from `north_star_value`.
- Keep imported residents on existing/default app progress.
- Add `questions` note when latest check-in lacks progress:
  - `[Import TODO] Missing north_star_value for latest check-in week: YYYY-MM-DD.`
- Include missing-progress rows in import report.

Rationale:
- Raw source metric values do not map cleanly to app percent progress, and latest weeks are mostly missing.

## LLM Enrichment Layer (Dedalus API)
Confirmed model choice:
- Use `openai/gpt-5.2` for LLM-assisted transformation tasks.

Pipeline:
1. Deterministic pass (required):
   - source ID mapping
   - house join/normalization
   - required-field validation
   - latest-checkin selection
2. LLM pass (enrichment only):
   - reformat/summarize narrative text into section-ready content
   - strict JSON-schema output
3. Write pass:
   - persist deterministic fields + validated transformed text
   - preserve raw source text for auditability

Guardrails:
- Schema-validate model output before write.
- Record `model`, `prompt_version`, and quality/confidence flags.
- Queue low-confidence rows for manual review.
- Do not let LLM control idempotency keys, source identity links, or house mapping.
- Any inferred progress values are future-only and must be clearly labeled inferred.

## Dry-Run and Reporting Contract
Both dry-run and real-run must output:
- Builders scanned/imported/updated/skipped
- Builders without check-ins
- Latest check-ins imported/updated/skipped
- Rows with missing `north_star_value`
- House normalization warnings
- Mapping/validation errors
- Count of LLM low-confidence rows requiring review

## Implementation Readiness
Readiness status: ready to start implementation once the importer uses the above defaults.

Execution order:
1. Build deterministic importer + mapping tables + dry-run.
2. Add LLM enrichment step using `openai/gpt-5.2` with schema validation.
3. Validate a sample set across houses and check-in completeness.
4. Run full Phase 1 import.
5. Decide on Phase 2 historical backfill after report review.
