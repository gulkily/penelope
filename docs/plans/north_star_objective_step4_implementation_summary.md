## Stage 1 - Extend SQLite data model for objective
- Changes: Added an objective column to projects, ensured legacy databases are migrated, seeded objectives, and exposed objective in the project payload.
- Verification: Manual (run the server and request `/api/projects/1` to confirm `objective` is present).
- Notes: Existing databases will default to an empty objective until updated.

## Stage 2 - Add API endpoint to update objective
- Changes: Added request schema and API route to update objectives per project.
- Verification: Manual (run the server and `PUT /api/projects/{id}/objective`, then re-fetch the project).
- Notes: Endpoint mirrors the questions update flow.
