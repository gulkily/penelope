## Stage 1 – Progress history storage and helpers
- Changes: Added the `progress_history` table and index during DB init, introduced history read/write helpers, exported new DB functions, and documented the table in the Postgres migration guide.
- Verification: Not run (requires running the app and confirming the table and helpers work).
- Notes: Uses UTC ISO timestamps for recorded history entries.

## Stage 2 – Log history on progress updates
- Changes: Progress updates now record a timestamped history entry alongside the existing progress update.
- Verification: Not run (requires updating a resident's progress and checking a history entry is created).
- Notes: History is written in the same DB transaction as the progress update.

## Stage 3 – Progress history read endpoint
- Changes: Added response schemas and a `GET /api/projects/{project_id}/progress/history` endpoint that returns timestamped progress entries.
- Verification: Not run (requires calling the new endpoint after multiple progress updates).
- Notes: Response uses the existing project check and returns history in recorded timestamp order.
