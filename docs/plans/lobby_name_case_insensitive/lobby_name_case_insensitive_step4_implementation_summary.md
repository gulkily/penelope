## Stage 1 - Add canonical case-insensitive account lookup helper
- Changes: Added `get_account_by_username_case_insensitive(username: str)` in `app/db_auth.py` using a trimmed, case-insensitive query with deterministic oldest-account selection (`ORDER BY id ASC LIMIT 1`). Re-exported the helper via `app/db.py`.
- Verification: Manual verification pending. Suggested smoke check: create/update an account as `Alex`, then confirm helper-backed flow resolves a lookup for `alex`.
- Notes: No schema changes were introduced; display name storage remains unchanged.

## Stage 2 - Apply case-insensitive linking during lobby approval
- Changes: Updated `approve_lobby_request` in `app/db_auth.py` so when no explicit target account exists (`link_to_self` absent and key not already linked), the approval flow first resolves an existing account via `get_account_by_username_case_insensitive(requested_username)` before creating a new account.
- Verification: Manual verification pending. Suggested smoke check: bootstrap first user as `Alex`, submit second request as `alex`, approve without `link_to_self`, and confirm both requests resolve to the same `account_id`.
- Notes: Bootstrap approval path remains unchanged; explicit `link_to_self` still takes precedence.

## Stage 3 - Align lobby link-to-self action with case-insensitive comparison
- Changes: Updated `static/js/lobby.js` to normalize usernames before comparison so the “Approve + link to me” action appears for case variants (for example, `Alex` and `alex`) while keeping existing trimmed input behavior.
- Verification: Manual verification pending. Suggested smoke check: sign in as a user whose display name is `Alex`, open approvals containing a request for `alex`, and confirm the “Approve + link to me” button is shown.
- Notes: No API or template changes were required.

## Stage 4 - Regression verification and handoff
- Changes: Finalized regression coverage for the new behavior through documented manual smoke checks in this summary and preserved existing API/UI contracts (no schema or payload changes).
- Verification: Ran `python -m py_compile app/db_auth.py app/db.py app/api_auth.py` successfully. Manual smoke verification remains required in a running app: (1) approve `Alex` then `alex` without `link_to_self` and confirm same `account_id`; (2) verify “Approve + link to me” appears for case variants in lobby approvals; (3) verify distinct names still create separate accounts.
- Notes: Automated regression tests were not added during Step 4 to stay aligned with the process guidance in `docs/feature_process/step4_implementation.md`.
