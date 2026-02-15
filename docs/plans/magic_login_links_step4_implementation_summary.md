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
