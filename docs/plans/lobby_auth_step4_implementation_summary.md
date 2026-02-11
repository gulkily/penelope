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
