## Stage 1 – Add a settings page shell
- Changes: Added `/settings` route and new `templates/settings.html` with a backup section plus navigation links from dashboard/manage pages.
- Verification: Not run here (requires loading `/settings` in a browser).
- Notes: Settings page uses shared styling and theme toggle.

## Stage 2 – Implement backup download endpoint
- Changes: Added `GET /api/backup` to return the SQLite file with a timestamped filename, plus a shared DB path helper in `app/db_connection.py`.
- Verification: Not run here (requires running the server and requesting the endpoint).
- Notes: Endpoint returns a 404 if the database file is missing.
