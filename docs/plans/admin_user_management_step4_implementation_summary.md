## Stage 1 - Define read-only user roster data contract
- Changes:
  - Added `list_accounts(limit: int = 500, offset: int = 0) -> list[dict]` in `app/db_auth.py` with safe limit/offset bounds and deterministic username ordering.
  - Exported `list_accounts` through `app/db.py` for shared DB access.
  - Added `AdminUserListEntry` and `AdminUserListResponse` models in `app/schemas.py`.
- Verification:
  - Ran `python -c "from app.db import init_db, list_accounts, count_accounts; ..."` to confirm helper wiring and returned field keys (`id`, `username`, `created_at`).
- Notes:
  - Admin status is intentionally excluded from DB storage and will be derived at API time from existing auth logic.

## Stage 2 - Add admin-only users list API endpoint
- Changes:
  - Added `GET /api/auth/users` in `app/api_auth.py` with `_require_admin` authorization.
  - Wired pagination guardrails (`limit` bounded to `1..500`, non-negative `offset`).
  - Response now returns `entries`, `total`, `limit`, and `offset` with per-row `is_admin` derived from `auth.is_admin_account`.
- Verification:
  - Ran `python -c "from app.main import app; ..."` to confirm route registration for `/api/auth/users`.
  - Confirmed handler uses the existing admin guard and shared runtime admin logic path.
- Notes:
  - Per-entry admin derivation currently performs one admin check per account row (acceptable for current bounded page sizes).
