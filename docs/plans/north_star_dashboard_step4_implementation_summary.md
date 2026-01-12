## Stage 1 - Establish FastAPI app skeleton and static serving
- Changes: Added FastAPI app entrypoint, template rendering, and static file mounting; created base template and static placeholder.
- Verification: Started `uvicorn app.main:app` and fetched `/` successfully.
- Notes: Static and template directories are in place for later stages.

## Stage 2 - Define data model and API contracts with SQLite-backed storage
- Changes: Added SQLite-backed data layer, API router, and request schemas; initialized schema with seed data; exposed JSON API routes; isolated DB config via `DATABASE_URL`.
- Verification: Started `uvicorn app.main:app`, requested `/api/projects`, and fetched `/api/projects/1`.
- Notes: SQLite is the default; non-sqlite `DATABASE_URL` will raise an error until Postgres support is added.

## Stage 3 - Build the HTML shell to match the screenshot structure
- Changes: Created the dashboard layout with project selector, progress bar, four section cards, and questions area.
- Verification: Started `uvicorn app.main:app` and loaded `/` in the browser.
- Notes: CSS and JS hooks are stubbed for later stages.
