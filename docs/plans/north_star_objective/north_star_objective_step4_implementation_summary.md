## Stage 1 - Extend SQLite data model for objective
- Changes: Added an objective column to projects, ensured legacy databases are migrated, seeded objectives, and exposed objective in the project payload.
- Verification: Manual (run the server and request `/api/projects/1` to confirm `objective` is present).
- Notes: Existing databases will default to an empty objective until updated.

## Stage 2 - Add API endpoint to update objective
- Changes: Added request schema and API route to update objectives per project.
- Verification: Manual (run the server and `PUT /api/projects/{id}/objective`, then re-fetch the project).
- Notes: Endpoint mirrors the questions update flow.

## Stage 3 - Add objective display and edit UI
- Changes: Added objective input and save action in the dashboard markup; wired client-side save via the objective endpoint.
- Verification: Manual (select a project, edit objective, click save, then reload and reselect).
- Notes: Objective input is disabled until a project is selected.

## Stage 4 - Styling and layout refinement
- Changes: Styled the objective section and save button to match the dashboard controls.
- Verification: Manual (check the objective area alignment on desktop and mobile widths).
- Notes: Objective section uses the existing form field styles for consistency.
