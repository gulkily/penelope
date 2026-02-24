## Stage 1 - Define read-only user roster data contract
- Changes:
  - Added `list_accounts(limit: int = 500, offset: int = 0) -> list[dict]` in `app/db_auth.py` with safe limit/offset bounds and deterministic username ordering.
  - Exported `list_accounts` through `app/db.py` for shared DB access.
  - Added `AdminUserListEntry` and `AdminUserListResponse` models in `app/schemas.py`.
- Verification:
  - Ran `python -c "from app.db import init_db, list_accounts, count_accounts; ..."` to confirm helper wiring and returned field keys (`id`, `username`, `created_at`).
- Notes:
  - Admin status is intentionally excluded from DB storage and will be derived at API time from existing auth logic.
