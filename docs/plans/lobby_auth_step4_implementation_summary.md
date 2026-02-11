## Stage 1 – Auth Data Model + Ledger Scaffold
- Changes: Added auth tables (accounts, public_keys, lobby_requests, ledger_events) and supporting DB helpers for accounts, keys, lobby requests, approvals, and ledger writes.
- Verification: Not run (requires app startup to create tables).
- Notes: Lobby requests start in `verifying` status and require signature verification before appearing in approvals.

## Stage 2 – Auth Utilities + Session Cookie Handling
- Changes: Added `app/auth.py` for cookie signing, fingerprinting, stateless challenges, and signature verification. Added `cryptography` dependency.
- Verification: Not run (will verify once endpoints are wired).
- Notes: Session cookie uses a long-lived HMAC signature and is restored via stateless challenge signing.

## Stage 3 – Lobby/Public Auth API Endpoints
- Changes: Added `/api/auth` router for registration, verification, lobby listing, approvals, username updates, session restore, and current-user lookup. Added auth request/response schemas.
- Verification: Not run (needs app running to exercise endpoints).
- Notes: Registration issues a 14-day code and challenge; approvals can optionally link a key to the approver account.

## Stage 4 – Route Gating + Session Reset Page
- Changes: Added auth middleware and lobby/reset routes in `app/main.py`, plus a session reset template and JS to restore cookies.
- Verification: Not run (requires manual browser check).
- Notes: Unauthorized API calls return 401; browser routes redirect to `/session/reset`.

## Stage 5 – Lobby UI + Approval UI
- Changes: Added lobby template and client script for key generation, registration, status polling, approvals, and username updates. Extended main styles for lobby layout.
- Verification: Not run (requires manual browser check).
- Notes: Lobby auto-restores session when approval arrives; approvers can optionally link requests to themselves.

## Stage 6 – Client Keypair Generation + Persistence
- Changes: Implemented in lobby client script (WebCrypto P-256 keypair generation, localStorage persistence, challenge signing).
- Verification: Not run (requires manual browser check).
- Notes: Signatures are sent as raw WebCrypto ECDSA and verified server-side.

## Stage 7 – Test Coverage
- Changes: Not implemented (per Step 4 guidance to avoid adding automated tests during implementation).
- Verification: Not run.
- Notes: Manual verification is required for lobby flow, approvals, and session restore.

## Stage 8 – API Validation Polish
- Changes: Added input validation for unsupported public key formats and signature verification errors.
- Verification: Not run.
- Notes: Prevents 500s on malformed auth payloads.

## Stage 9 – Lobby Status Messaging
- Changes: Improved lobby status polling messages for verifying/pending/approved/rejected states.
- Verification: Not run.
- Notes: Keeps lobby status clearer while awaiting approval.
