# Builder Import Open Questions + Proposed Answers

## Goal
Convert the remaining uncertainty from `builder_import_strategy_hybrid_notes.md` into concrete implementation decisions for Phase 1 (latest snapshot import).

## 1) Source identity and idempotency
Question:
- How do we guarantee safe reruns when source IDs are UUIDs but app `projects.id` is integer?

Proposed answer:
- Do not try to reuse source UUIDs as `projects.id`.
- Add dedicated import mapping tables:
  - `import_builder_map(source_builder_id TEXT PRIMARY KEY, project_id INTEGER UNIQUE NOT NULL, imported_at TEXT NOT NULL, updated_at TEXT NOT NULL)`
  - `import_checkin_map(source_checkin_id TEXT PRIMARY KEY, source_builder_id TEXT NOT NULL, week_of TEXT NOT NULL, project_id INTEGER NOT NULL, imported_at TEXT NOT NULL, updated_at TEXT NOT NULL, UNIQUE(source_builder_id, week_of))`
- Upsert rules:
  - Builder: upsert by `source_builder_id`.
  - Check-in snapshot: upsert by `source_checkin_id` (and guard by `(source_builder_id, week_of)`).

Why:
- This keeps core product tables simple while making reruns deterministic.

## 2) Progress semantics (`north_star_value` -> app progress)
Question:
- Should we write `progress` / `progress_history` from `north_star_value`?

Proposed answer:
- Phase 1: do **not** write numeric `progress` or `progress_history` from `north_star_value`.
- Keep imported residents at existing/default app progress until manually set.
- Carry raw metric values in narrative/context text and in import reports.
- Optional later path: allow LLM-inferred progress suggestions, but only as clearly labeled inferred data (never silent overwrite of source-of-truth progress).

Why:
- `north_star_value` is missing in latest weeks and app progress is a normalized percentage model; forced conversion would be noisy and misleading.

## 3) Weekly field mapping to app sections
Question:
- How should `weekly_checkins` text fields map to current sections?

Proposed answer (latest check-in only):
- `positive_summary` -> `summary` section item
- `blockers_text` -> `challenges` section item
- `traction_text` -> `milestones` section item
- `llm_summary` -> `opportunities` section item
- `textual_data` -> append to `questions` only when all mapped text fields are empty

Why:
- This is low-risk, human-readable, and aligned with existing section semantics.

## 4) “Missing progress needs manual completion” flag
Question:
- Where do we store this without new product-facing schema?

Proposed answer:
- Append a standardized note in `questions`:
  - `[Import TODO] Missing north_star_value for latest check-in week: YYYY-MM-DD.`
- Also include these residents in the post-import report.

Why:
- No core schema change required; visible to operators.

## 5) House mapping and normalization
Question:
- How do source houses map to required app house values?

Proposed answer:
- Resolve house from source join:
  - `builders.ca_id -> community_architects.house_id -> houses.name`
- Normalize to app fixed list:
  - `Actioners`, `SF2`, fallback `Unassigned`
- If source house is unknown/new, map to `Unassigned` and include warning in report.

Why:
- Satisfies current fixed-list house requirement while avoiding import failure.

## 6) Builders with no check-ins
Question:
- Import or skip?

Proposed answer:
- Import them as residents/projects (house + objective metadata), with no section items from check-ins.
- Add note in `questions`:
  - `[Import] No weekly check-ins available in source dataset.`

Why:
- Matches Phase 1 requirement to import all builders.

## 7) Timestamp policy
Question:
- What timestamp should we use for imported latest snapshot records?

Proposed answer:
- Snapshot “as-of” date: `week_of` from source check-in.
- Ordering timestamp fallback: `updated_at`, then `created_at`, then `week_ofT00:00:00Z`.
- Store UTC ISO strings.

Why:
- Gives consistent ordering and auditability.

## 8) Dry-run and report contract
Question:
- What minimum report fields do we need before real writes?

Proposed answer:
- Dry-run and real-run both produce:
  - builders scanned/imported/updated/skipped
  - builders with no check-ins
  - latest check-ins imported/updated/skipped
  - rows with missing `north_star_value`
  - house normalization warnings
  - unknown-source or mapping errors

Why:
- Enables safe validation and rerun confidence.

## 9) LLM-assisted transformation (Dedalus Labs API)
Question:
- Can we use a language model (including top models via Dedalus Labs API) to review and reformat import data before writing to the app DB?

Proposed answer:
- Yes, as an enrichment/formatting layer after deterministic mapping.
- Recommended pipeline:
  - Step A (deterministic): source ID mapping, house join/normalization, required-field checks, latest-checkin selection.
  - Step B (LLM): reformat/summarize text fields into app section-ready content, with strict JSON schema output.
  - Step C (write): persist deterministic fields plus LLM-transformed text; keep raw source text for auditability.
- Guardrails:
  - LLM output must be schema-validated before write.
  - Persist `model`, `prompt_version`, and a confidence/quality flag.
  - Add manual-review queue for low-confidence transformations.
  - Never let LLM decide idempotency keys, source identity links, or house mapping when deterministic joins exist.

Why:
- Improves text quality and consistency while preserving deterministic data integrity.

## Implementation Readiness
Current readiness: **mostly ready**, pending explicit confirmation of 4 decisions:
1. Approve import mapping tables for idempotency (`import_builder_map`, `import_checkin_map`).
2. Approve Phase 1 policy to skip numeric `progress/progress_history` writes.
3. Approve the proposed field-to-section mapping for latest check-ins.
4. Confirm LLM policy: enrichment-only in Phase 1 (no deterministic key/identity decisions by model), with schema validation + review flags.

If these are accepted, implementation can start immediately with low ambiguity.
