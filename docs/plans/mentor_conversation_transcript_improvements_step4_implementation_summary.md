## Stage 1 – Tighten transcript prompt rules
- Changes: Strengthened prompt guardrails to only propose updates with explicit transcript support.
- Verification: Not run (prompt review only).
- Notes: Intended to reduce unsupported suggestions.

## Stage 2 – Client-side suggestion filtering
- Changes: Added filtering to hide unchanged text/goal/progress suggestions and skip empty/duplicate list items.
- Verification: Not run (manual analysis recommended).
- Notes: Text comparison normalizes whitespace and case for matching.

## Stage 3 – Show resident context in dialog
- Changes: Added resident name line in the transcript dialog and populate it on open.
- Verification: Not run (manual dialog check recommended).
- Notes: Uses loaded project data or selector text as fallback.

## Stage 4 – Clarify progress context
- Changes: Progress suggestions now show current percent + units/goal and a proposed percent + units line.
- Verification: Not run (manual dialog check recommended).
- Notes: Proposed units use the suggested goal when available.

## Stage 5 – Draft Option C Step 1
- Changes: Added `docs/plans/mentor_conversation_transcript_option_c_step1_solution_assessment.md` for the evidence-backed validation track.
- Verification: Not applicable.
- Notes: Option B recommended for server-side validation with evidence fields.

## Stage 6 – Units-based progress proposals
- Changes: Added progress units fields to the proposal schema and prefer units/delta to compute percent suggestions in the dialog; updated prompt rules/output format.
- Verification: Not run (manual transcript test recommended).
- Notes: Units/delta proposals override percent suggestions and are converted using the current or proposed goal.
