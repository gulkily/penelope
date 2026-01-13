# Database Backup from Frontend - Step 3 Development Plan

1. Stage 1 - Add a settings page shell
   - Goal: Introduce a dedicated settings page to host backup and future controls.
   - Dependencies: Existing routing in `app/main.py` and templates structure.
   - Expected changes: Add a new route and template (e.g., `/settings` -> `templates/settings.html`) with shared layout and navigation back to the dashboard.
   - Verification: Start the app and load `/settings` to confirm the page renders.
   - Risks/open questions: Decide where to link to the settings page from the main UI.
   - Shared components/API contracts touched: `app/main.py`, `templates/`.

2. Stage 2 - Implement backup download endpoint
   - Goal: Provide an API endpoint that returns a full database backup file.
   - Dependencies: Database location logic in `app/db_connection.py` and FastAPI routing in `app/api.py`.
   - Expected changes: Add an endpoint (e.g., `GET /api/backup`) that streams or returns the SQLite file with a timestamped filename; ensure it is read-only and does not lock writes longer than necessary.
   - Planned signatures: `GET /api/backup`.
   - Verification: With the server running, hit the endpoint and confirm the file downloads.
   - Risks/open questions: Confirm safe file access under concurrent writes; decide whether to gate access (if needed).
   - Shared components/API contracts touched: `app/api.py`, `app/db_connection.py`.

3. Stage 3 - Wire backup UI on settings page
   - Goal: Add a backup download control to the settings page.
   - Dependencies: Stage 1–2.
   - Expected changes: Add a button or link on `settings.html` that triggers the download; add a small JS helper to call the endpoint and handle errors.
   - Verification: Click the backup control and confirm a file download starts.
   - Risks/open questions: Decide on UI messaging for download success/failure.
   - Shared components/API contracts touched: `templates/settings.html`, new `static/js/settings.js` (or similar).

4. Stage 4 - Document backup usage
   - Goal: Make the backup flow discoverable.
   - Dependencies: Stage 1–3.
   - Expected changes: Update `README.md` (and `AGENTS.md` if needed) with backup instructions and the settings page entry point.
   - Verification: Review docs for accuracy and clarity.
   - Risks/open questions: Ensure documentation aligns with the actual backup filename and location.
   - Shared components/API contracts touched: `README.md`, `AGENTS.md`.
