## Stage 1 – Add a settings page shell
- Changes: Added `/settings` route and new `templates/settings.html` with a backup section plus navigation links from dashboard/manage pages.
- Verification: Not run here (requires loading `/settings` in a browser).
- Notes: Settings page uses shared styling and theme toggle.

## Stage 2 – Implement backup download endpoint
- Changes: Added `GET /api/backup` to return the SQLite file with a timestamped filename, plus a shared DB path helper in `app/db_connection.py`.
- Verification: Not run here (requires running the server and requesting the endpoint).
- Notes: Endpoint returns a 404 if the database file is missing.

## Stage 3 – Wire backup UI on settings page
- Changes: Added backup download UI to `templates/settings.html` plus `static/js/settings.js` to fetch and download the backup, with basic status messaging and error styling in `static/css/main.css`.
- Verification: Not run here (requires loading `/settings` and clicking the backup button).
- Notes: Uses the API-provided filename when available.

## Stage 4 – Document backup usage
- Changes: Documented the Settings backup entry point in `README.md`.
- Verification: Not run here (documentation update only).
- Notes: None.
