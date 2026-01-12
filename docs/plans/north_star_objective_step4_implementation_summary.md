## Stage 1 - Extend SQLite data model for objective
- Changes: Added an objective column to projects, ensured legacy databases are migrated, seeded objectives, and exposed objective in the project payload.
- Verification: Manual (run the server and request `/api/projects/1` to confirm `objective` is present).
- Notes: Existing databases will default to an empty objective until updated.
