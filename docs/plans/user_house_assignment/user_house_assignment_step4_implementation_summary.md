# User House Assignment - Step 4 Implementation Summary

## Stage 1 - Account house persistence and migration
- Changes:
  - Added account-level `house` persistence to the `accounts` schema (create + ensure-column path).
  - Added `houses` table bootstrap/seed flow and startup backfill for existing account houses.
  - Added `app/db_houses.py` and `app.house.list_houses()` so house normalization is driven from DB-backed options.
- Verification:
  - Ran `python3 -m compileall app scripts` (pass).
  - Ran a temp-DB check (`DATABASE_URL=sqlite:////tmp/penelope_houses_dynamic_verify.db`) confirming seeded houses and dynamic normalization against DB values.
- Notes:
  - `normalize_house` now validates against the `houses` table; removing legacy house names from DB intentionally makes them invalid.

## Stage 2 - Magic-link issuance house assignment contract
- Changes:
  - Extended magic-link request/response contracts to include house assignment and placeholder-account creation metadata.
  - Updated shared magic-link service to:
    - create placeholder accounts when target username is new,
    - update existing account house when username already exists,
    - return `assigned_house` and `account_created`.
  - Updated CLI `./pnl magic-link` to support `--house` and print assigned house/create status.
- Verification:
  - Ran `python3 scripts/pnl.py magic-link --help` to confirm CLI contract.
  - Ran an isolated temp-DB script proving:
    - first issue for new username creates account + house,
    - second issue for same username updates existing house.
- Notes:
  - Existing-user house overwrite during issuance is intentional per approved scope.

## Stage 3 - Admin API for user house management
- Changes:
  - Extended `GET /api/auth/users` entries to include `house`.
  - Added admin-only `PUT /api/auth/users/{account_id}/house`.
  - Added ledger event logging for explicit user house updates.
  - Added `GET /api/houses` for DB-backed house option retrieval across UI surfaces.
- Verification:
  - Imported and called `get_houses()` directly in Python to confirm response shape and dynamic data.
  - Re-ran Python compilation after API/schema updates (pass).
- Notes:
  - House-update endpoint currently allows updates for both admin and non-admin accounts (as requested).

## Stage 4 - Users page house dropdown assignment
- Changes:
  - Converted Users page from read-only list to editable per-row house dropdown.
  - Users UI now loads house options from `/api/houses` (not hard-coded).
  - Hooked dropdown changes to `PUT /api/auth/users/{account_id}/house` with inline status/error handling.
- Verification:
  - Static JS wiring validated by build-time parse checks and endpoint contract consistency.
- Notes:
  - Manual browser validation still needed in running app to confirm final interaction flow.

## Stage 5 - Magic-links page house selector + existing-user prefill
- Changes:
  - Added house selector to magic-link generation form.
  - Selector options now load from `/api/houses` (DB-backed).
  - Added existing-user house prefill based on username match from admin users API.
  - Magic-link status messaging now reflects whether account was created vs updated.
- Verification:
  - Verified new request contract alignment between frontend payload and backend schema/service.
  - Verified CLI and API contracts both include house assignment behavior.
- Notes:
  - Username-match prefill is exact case-insensitive trimmed match against loaded user roster.

## Stage 6 - Dashboard house selector hidden for non-admin
- Changes:
  - Updated dashboard template to render house filter only for admin sessions.
  - Added `data-can-filter-houses` session flag and frontend gating.
  - Added server-side house scoping in `GET /api/projects` for non-admin sessions, forcing project list results to the signed-in account's house.
  - Non-admin dashboard path keeps selector hidden and uses server-scoped list results for resident selection.
  - Refactored dashboard and resident-management house selectors to load options from `/api/houses`.
- Verification:
  - Verified template and script gating logic alignment in code paths.
  - Ran a temp-DB API smoke script showing non-admin list responses are house-scoped even when querying another house.
  - Verified no hard-coded house option strings remain in frontend templates/scripts.
- Notes:
  - House scoping is currently enforced on project-list responses; direct single-project access rules were not changed in this pass.

## Stage 7 - Final regression checks and docs
- Changes:
  - Updated README command/docs for house assignment at magic-link issuance.
  - Documented DB-backed house option sourcing in Notes.
  - Added Step 4 implementation summary with stage outcomes.
- Verification:
  - Ran `python3 -m compileall app scripts` after final changes (pass).
  - Ran `python3 scripts/pnl.py --help` and `python3 scripts/pnl.py magic-link --help` (pass).
  - Ran targeted Python smoke scripts for:
    - dynamic house-list behavior from DB,
    - magic-link placeholder creation + existing-user house update behavior.
- Notes:
  - I did not run browser manual smoke or full E2E/HTTP suites in this environment.
