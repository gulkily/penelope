# Project URL State - Step 3 Development Plan

1. Stage 1 - Read project ID from URL on load
   - Goal: Preselect the project based on the `?project=` query param.
   - Dependencies: Existing project list fetch and selection flow.
   - Expected changes: Parse `window.location.search` to capture a project ID and set the select value before loading data.
   - Verification: Load `/` with `?project=1` and confirm selection and data load.
   - Risks/open questions: Handle invalid IDs gracefully.
   - Shared components/API contracts: Reuse `GET /api/projects/{project_id}`.

2. Stage 2 - Update URL on selection changes
   - Goal: Keep the URL in sync with the current selection.
   - Dependencies: Stage 1.
   - Expected changes: Update the query string when project selection changes; clear the param when none is selected.
   - Verification: Select a project and confirm `?project=` updates; clear selection and confirm the param is removed.
   - Risks/open questions: Ensure back/forward navigation behaves as expected.
   - Shared components/API contracts: None.

3. Stage 3 - Handle reload and invalid states cleanly
   - Goal: Ensure the UI stays consistent across reloads and invalid URLs.
   - Dependencies: Stages 1–2.
   - Expected changes: Add fallback to empty state for invalid IDs; re-run state sync on `pageshow`.
   - Verification: Use an invalid project ID and confirm empty state; reload and verify selection persists.
   - Risks/open questions: If the project list changes, selection may no longer be valid.
   - Shared components/API contracts: None.
