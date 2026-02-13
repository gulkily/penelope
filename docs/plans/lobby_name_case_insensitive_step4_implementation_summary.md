## Stage 1 - Add canonical case-insensitive account lookup helper
- Changes: Added `get_account_by_username_case_insensitive(username: str)` in `app/db_auth.py` using a trimmed, case-insensitive query with deterministic oldest-account selection (`ORDER BY id ASC LIMIT 1`). Re-exported the helper via `app/db.py`.
- Verification: Manual verification pending. Suggested smoke check: create/update an account as `Alex`, then confirm helper-backed flow resolves a lookup for `alex`.
- Notes: No schema changes were introduced; display name storage remains unchanged.

## Stage 2 - Apply case-insensitive linking during lobby approval
- Changes: Updated `approve_lobby_request` in `app/db_auth.py` so when no explicit target account exists (`link_to_self` absent and key not already linked), the approval flow first resolves an existing account via `get_account_by_username_case_insensitive(requested_username)` before creating a new account.
- Verification: Manual verification pending. Suggested smoke check: bootstrap first user as `Alex`, submit second request as `alex`, approve without `link_to_self`, and confirm both requests resolve to the same `account_id`.
- Notes: Bootstrap approval path remains unchanged; explicit `link_to_self` still takes precedence.
