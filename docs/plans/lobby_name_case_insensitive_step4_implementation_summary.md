## Stage 1 - Add canonical case-insensitive account lookup helper
- Changes: Added `get_account_by_username_case_insensitive(username: str)` in `app/db_auth.py` using a trimmed, case-insensitive query with deterministic oldest-account selection (`ORDER BY id ASC LIMIT 1`). Re-exported the helper via `app/db.py`.
- Verification: Manual verification pending. Suggested smoke check: create/update an account as `Alex`, then confirm helper-backed flow resolves a lookup for `alex`.
- Notes: No schema changes were introduced; display name storage remains unchanged.
