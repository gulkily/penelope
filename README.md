# North Star Dashboard

This project provides a lightweight FastAPI + vanilla HTML/CSS/JS dashboard for tracking North Star progress across projects.

## Local development
1. Create a virtual environment and install dependencies:
   - `python -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install fastapi uvicorn`
2. Run the server:
   - `uvicorn app.main:app --reload`
3. Open `http://127.0.0.1:8000/`.

## Data & persistence
- Default storage is SQLite at `data/north_star.db` (created automatically on first run).
- Override the database location with `DATABASE_URL` (use `sqlite:///path/to.db`).
- The seed data includes a few example projects and items to populate the UI.

## Notes
- Item additions use a prompt dialog; questions auto-save while typing.
