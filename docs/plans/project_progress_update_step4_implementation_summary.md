## Stage 1 - Extend data layer and API for progress updates
- Changes: Added progress update schema, API endpoint, and data layer helper to persist progress updates.
- Verification: Not run yet; please start the server and `PUT /api/projects/{id}/progress` to confirm updates persist.
- Notes: Progress validation enforces 0-100 bounds via the request schema.
