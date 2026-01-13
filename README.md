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

## Task runner
- `./pnl venv` for virtual environment setup help.
- `./pnl install` to install dependencies.
- `./pnl start` to run the server.
- `./pnl test` to run all tests.
- `./pnl test e2e` or `./pnl test http` for focused test runs.
- `./pnl test e2e --headed` for visible browser runs.
- `./pnl test --workers 4` for parallel runs against a running server.
- `./pnl test --duration 60 --workers 2` for light load-style loops.
- `./pnl test --help` for test-specific options (looping, delay, parallelism, etc).
- `./pnl seed-demo` to add demo data (use `--allow-duplicates` if needed).

## Testing
1. Install test dependencies:
   - `pip install -r requirements.txt`
   - `python -m playwright install`
2. Start the server in a separate terminal:
   - `./start.sh`
3. Run tests:
   - `pytest tests/e2e` (browser-driven E2E)
   - `pytest tests/http` (HTTP-level integration)
   - `pytest` (all tests)
4. Optional: set `E2E_BASE_URL` to point at a non-default server.
5. Optional: run in parallel with `pytest -n 4` or `./pnl test --workers 4` (uses the current database).
6. Optional: loop tests with `./pnl test --loop 10 --workers 2` or `python scripts/run_e2e_loop.py 10 --workers 2`.

## Test coverage matrix
- See `docs/test_matrix.md` for frontend flow coverage and gaps.

## Data & persistence
- Default storage is SQLite at `data/north_star.db` (created automatically on first run).
- Override the database location with `DATABASE_URL` (use `sqlite:///path/to.db`).
- The seed data includes a few example projects and items to populate the UI.
- To add additional demo data, run `python scripts/seed_demo_data.py`.

## Notes
- Item additions use inline add rows; edit and delete are available per item with an undo toast.
- Project Management lists are paginated at 100 items per page with next/previous controls.
- Settings includes a database backup download for saving recovery copies.
- The North Star objective can be updated per project via the Save button.
- Progress updates happen immediately via the integrated slider.
- Questions auto-save while typing.
- Keyboard shortcuts: Enter submits add/edit, Shift+Enter inserts a newline, Escape cancels edits.
