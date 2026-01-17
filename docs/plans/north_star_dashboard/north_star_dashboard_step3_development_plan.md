# North Star Dashboard - Step 3 Development Plan

1. Stage 1 - Establish FastAPI app skeleton and static serving
   - Goal: Create the minimal backend structure and static asset wiring.
   - Dependencies: None.
   - Expected changes: Add FastAPI app entrypoint; configure static file serving and a root route for the UI shell.
   - Verification: Start the server and confirm the base page loads.
   - Risks/open questions: Decide on file layout for backend/frontend assets.
   - Shared components/API contracts: New FastAPI app/router; new static asset pipeline.

2. Stage 2 - Define data model and API contracts with SQLite-backed storage
   - Goal: Provide a predictable JSON shape for projects, progress, sections, and questions using SQLite as the default store.
   - Dependencies: Stage 1.
   - Expected changes: Create a SQLite schema and seed data; define API routes and payloads; isolate DB connection config via `DATABASE_URL` so Postgres can be swapped in later.
   - Planned signatures: `GET /api/projects`, `GET /api/projects/{project_id}`, `POST /api/projects/{project_id}/items`, `PUT /api/projects/{project_id}/questions`.
   - Verification: Call endpoints and validate payload shapes manually.
   - Risks/open questions: Confirm initial schema fields and whether to include migrations now or keep it simple with a bootstrap script.
   - Shared components/API contracts: New JSON API for project data and updates; DB access layer with portable SQL.

3. Stage 3 - Build the HTML shell to match the screenshot structure
   - Goal: Create the base layout (project selector, progress bar, four cards, questions area).
   - Dependencies: Stage 1 (routing/templating).
   - Expected changes: Add a single HTML page with named containers for each section.
   - Verification: Load the page and confirm layout regions match the screenshot.
   - Risks/open questions: None beyond layout fidelity.
   - Shared components/API contracts: New HTML structure used by JS rendering.

4. Stage 4 - Implement vanilla JS rendering and interactions
   - Goal: Populate UI from the API and enable adding items/questions.
   - Dependencies: Stages 2–3.
   - Expected changes: Add a JS module to fetch projects, update progress, render lists, and handle add-item actions.
   - Verification: Select a project, add items, and confirm updates appear without a page reload.
   - Risks/open questions: Handling optimistic vs confirmed updates if persistence is file-backed.
   - Shared components/API contracts: Uses the project API payloads; ensures front/back alignment.

5. Stage 5 - Apply CSS styling to match spacing and card visuals
   - Goal: Match the screenshot’s spacing, card layout, and progress bar appearance.
   - Dependencies: Stage 3 (HTML structure).
   - Expected changes: Add a single CSS file with layout rules for grid/cards/progress bar.
   - Verification: Visual check against the screenshot on desktop and mobile widths.
   - Risks/open questions: Cross-browser spacing differences may require minor adjustments.
   - Shared components/API contracts: None; frontend-only styling.

6. Stage 6 - Manual QA and documentation touch-up
   - Goal: Verify end-to-end flow and add brief usage notes.
   - Dependencies: Stages 1–5.
   - Expected changes: Update README or docs with run instructions and sample data notes.
   - Verification: Fresh start run-through on a clean server run.
   - Risks/open questions: None.
   - Shared components/API contracts: None.
