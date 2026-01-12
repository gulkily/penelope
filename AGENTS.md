# Repository Guidelines

## Project Structure & Module Organization
- `app/` for FastAPI application code (routers, services, db).
- `static/` for vanilla HTML/CSS/JS assets.
- `templates/` if server-rendered HTML is used.
- `docs/plans/` for feature planning artifacts (Step 1–4).
- `FEATURE_DEVELOPMENT_PROCESS.md` in the repo root is the source of truth for the planning workflow.

If a different layout is introduced, update this guide and keep directory names stable.

## Build, Test, and Development Commands
- `./start.sh` for local development.
- `pip install -r requirements.txt` to install Python dependencies.
- `python -m playwright install` to download Playwright browser binaries.
- `pytest tests/e2e` for browser-driven E2E tests (requires the app to be running).
- `pytest tests/http` for HTTP-level integration tests (requires the app to be running).
- `pytest` to run all tests.
- Do not use npm; use Python tooling for tests and scripts.
- Task runner:
  - `./pnl venv` for virtual environment setup help.
  - `./pnl install` to install dependencies.
  - `./pnl start` to run the server.
- `./pnl test` to run all tests.
- `./pnl test e2e` or `./pnl test http` for focused test runs.
- `./pnl test e2e --headed` for visible browser runs.

## Coding Style & Naming Conventions
- Python: 4-space indentation, type hints where practical, `snake_case` for functions/modules, `PascalCase` for classes.
- JS/CSS/HTML: 2-space indentation, `kebab-case` for filenames, `data-*` attributes for JS hooks.
- Avoid third-party frontend frameworks (no React/Tailwind); use plain HTML/CSS/JS.
- Store HTML templates in separate files under `templates/`, not inline in Python.
- Keep Python modules under ~200 lines; refactor into additional files when they grow beyond that.

## Data & Persistence
- Default database: SQLite (local dev), with an easy switch to Postgres via `DATABASE_URL`.
- Keep SQL portable and isolate DB access in a single module to ease migration.
- Avoid schema changes unless required; document any changes in `docs/`.

## Testing Guidelines
- Test framework: pytest + Playwright.
- Mirror structure between `app/` and `tests/` where practical.
- Name tests by module and behavior (e.g., `tests/http/test_projects_api.py`).
- Add a single command to run all tests and a smaller command for focused runs.
- Do not start the server for manual testing; ask the user to run any manual verification steps.

## Commit & Pull Request Guidelines
- Use clear, scoped messages (e.g., `feat: add project selector`, `fix: handle empty questions`).
- Planning docs: do not commit Step 1–3 until explicitly approved.
- PRs should include a short summary, links to relevant issues, and screenshots for UI changes.
