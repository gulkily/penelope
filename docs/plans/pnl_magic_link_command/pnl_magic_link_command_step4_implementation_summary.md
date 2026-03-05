## Stage 1 - Extract shared magic-link issuance service
- Changes: Added `app/magic_link_service.py` with canonical `issue_magic_link(...)` and `build_magic_link(...)`; refactored `POST /api/auth/magic-links` in `app/api_auth.py` to reuse the shared service.
- Verification: Ran `python -m py_compile app/magic_link_service.py app/api_auth.py scripts/pnl.py`.
- Notes: API response contract remains unchanged (`token_id`, `configured_username`, `magic_link`, `expires_at`).

## Stage 2 - Define `pnl` command contract
- Changes: Added new task-runner subcommand `magic-link` in `scripts/pnl.py` with `--admin-username`, `--username`, and `--base-url`.
- Verification: Ran `./pnl --help` and `./pnl magic-link --help` to confirm command discovery and argument contract.
- Notes: `--base-url` defaults to `http://127.0.0.1:8000`.

## Stage 3 - Implement CLI admin authorization + issuance flow
- Changes: Implemented `run_magic_link_command(...)` in `scripts/pnl.py`:
  - resolves issuer account by username,
  - bootstraps issuer account when missing and no admin allowlist is configured,
  - enforces admin authorization via existing `auth.is_admin_account(...)`,
  - issues links through the shared service,
  - prints copy-friendly output (`issuer_username`, `target_username`, `token_id`, `magic_link`).
- Verification:
  - Created temp DB + accounts via Python snippet.
  - Ran success path:
    - `DATABASE_URL=sqlite:////tmp/pnl_magic_link_feature_test.sqlite MAGIC_LINK_ADMIN_USERNAMES=admin-user ./pnl magic-link --admin-username admin-user --username target-user --base-url http://localhost:8000`
  - Ran non-admin failure path:
    - `DATABASE_URL=sqlite:////tmp/pnl_magic_link_feature_test.sqlite MAGIC_LINK_ADMIN_USERNAMES=admin-user ./pnl magic-link --admin-username viewer-user --username target-user --base-url http://localhost:8000`
  - Confirmed token + ledger event persisted in temp DB.
- Notes: No server startup required for CLI issuance flow.

## Stage 4 - Regression coverage and docs updates
- Changes: Documented the new command in `README.md` and `AGENTS.md`.
- Verification: Manual doc check against `./pnl --help` command list.
- Notes: No automated test suite additions in this step; behavior validated with command-level smoke checks.
