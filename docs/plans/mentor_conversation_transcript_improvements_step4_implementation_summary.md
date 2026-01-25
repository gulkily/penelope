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
