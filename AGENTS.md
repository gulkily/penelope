# Repository Guidelines

## Project Structure & Module Organization
- `app/` for FastAPI application code (routers, services, db).
- `static/` for vanilla HTML/CSS/JS assets.
- `templates/` if server-rendered HTML is used.
- `docs/plans/` for feature planning artifacts (Step 1–4).
- `FEATURE_DEVELOPMENT_PROCESS.md` in the repo root is the source of truth for the planning workflow.

If a different layout is introduced, update this guide and keep directory names stable.

## Build, Test, and Development Commands
No commands are standardized yet. Once tooling is added, keep this section current, for example:
- `uvicorn app.main:app --reload` for local development.
- `pytest` for tests.
- `python -m app.db.init` for local DB bootstrap if applicable.

## Coding Style & Naming Conventions
- Python: 4-space indentation, type hints where practical, `snake_case` for functions/modules, `PascalCase` for classes.
- JS/CSS/HTML: 2-space indentation, `kebab-case` for filenames, `data-*` attributes for JS hooks.
- Avoid third-party frontend frameworks (no React/Tailwind); use plain HTML/CSS/JS.
- Store HTML templates in separate files under `templates/`, not inline in Python.

## Data & Persistence
- Default database: SQLite (local dev), with an easy switch to Postgres via `DATABASE_URL`.
- Keep SQL portable and isolate DB access in a single module to ease migration.
- Avoid schema changes unless required; document any changes in `docs/`.

## Testing Guidelines
No test framework is set up yet. When added:
- Mirror structure between `app/` and `tests/`.
- Name tests by module and behavior (e.g., `tests/test_projects_api.py`).
- Add a single command to run all tests and a smaller command for focused runs.
- Do not start the server for manual testing; ask the user to run any manual verification steps.

## Commit & Pull Request Guidelines
- Use clear, scoped messages (e.g., `feat: add project selector`, `fix: handle empty questions`).
- Planning docs: do not commit Step 1–3 until explicitly approved.
- PRs should include a short summary, links to relevant issues, and screenshots for UI changes.
