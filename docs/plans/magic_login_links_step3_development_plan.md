# Magic Login Links (Preconfigured Username) — Step 3 Development Plan

Database changes: add a dedicated magic-login token store (single-use metadata + status timestamps) and a linkage from lobby requests to an optional magic token so the existing register/verify path can auto-approve when appropriate.
Sizing note: each stage is scoped to roughly <=1 hour of work; if implementation exceeds ~50 lines or broadens behavior, split into a follow-up stage before coding further.

1. Stage 1 - Define admin authorization + token lifecycle primitives
   - Goal: Add secure issuance/revocation/lookup primitives for magic tokens without changing normal lobby behavior.
   - Dependencies: Existing auth/session utilities and `accounts`/`ledger_events` model.
   - Expected changes:
     - Add configurable admin check helper in auth layer (for "admin-only" issuance path).
     - Add DB helpers for token lifecycle (issue, lookup by token hash, consume, revoke, expiry checks).
     - Add DB helper to associate a validated token with a lobby request created by `/api/auth/register`.
     - Planned signatures:
       - `is_admin_account(account_id: int) -> bool`
       - `create_magic_login_token(configured_username: str, created_by_account_id: int, expires_at: str, token_hash: str) -> dict`
       - `get_magic_login_token_by_hash(token_hash: str) -> dict`
       - `attach_magic_token_to_lobby_request(request_id: str, token_id: str) -> None`
       - `consume_magic_login_token(token_id: str, request_id: str, account_id: int) -> dict`
       - `mark_magic_login_token_revoked(token_id: str, actor_account_id: int) -> dict`
   - Verification approach: Manual DB/API smoke check that tokens can be issued, resolved, attached to a request, consumed once, and revoked.
   - Risks/open questions:
     - "Admin" source of truth should be fixed before implementation starts (env allowlist for now, role model as future enhancement).
     - This stage may exceed the line-size target if role modeling is introduced; split role-modeling into a follow-up stage if needed.
   - Canonical components/API contracts touched: `app/auth.py`, `app/db_auth.py`, `app/db.py`, `app/db_init.py`.

2. Stage 2 - Add API contracts for issue/revoke and lobby bootstrap
   - Goal: Expose admin token issuance controls and keep recipient flow on existing lobby endpoints.
   - Dependencies: Stage 1 lifecycle/auth helpers.
   - Expected changes:
     - Extend schemas for magic-link issuance/revocation payloads and responses.
     - Add admin-only issuance endpoint and revoke endpoint in `app/api_auth.py`.
     - Add optional bootstrap endpoint to validate incoming token and return configured username for lobby auto-start.
     - Planned signatures:
       - `POST /api/auth/magic-links` (admin): input configured username (+ optional ttl), output full link + expires_at.
       - `POST /api/auth/magic-links/{token_id}/revoke` (admin): revoke unconsumed token.
       - `GET /api/auth/magic-links/bootstrap?token=...` (public): return usable/blocked state and configured username when usable.
   - Verification approach: Manual HTTP checks for unauthorized issuer, valid issuance, revoked/expired bootstrap state, and non-leaky errors.
   - Risks/open questions:
     - Ensure bootstrap and error responses do not expose token internals.
   - Canonical components/API contracts touched: `app/api_auth.py`, `app/schemas.py`, `/api/auth/*`.

3. Stage 3 - Integrate token into existing register/verify session flow
   - Goal: Keep key creation + challenge verification intact while auto-approving requests that carry a valid magic token.
   - Dependencies: Stages 1-2 plus existing `/api/auth/register` and `/api/auth/verify` flow.
   - Expected changes:
     - Extend `AuthRegisterRequest` with optional `magic_token`.
     - In `/api/auth/register`, when `magic_token` is present and valid, bind token to the newly created lobby request and use token-configured username.
     - In `/api/auth/verify`, after key ownership verification, auto-approve linked requests when token is valid and consume token atomically.
     - Continue using existing `/api/auth/session/restore` for final cookie creation.
   - Verification approach: Manual browser flow that opens magic link, generates key, verifies challenge, transitions to approved without manual approver action, then restores session.
   - Risks/open questions:
     - Consumption and approval must be atomic to prevent replay/race conditions.
   - Canonical components/API contracts touched: `app/api_auth.py`, `app/schemas.py`, `app/db_auth.py`, `templates/lobby.html`, `static/js/lobby.js`.

4. Stage 4 - Add one-click lobby entry UX for token links
   - Goal: Clicking the link starts the normal lobby flow automatically with preconfigured username and no manual approval queue dependency.
   - Dependencies: Stages 2-3.
   - Expected changes:
     - Update `templates/lobby.html` and `static/js/lobby.js` to read token from URL query params.
     - Use bootstrap response to prefill/lock configured username and auto-trigger register+verify flow when token is usable.
     - On blocked token (expired/revoked/used), show explicit failure message and do not attempt approval.
   - Verification approach: Manual browser checks for valid-token auto-start and blocked-token failure states.
   - Risks/open questions:
     - Token should be removed from address bar/history after initial processing.
   - Canonical components/API contracts touched: `templates/lobby.html`, `static/js/lobby.js`, `static/css/main.css`.

5. Stage 5 - Extend Settings UI for admin issue/revoke workflow
   - Goal: Give admins in-app controls to generate and optionally revoke one-click links.
   - Dependencies: Stage 2 endpoints.
   - Expected changes:
     - Extend `templates/settings.html` with magic-link card (configured username input, generate action, link output, revoke action for latest link).
     - Extend `static/js/settings.js` for issue/revoke calls and copy-to-clipboard support.
   - Verification approach: Manual settings flow with admin and non-admin sessions.
   - Risks/open questions:
     - Keep first iteration minimal to stay within stage-size budget.
   - Canonical components/API contracts touched: `templates/settings.html`, `static/js/settings.js`, `static/css/main.css`.

6. Stage 6 - Ledger instrumentation, hardening, and regression coverage
   - Goal: Preserve auditability and enforce secure single-use semantics across the full flow.
   - Dependencies: Stages 1-5.
   - Expected changes:
     - Record ledger events for issue, bootstrap blocked, auto-approval, token consume, and revoke actions.
     - Enforce TTL/single-use/revocation checks at both bootstrap and verify boundaries.
     - Add focused tests for admin-only issuance, valid token auto-approval, replay rejection, expiry rejection, and revoke behavior.
     - Update docs with issuer workflow, recipient one-click flow, and admin config source.
   - Verification approach: Run focused HTTP/e2e tests plus one manual end-to-end smoke path.
   - Risks/open questions:
     - Rate limiting may need a follow-up if issuance/bootstrap abuse becomes a concern.
   - Canonical components/API contracts touched: `app/api_auth.py`, `app/db_auth.py`, `/api/auth/ledger`, `tests/`, `README.md`, `docs/`.
