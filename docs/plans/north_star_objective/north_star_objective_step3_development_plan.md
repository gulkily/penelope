# North Star Objective - Step 3 Development Plan

1. Stage 1 - Extend SQLite data model for objective
   - Goal: Persist a single objective per project.
   - Dependencies: Existing SQLite initialization in `app/db.py`.
   - Expected changes: Add an `objective` field to projects; update seed data to include objectives; ensure read/write accessors return objective.
   - Verification: Manually query the project API and confirm the objective appears.
   - Risks/open questions: Decide on a default value for existing projects.
   - Shared components/API contracts: `GET /api/projects/{project_id}` payload extended with `objective`.

2. Stage 2 - Add API endpoint to update objective
   - Goal: Allow clients to update the objective per project.
   - Dependencies: Stage 1.
   - Expected changes: Add request schema and a `PUT /api/projects/{project_id}/objective` route; update DB write helper.
   - Planned signatures: `PUT /api/projects/{project_id}/objective`.
   - Verification: Use curl to update objective and re-fetch project data.
   - Risks/open questions: None.
   - Shared components/API contracts: New objective update endpoint, plus shared project payload.

3. Stage 3 - Add objective display and edit UI
   - Goal: Surface the objective near the top of the dashboard with inline editing.
   - Dependencies: Stage 1–2.
   - Expected changes: Add an objective field or card in the HTML; wire JS to render and update via API.
   - Verification: Select a project, edit objective, and confirm persistence.
   - Risks/open questions: Ensure empty objectives are handled gracefully.
   - Shared components/API contracts: Reuse project selection and rendering flow; extend `app.js` to update objective.

4. Stage 4 - Styling and layout refinement
   - Goal: Keep the new objective section consistent with the existing layout.
   - Dependencies: Stage 3.
   - Expected changes: Update CSS for objective area spacing and typography.
   - Verification: Visual check on desktop and mobile widths.
   - Risks/open questions: Ensure objective does not crowd the progress bar.
   - Shared components/API contracts: None.
