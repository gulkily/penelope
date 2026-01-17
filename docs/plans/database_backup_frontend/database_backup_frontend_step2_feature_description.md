# Database Backup from Frontend - Step 2 Feature Description

Problem: Users need a simple, frontend-triggered way to download a full database backup from a dedicated settings page so they can store it with the open-source project and recover from failures.

User stories:
- As a user, I want a one-click backup download from a settings page so that I can save a recovery copy quickly.
- As a maintainer, I want a dedicated settings page so that future admin controls (server settings, preferences) have a clear home.
- As a maintainer, I want backups to be full-fidelity so that restoration is straightforward.
- As an operator, I want the backup workflow to be clear and safe so that routine use does not risk data loss.

Core requirements:
- Provide a visible UI control on a settings page to trigger a backup download.
- Provide a dedicated settings page entry point from the UI.
- The backup includes the full database contents (not a partial export).
- The download uses a clear filename (including date or timestamp).
- The backup action does not interrupt normal app usage.
- The workflow is documented for users who store backups with the repo.

Shared component inventory:
- `templates/`: add a new settings page template that can host future controls.
- `static/js/`: add a settings page script for backup actions.
- `app/api.py`: reuse the API router for a backup download endpoint.
- `app/db_connection.py` (and related DB utilities): reuse the canonical database location logic.
- `README.md`: extend with backup usage guidance.

Simple user flow:
1. Open the Settings page.
2. Click “Download backup.”
3. Save the file to the project directory or preferred backup location.

Success criteria:
- A backup download can be triggered from the settings page in one step.
- The downloaded file contains the full database contents.
- The UI remains responsive during the backup operation.
- Users can follow documentation to store the backup alongside the repository.
