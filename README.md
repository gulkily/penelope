# North Star Dashboard

This project provides a lightweight FastAPI + vanilla HTML/CSS/JS dashboard for tracking North Star progress across projects.

## Local development
1. Create a virtual environment and install dependencies:
   - `python -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install -r requirements.txt`
2. Run the server:
   - `./start.sh`
3. Open `http://127.0.0.1:8000/`.

## Testing
1. Install Playwright dependencies:
   - `npm install`
   - `npx playwright install`
2. Start the server in a separate terminal:
   - `./start.sh`
3. Run tests:
   - `npm run test:e2e` (browser-driven E2E)
   - `npm run test:api` (HTTP-level integration)
   - `npm run test` (all Playwright tests)

## Data & persistence
- Default storage is SQLite at `data/north_star.db` (created automatically on first run).
- Override the database location with `DATABASE_URL` (use `sqlite:///path/to.db`).
- The seed data includes a few example projects and items to populate the UI.

## Notes
- Item additions use inline add rows; edit and delete are available per item with an undo toast.
- The North Star objective can be updated per project via the Save button.
- Progress updates happen immediately via the integrated slider.
- Questions auto-save while typing.
- Keyboard shortcuts: Enter submits add/edit, Shift+Enter inserts a newline, Escape cancels edits.
