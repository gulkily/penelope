# Lobby Auth Step 3: Development Plan

1. **Stage 1: Auth Data Model + Ledger Scaffold**
   - Goal: Add minimal persistence for accounts, public keys, lobby codes, and ledger events.
   - Dependencies: None.
   - Expected changes:
     - New auth DB module (e.g., `app/db_auth.py`) with functions like:
       - `create_account(initial_username: str) -> dict`
       - `add_public_key(account_id: int | None, public_key: str, fingerprint: str) -> dict`
       - `create_lobby_request(public_key_id: int, code: str, expires_at: str) -> dict`
       - `list_pending_lobby_requests() -> list[dict]`
       - `approve_lobby_request(request_id: int, approved_by_account_id: int) -> dict`
       - `reject_lobby_request(request_id: int, rejected_by_account_id: int) -> dict`
       - `link_key_to_account(public_key_id: int, account_id: int) -> None`
       - `update_username(account_id: int, new_username: str) -> dict`
       - `append_ledger_event(event_type: str, actor_account_id: int | None, subject_account_id: int | None, metadata: dict) -> None`
     - Extend `app/db_init.py` with new tables (conceptual: accounts, public_keys, lobby_requests, ledger_events).
   - Verification approach: Run app startup and confirm tables exist; manually insert/select via SQLite shell.
   - Risks or open questions:
     - How approvals link a key to an existing account vs new account (default behavior).
   - Canonical components/API touched: DB init, DB access module(s).

2. **Stage 2: Auth Utilities + Session Cookie Handling**
   - Goal: Centralize session creation/lookup and key fingerprinting.
   - Dependencies: Stage 1.
   - Expected changes:
     - New module (e.g., `app/auth.py`) with functions like:
       - `generate_fingerprint(public_key: str) -> str`
       - `verify_key_ownership(public_key: str, signature: str, challenge: str) -> bool`
       - `get_session_account(request: Request) -> dict | None`
       - `set_session_cookie(response: Response, account_id: int) -> None`
       - `clear_session_cookie(response: Response) -> None`
     - Add config for auth secret (env or settings file) used to sign/verify session cookies.
   - Verification approach: Manual call to a small test endpoint to set/clear cookies and read back session state.
   - Risks or open questions:
     - Session cookie format and whether signatures require additional client challenge.
   - Canonical components/API touched: new auth utility, request/response handling.

3. **Stage 3: Lobby/Public Auth API Endpoints**
   - Goal: Expose endpoints for lobby registration, status polling, approvals, and username changes.
   - Dependencies: Stages 1–2.
   - Expected changes:
     - New router (e.g., `app/api_auth.py`) with endpoints like:
       - `POST /api/auth/register` (username + public key, returns lobby code + request id)
       - `GET /api/auth/status` (by request id, returns approved/rejected/pending)
       - `GET /api/auth/lobby` (list pending requests for approved users)
       - `POST /api/auth/lobby/{request_id}/approve`
       - `POST /api/auth/lobby/{request_id}/reject`
       - `POST /api/auth/username` (update display name)
     - Response contracts include username, fingerprint, code, and status.
   - Verification approach: Curl through register → status → approve flow; ensure ledger rows are created.
   - Risks or open questions:
     - Public key format choice for compatibility (JWK vs SPKI PEM) and how to store it.
   - Canonical components/API touched: new auth API routes.

4. **Stage 4: Route Gating + Session Reset Page**
   - Goal: Enforce lobby-only access for guests and provide a recovery path when cookies are missing.
   - Dependencies: Stages 2–3.
   - Expected changes:
     - Add dependency or middleware to gate existing HTML routes and `/api/*` routes.
     - New route/page for session reset (clears cookie and redirects to lobby with instructions).
     - Update `app/main.py` to include the auth router and lobby page route.
   - Verification approach: Manually visit `/` with and without cookie to confirm redirect to lobby/reset flow.
   - Risks or open questions:
     - Ensuring static assets remain accessible to render the lobby.
   - Canonical components/API touched: `app/main.py`, existing HTML routes, all API routers.

5. **Stage 5: Lobby UI + Approval UI**
   - Goal: Provide the dedicated lobby page and approval list.
   - Dependencies: Stage 3.
   - Expected changes:
     - New `templates/lobby.html` plus JS/CSS in `static/` for:
       - Username prompt and key generation status.
       - Display of lobby code + approval status.
       - Approval queue UI (username, fingerprint, code, approve/reject).
   - Verification approach: Manual browser walkthrough with two sessions (guest + approved user).
   - Risks or open questions:
     - UX for linking a new key to an existing account vs new account creation.
   - Canonical components/API touched: new lobby template and static JS, existing styles.

6. **Stage 6: Client Keypair Generation + Persistence**
   - Goal: Implement browser-side keypair generation, fingerprinting, and storage.
   - Dependencies: Stage 5 (UI) and Stage 3 (API).
   - Expected changes:
     - New client JS module for WebCrypto keygen (P-256), storing private key in `localStorage` and public key in portable format.
     - Client signs a server challenge to prove key ownership for registration/session restore.
   - Verification approach: Confirm keys persist across reload and registration succeeds; verify signature failures reject.
   - Risks or open questions:
     - Browser support nuances for key export/import and signature encoding.
   - Canonical components/API touched: lobby JS, auth APIs.

7. **Stage 7: Test Coverage**
   - Goal: Add minimal tests for auth gating and lobby approval flows.
   - Dependencies: Stages 1–6.
   - Expected changes:
     - HTTP tests for register → approve → access flow and rejection behavior.
     - Gating test for anonymous access redirect to lobby.
   - Verification approach: `pytest tests/http` (app running) and spot-check with `./pnl test http`.
   - Risks or open questions:
     - Test setup for WebCrypto signing may need a mock path.
   - Canonical components/API touched: tests mirroring auth endpoints and route gating.
