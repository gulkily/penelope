# Mentor Transcript Improvements (Step 3: Development Plan)

1. Tighten transcript prompt rules
   - Goal: Reduce off-target suggestions by reinforcing “only if mentioned” behavior.
   - Dependencies: Existing prompt templates.
   - Expected changes: Update `app/prompts/transcript_system.txt` with clearer constraints; no schema changes.
   - Verification: Manual prompt review to confirm rules are explicit.
   - Risks/open questions: Overly strict prompts might reduce helpful updates.
   - Canonical components/APIs: Prompt templates used by transcript analyzer.

2. Add client-side suggestion filtering
   - Goal: Suppress suggestions that match current values or are empty.
   - Dependencies: Current transcript proposal rendering in `static/js/app.js`.
   - Expected changes: Filter proposal fields in the UI before rendering; skip unchanged summary/questions/objective/goal/progress; skip empty items.
   - Verification: Manual: run analysis with a transcript that doesn’t mention progress and confirm no progress suggestion renders.
   - Risks/open questions: False negatives if normalization differs between server and client.
   - Canonical components/APIs: Reuse existing project data from `/api/projects/{project_id}`.

3. Show resident context in dialog
   - Goal: Reduce mistaken updates by showing the active resident name.
   - Dependencies: Dialog markup and project data in `static/js/app.js`.
   - Expected changes: Add resident name in the dialog header in `templates/index.html`; populate it when the dialog opens.
   - Verification: Manual: open dialog and confirm the resident name matches the selector.
   - Risks/open questions: None.
   - Canonical components/APIs: Resident selector and project data already loaded in the dashboard.

4. Clarify progress suggestion context
   - Goal: Show both percent and units/goal for progress suggestions.
   - Dependencies: Existing progress math helpers in `static/js/app.js`.
   - Expected changes: Update progress suggestion rendering to display computed units alongside percent; no API changes.
   - Verification: Manual: check that percent and units align with current goal.
   - Risks/open questions: Ensure unit math matches slider display.
   - Canonical components/APIs: Progress display helpers and existing goal/progress fields.

5. Draft Option C follow-up Step 1
   - Goal: Capture a fresh Step 1 solution assessment for the Option C track once these improvements are complete.
   - Dependencies: Completion feedback from Steps 1–4 and any observed false positives.
   - Expected changes: New planning doc in `docs/plans/` for Option C Step 1 (evidence-backed updates with server validation).
   - Verification: Manual review of the Step 1 doc with stakeholders.
   - Risks/open questions: Scope creep if Option C requirements are still evolving.
   - Canonical components/APIs: Planning artifacts only.
