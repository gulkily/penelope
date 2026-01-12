# Project Management (Add/Archive) - Step 3 Development Plan

1. Stage 1 - Extend data model for archived state
   - Goal: Track whether a project is archived.
   - Dependencies: Existing projects table and project list API.
   - Expected changes: Add `archived` field to projects; include it in list/get responses; seed defaults.
   - Verification: Fetch project list and confirm archived values appear.
   - Risks/open questions: Backfill default to false for existing records.
   - Shared components/API contracts: `GET /api/projects` and `GET /api/projects/{id}` payloads.

2. Stage 2 - Add API endpoints for add/archive updates
   - Goal: Allow creating projects and toggling archived state.
   - Dependencies: Stage 1.
   - Expected changes: Add `POST /api/projects` for creation; add `PUT /api/projects/{id}/archive` for updates.
   - Planned signatures: `POST /api/projects`, `PUT /api/projects/{id}/archive`.
   - Verification: Create a project via API and toggle archived state; verify list updates.
   - Risks/open questions: Decide on name validation and duplicate handling.
   - Shared components/API contracts: New project create and archive update endpoints.

3. Stage 3 - Build the management page UI
   - Goal: Provide a separate page with a table and add form.
   - Dependencies: Stage 1–2.
   - Expected changes: Add a new template and route for management; render a table with project name, archived checkbox, and link to dashboard.
   - Verification: Load the page, see projects, and click through to dashboard links.
   - Risks/open questions: Decide where to link from the main dashboard (nav link).
   - Shared components/API contracts: Reuse `?project=` URL pattern for links.

4. Stage 4 - Wire UI actions to the API
   - Goal: Make add and archive interactions persist.
   - Dependencies: Stage 2–3.
   - Expected changes: Add JS to submit new projects, toggle archive checkboxes, and refresh the table.
   - Verification: Add a project, toggle archive, refresh, and confirm persistence.
   - Risks/open questions: Ensure disabled state when network calls are in flight.
   - Shared components/API contracts: Uses new create/archive endpoints.

5. Stage 5 - Styling and UX polish
   - Goal: Keep the management page consistent with the dashboard.
   - Dependencies: Stage 3–4.
   - Expected changes: Add CSS for table layout, form controls, and archived styling.
   - Verification: Visual check on desktop and mobile widths.
   - Risks/open questions: Table responsiveness for narrow screens.
   - Shared components/API contracts: None.
