# Supabase Backend Transition - Step 3 Development Plan

1. Stage 1 - Add backend selection and connection contract
   - Goal: Support SQLite and Supabase Postgres selection through `DATABASE_URL` without changing API routes.
   - Dependencies: `app/db_connection.py`, startup usage in `app/main.py`/`app/db.py`.
   - Expected changes: Introduce backend detection and a unified connection boundary used by all `app/db_*` modules.
   - Planned signatures: `resolve_database_backend(database_url: str | None) -> str`; `connect() -> ConnectionLike`; `get_database_backend() -> str`.
   - Verification: Start app once with SQLite URL and once with Supabase Postgres URL; confirm startup and basic `/api/projects` read succeed.
   - Risks/open questions:
     - Decide whether unsupported URL schemes fail fast at startup.
     - Confirm transaction/commit semantics stay consistent across drivers.
   - Shared components/API contracts touched: `app/db_connection.py`, `app/db.py` exports, existing `/api/*` contracts (no payload changes).

2. Stage 2 - Define Supabase-compatible schema/bootstrap behavior
   - Goal: Keep table/constraint expectations explicit for Postgres while avoiding SQLite-specific startup assumptions.
   - Dependencies: Stage 1, current startup initialization in `app/db_init.py`.
   - Expected changes: Split schema expectation checks from seed/bootstrap logic; keep startup behavior safe for both backends.
   - Planned signatures: `init_db() -> None`; `validate_required_schema() -> list[str]`; `seed_if_empty() -> None` (or equivalent internal boundary).
   - Verification: Run startup against Supabase with pre-created schema and confirm no destructive bootstrap side effects.
   - Risks/open questions:
     - Decide whether seed behavior is disabled by default for Supabase.
     - Confirm required table list includes auth/lobby/magic-link/import-map tables.
   - Shared components/API contracts touched: `app/db_init.py`, `app/main.py` startup hook.

3. Stage 3 - Port project/item/progress data access to backend-safe queries
   - Goal: Preserve dashboard/project behavior on Supabase without changing route contracts.
   - Dependencies: Stage 1-2.
   - Expected changes: Update `app/db_projects.py`, `app/db_items.py`, `app/db_progress_history.py`, and `app/db_houses.py` query patterns that assume SQLite behavior.
   - Verification: Manual smoke through dashboard/project management: list projects, create/archive resident, add/edit/delete/reorder items, update progress/objective/goal, view progress history.
   - Risks/open questions:
     - `COLLATE NOCASE` sort behavior parity may differ between backends.
     - If this stage exceeds ~50 lines, split by module before implementation.
   - Shared components/API contracts touched: `GET/POST/PUT /api/projects*`, `PUT/DELETE /api/items/*`, `GET /api/houses`.

4. Stage 4 - Port auth/lobby/magic-link/ledger data access to backend-safe queries
   - Goal: Keep current auth/admin operational flows unchanged on Supabase.
   - Dependencies: Stage 1-2.
   - Expected changes: Update `app/db_auth.py` operations for accounts, public keys, lobby requests, magic login tokens, and ledger events to be backend-safe.
   - Verification: Manual smoke for register/verify/status, lobby approve/reject, magic-link create/revoke/redeem bootstrap, users list + house update, and ledger listing.
   - Risks/open questions:
     - Case-insensitive username matching must remain equivalent.
     - If this stage exceeds ~50 lines, split by domain (`accounts/public_keys`, `lobby/magic`, `ledger`).
   - Shared components/API contracts touched: `app/api_auth.py` routes under `/api/auth/*`, `templates/lobby.html`, `templates/magic_links.html`, `templates/users.html`, `templates/ledger.html`.

5. Stage 5 - Preserve `/api/backup` behavior with backend-aware artifacts
   - Goal: Keep settings backup workflow usable after moving off local SQLite.
   - Dependencies: Stage 1.
   - Expected changes: Make backup generation backend-aware while keeping `GET /api/backup` as the canonical endpoint.
   - Planned signatures: `build_backup_artifact() -> tuple[str, str]` (path/content-type contract or equivalent).
   - Verification: From Settings, trigger backup and confirm downloadable artifact exists for both SQLite and Supabase configurations.
   - Risks/open questions:
     - Define expected backup format for Supabase-backed runs.
     - Ensure backup generation does not block normal app traffic.
   - Shared components/API contracts touched: `app/api.py` `GET /api/backup`, `static/js/settings.js`, `templates/settings.html`.

6. Stage 6 - Add one-time SQLite-to-Supabase migration utility and parity checks
   - Goal: Provide a repeatable cutover path for existing data.
   - Dependencies: Stage 2-4 (stable schema and data access assumptions).
   - Expected changes: Add a script/command that migrates in-scope tables and emits parity counts/check summaries.
   - Planned signatures: `migrate_sqlite_to_postgres(sqlite_url: str, postgres_url: str) -> MigrationReport`; `verify_parity(...) -> ParityReport`.
   - Verification: Run migration from a representative SQLite dataset, then validate table counts and sample records for projects/items/accounts/lobby/magic/ledger/progress.
   - Risks/open questions:
     - Define idempotency strategy for re-running migration safely.
     - Confirm handling for existing IDs and timestamp fidelity.
   - Shared components/API contracts touched: new migration script under `scripts/`, existing DB tables only (no API contract change).

7. Stage 7 - Expand test and environment coverage for Supabase backend mode
   - Goal: Ensure regression confidence before cutover.
   - Dependencies: Stage 1-6.
   - Expected changes: Add/update test fixtures and config guidance so HTTP/E2E suites can run against Supabase-backed environments.
   - Verification: Run `pytest tests/http` and targeted `pytest tests/e2e` smoke flows against Supabase mode and confirm parity with SQLite mode.
   - Risks/open questions:
     - Test runtime and data reset strategy for shared Supabase environments.
     - Secrets/config handling for CI or staging.
   - Shared components/API contracts touched: `tests/http`, `tests/e2e`, `README.md`/test docs as needed.

8. Stage 8 - Publish cutover and rollback runbook
   - Goal: Give developer/admin/PM clear operational steps for transition day.
   - Dependencies: Stage 1-7 outputs.
   - Expected changes: Add concise docs covering prerequisites, migration order, verification checklist, rollback to SQLite, and post-cutover monitoring checks.
   - Verification: Perform a dry-run walkthrough using the runbook on a staging-like environment.
   - Risks/open questions:
     - Define clear cutover go/no-go thresholds.
     - Assign ownership for rollback decision window.
   - Shared components/API contracts touched: `docs/` migration/runbook docs, `README.md` operational notes.
