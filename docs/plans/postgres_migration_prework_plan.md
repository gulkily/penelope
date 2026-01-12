# Postgres Migration Prework Plan

1. Isolate database access
   - Goal: Keep all SQL and connection logic in a single module.
   - Action: Ensure all DB reads/writes flow through `app/db.py` (or a dedicated data layer).

2. Introduce migrations early
   - Goal: Track schema changes explicitly.
   - Action: Add Alembic and create an initial migration for `projects` and `items`.

3. Make seeding explicit
   - Goal: Avoid implicit schema/data changes on app startup.
   - Action: Move seed data into a separate `app/db_seed.py` (or `python -m app.db.seed`) script.

4. Standardize configuration
   - Goal: Make backend switching trivial.
   - Action: Use `DATABASE_URL` as the only DB selector; document expected formats.

5. Add a repository layer
   - Goal: Keep API handlers DB-agnostic.
   - Action: Introduce small, named functions for each data operation (already mostly present).

6. Add a smoke test script
   - Goal: Validate read/write flows against any backend.
   - Action: Create a simple script that hits list/get/add/edit/delete endpoints.

7. Document schema expectations
   - Goal: Keep schema consistent across SQLite and Postgres.
   - Action: Add a short schema overview in `docs/` (tables, columns, constraints).

8. Avoid SQLite-only behavior
   - Goal: Prevent migration surprises.
   - Action: Replace or guard SQLite-specific behavior (PRAGMA, implicit typing).
