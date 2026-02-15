# Magic Login Links (Preconfigured Username) — Step 4 Implementation Summary

## Stage 1 - Define admin authorization + token lifecycle primitives
- Changes:
  - Added `magic_login_tokens` schema support and `lobby_requests.magic_token_id` linkage in `app/db_init.py`.
  - Added token lifecycle DB helpers in `app/db_auth.py` for create/lookup/attach/consume/revoke.
  - Added auth helpers in `app/auth.py` for token hashing and admin authorization via `MAGIC_LINK_ADMIN_USERNAMES`.
  - Updated `app/db.py` exports for the new auth/token data functions.
- Verification:
  - Ran `python -m compileall app` to confirm the updated modules compile.
- Notes:
  - Admin allowlist currently defaults to permissive behavior when `MAGIC_LINK_ADMIN_USERNAMES` is unset.

## Stage 2 - Add API contracts for issue/revoke and lobby bootstrap
- Changes:
  - Extended auth schemas in `app/schemas.py` with magic-link request/response models and optional `magic_token` on lobby register payloads.
  - Added admin issue endpoint `POST /api/auth/magic-links`, admin revoke endpoint `POST /api/auth/magic-links/{token_id}/revoke`, and public bootstrap endpoint `GET /api/auth/magic-links/bootstrap` in `app/api_auth.py`.
  - Added token classification helpers and admin authorization guard reuse for the new endpoints.
- Verification:
  - Ran `python -m compileall app` to confirm endpoint/schema updates compile.
- Notes:
  - Bootstrap endpoint returns non-sensitive token states (`usable|invalid|expired|revoked|used`) without exposing token internals.

## Stage 3 - Integrate token into existing register/verify session flow
- Changes:
  - Added atomic data-layer helper `approve_lobby_request_with_magic_token` in `app/db_auth.py` to consume token + approve request in one transaction boundary.
  - Updated `/api/auth/register` in `app/api_auth.py` to accept optional `magic_token`, validate it, and bind it to the lobby request while enforcing token-configured username.
  - Updated `/api/auth/verify` in `app/api_auth.py` to auto-approve verified requests with a bound magic token and return approved status without manual approver intervention.
- Verification:
  - Ran `python -m compileall app` to confirm register/verify and DB-layer updates compile.
- Notes:
  - Token auto-approval returns a conflict response when token state changes between register and verify.

## Stage 4 - Add one-click lobby entry UX for token links
- Changes:
  - Updated `static/js/lobby.js` to read `magic_token` from URL query params, call bootstrap validation, and auto-start the existing register+verify flow with token-bound username.
  - Added blocked-token messaging (`invalid|expired|revoked|used`) and failure-safe behavior that avoids auto-approval when bootstrap is not usable.
  - Added URL cleanup via `history.replaceState` so the token is removed from browser address/history after initial processing.
- Verification:
  - Ran `python -m compileall app` to confirm backend dependencies used by lobby flow remain valid.
- Notes:
  - Token flow now reuses the same key generation and challenge verification path as manual lobby onboarding.

## Stage 5 - Extend Settings UI for admin issue/revoke workflow
- Changes:
  - Added a new Settings card in `templates/settings.html` for magic link operations (configured username input, generate, copy, revoke, and latest-link display).
  - Reworked `static/js/settings.js` to support magic link issue/copy/revoke actions while preserving existing backup download behavior.
  - Added admin-friendly status/error messaging for unauthorized or failed issue/revoke calls.
- Verification:
  - Ran `python -m compileall app` to verify server-side template dependencies remain loadable.
- Notes:
  - Revoke action currently targets the most recently generated link in the current browser session.
