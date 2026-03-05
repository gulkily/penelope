# Lobby Name Case-Insensitive Login — Step 3 Development Plan

1. Stage 1: Add canonical case-insensitive account lookup in DB helpers
   - Goal: Provide one backend helper that resolves an account by username without casing differences.
   - Dependencies: Existing auth tables and `app/db_auth.py` account queries.
   - Expected changes:
     - Add helper signature: `get_account_by_username_case_insensitive(username: str) -> dict`.
     - Export helper through `app/db.py`.
     - Keep display name storage unchanged (no schema/migration changes).
   - Verification approach: Unit-level check (or targeted API test) confirming `Alex` lookup finds `alex` account.
   - Risks/open questions:
     - Existing duplicate historical accounts that differ only by casing should resolve deterministically (oldest account id first).
   - Canonical components/API contracts touched: `app/db_auth.py`, `app/db.py`.

2. Stage 2: Apply case-insensitive linking during lobby approval
   - Goal: Prevent duplicate account creation when a pending request username matches an existing account by case-insensitive comparison.
   - Dependencies: Stage 1 helper; existing `approve_lobby_request` path.
   - Expected changes:
     - Update approval decision path in `app/db_auth.py` so `Approve` links to existing matched account before creating a new account.
     - Keep existing explicit `link_to_self` behavior intact, but ensure fallback matching still applies when not linking to self.
     - Preserve ledger behavior and response contracts.
   - Verification approach: API-level flow where first user is `Alex`, second request is `alex`; approval should return same `account_id`.
   - Risks/open questions:
     - Need to avoid changing bootstrap-first-account behavior.
   - Canonical components/API contracts touched: `app/db_auth.py`, `app/api_auth.py`, `/api/auth/lobby/{request_id}/approve`.

3. Stage 3: Align lobby UI “link to me” affordance with case-insensitive comparison
   - Goal: Keep frontend action visibility consistent with backend matching semantics.
   - Dependencies: Existing `loadCurrentUser` + approval list rendering.
   - Expected changes:
     - Update lobby client comparison to treat `currentUsername` and `requested_username` as case-insensitive when showing “Approve + link to me”.
     - Reuse existing markup/actions; no template or API contract changes.
   - Verification approach: Manual lobby smoke check showing link button for `Alex` vs `alex`.
   - Risks/open questions:
     - Whitespace handling should remain trimmed as today.
   - Canonical components/API contracts touched: `static/js/lobby.js`, `/api/auth/lobby`.

4. Stage 4: Add regression coverage for case-insensitive linking
   - Goal: Lock behavior to prevent reintroducing case-sensitive duplicate account creation.
   - Dependencies: Stages 1–3.
   - Expected changes:
     - Add focused test(s) under `tests/http/` or `tests/` to validate:
       - `Approve` links `Alex` and `alex` to one account.
       - Distinct non-matching names still create separate accounts.
     - Keep test setup compatible with existing local test workflow.
   - Verification approach: Run targeted pytest command for new test module, then full `pytest` if practical.
   - Risks/open questions:
     - Existing test suite currently leans on running app instances; may need lightweight isolated test scaffolding for auth flow.
   - Canonical components/API contracts touched: `tests/`, `app/api_auth.py`, `app/db_auth.py`.

