# Supabase Backend Transition - Step 2 Feature Description

Problem: The app currently depends on local SQLite, which limits managed backend operations and hosted deployment consistency. The team needs a database-only transition to Supabase Postgres while keeping existing product behavior unchanged.

User stories:
- As a developer, I want to switch persistence to Supabase Postgres behind the existing backend contracts so that frontend and API behavior stays stable.
- As an admin, I want dashboard, settings, users, lobby, magic-link, and ledger workflows to keep working the same way so that operations are not disrupted.
- As a PM, I want this transition scoped to backend persistence only so that timeline and risk remain predictable.
- As an operator, I want a clear rollback path during cutover so that incidents can be contained quickly.

Core requirements:
- Supabase Postgres can be used as the primary backend via environment configuration without changing user-facing routes.
- Existing API payload shapes, permissions, and page behaviors remain functionally equivalent for current workflows.
- Existing SQLite data can be moved to Supabase with validated record parity for active product tables.
- Authentication, lobby approvals, magic-link issuance/redemption, and ledger history remain intact after cutover.
- A documented fallback path to SQLite is available during the transition window.

Shared component inventory:
- `templates/index.html` + `static/js/app.js`: reuse as canonical dashboard UI; no new UI surface needed.
- `templates/manage_projects.html` + `static/js/manage-projects.js`: reuse project-management UI; no new UI surface needed.
- `templates/lobby.html`, `templates/welcome.html`, `templates/session_reset.html` + `static/js/lobby.js`/`static/js/session_reset.js`: reuse auth/lobby/session recovery surfaces; no new UI surface needed.
- `templates/settings.html`, `templates/magic_links.html`, `templates/users.html` + `static/js/settings.js`/`static/js/magic-links.js`/`static/js/users.js`: reuse admin settings surfaces; no new UI surface needed.
- `templates/ledger.html` + `static/js/ledger.js`: reuse ledger UI; no new UI surface needed.
- `app/api.py`: reuse canonical project/item/progress/backup/house APIs; behavior remains the same.
- `app/api_auth.py`: reuse canonical auth, lobby, users, magic-link, ledger, and session restore APIs; behavior remains the same.
- `app/api_transcript.py`: reuse transcript analysis and question-regeneration APIs; behavior remains the same.
- `app/db.py`, `app/db_connection.py`, and existing `app/db_*` modules: extend the canonical data-access boundary for Supabase-backed persistence.
- New shared component required: none (Option B keeps existing UI and API surfaces).

Simple user flow:
1. Developer configures the app to run against Supabase Postgres.
2. Admin/operator migrates current SQLite data and starts the app with the new backend.
3. Users continue normal dashboard/auth/admin workflows without UI changes.
4. PM/admin verifies key workflows and data integrity before declaring cutover complete.

Success criteria:
- `pytest tests/http` and `pytest tests/e2e` pass against the Supabase-backed environment.
- Critical workflows (project CRUD, item updates, progress history, lobby/auth, magic links, users, ledger) behave equivalently to current production behavior.
- Data parity checks confirm migrated Supabase records match the SQLite source for in-scope tables.
- No new user-facing page or API contract is required to complete the transition.
