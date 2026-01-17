# Test Matrix Gaps - Step 3 Development Plan

1. Add E2E coverage for Questions autosave
   - Goal: Validate that questions persist after typing.
   - Dependencies: Existing questions autosave in `static/js/app.js`.
   - Expected changes: Add an E2E test that edits questions and confirms persistence after reload.
   - Verification: Run the E2E suite locally.
   - Risks/open questions: Autosave timing may require a wait for the save request.
   - Shared components/API contracts touched: Questions textarea in `templates/index.html` and `/questions` endpoint.

2. Add E2E coverage for item add/edit/delete
   - Goal: Validate core list item CRUD flows.
   - Dependencies: Inline add/edit/delete flows in `static/js/app.js`.
   - Expected changes: Add an E2E test that adds an item, edits it, deletes it, and verifies UI updates.
   - Verification: Run the E2E suite locally.
   - Risks/open questions: Toast/undo timing and dynamic list updates can be flaky.
   - Shared components/API contracts touched: Item endpoints and inline list UI.

3. Add E2E coverage for archive/unarchive project
   - Goal: Validate project archive toggling in the project management view.
   - Dependencies: Manage Projects flow in `templates/manage_projects.html` and `static/js/manage-projects.js`.
   - Expected changes: Add an E2E test that archives a project and verifies status.
   - Verification: Run the E2E suite locally.
   - Risks/open questions: The archived row styling may require explicit assertions.
   - Shared components/API contracts touched: `/projects/{id}/archive` endpoint.

4. Add E2E coverage for theme toggle
   - Goal: Validate theme toggle behavior and persistence.
   - Dependencies: Theme toggle UI and `static/js/theme.js`.
   - Expected changes: Add an E2E test that toggles theme and confirms attribute updates.
   - Verification: Run the E2E suite locally.
   - Risks/open questions: System theme state may need to be normalized for consistency.
   - Shared components/API contracts touched: Theme toggle button and `data-theme` attribute.

5. Update test matrix
   - Goal: Keep coverage documentation accurate.
   - Dependencies: `docs/test_matrix.md`.
   - Expected changes: Mark newly covered flows and add references to new tests.
   - Verification: Review the matrix for completeness.
   - Risks/open questions: Keep names aligned with tests.
   - Shared components/API contracts touched: Documentation only.
