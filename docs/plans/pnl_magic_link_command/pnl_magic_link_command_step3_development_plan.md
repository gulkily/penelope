# PNL Magic Link Command - Step 3 Development Plan

Database changes: none expected.
Sizing note: each stage is scoped to <=1 hour / <=50 lines where practical; split further if a stage grows.

1. Stage 1 - Extract shared magic-link issuance service
   - Goal: Create one canonical issuance path reused by both API and CLI.
   - Dependencies: Existing magic-link issuance logic and ledger event behavior.
   - Expected changes:
     - Add a shared service module for issuing links and returning the same response contract used today.
     - Refactor `POST /api/auth/magic-links` to call the shared service without changing external behavior.
     - Planned signatures:
       - `issue_magic_link(configured_username: str, issuer_account_id: int, base_url: str) -> dict`
   - Verification approach: Manual API smoke check confirms response shape and ledger event remain unchanged.
   - Risks/open questions:
     - Keep parity with current API semantics (token id, link format, event metadata).
   - Canonical components/API contracts touched: `app/api_auth.py`, `app/db_auth.py`, `app/auth.py`, ledger event flow.

2. Stage 2 - Define `pnl` command contract
   - Goal: Add a clear CLI interface for admins to issue links.
   - Dependencies: Existing `pnl` parser/dispatch architecture.
   - Expected changes:
     - Extend `scripts/pnl.py` and `./pnl` command help with a new `magic-link` subcommand.
     - Require explicit issuer identity via argument (for deterministic admin checks).
     - Planned command contract:
       - `./pnl magic-link --admin-username <issuer> --username <target>`
   - Verification approach: Manual `./pnl --help` and `./pnl magic-link --help` checks.
   - Risks/open questions:
     - Keep argument naming unambiguous (`admin` issuer vs target username).
   - Canonical components/API contracts touched: `scripts/pnl.py`, `pnl`.

3. Stage 3 - Implement CLI admin authorization + issuance flow
   - Goal: Enforce admin-only issuance in CLI context and generate links through the shared service.
   - Dependencies: Stage 1 service + Stage 2 command contract.
   - Expected changes:
     - Resolve issuer account by username from existing account lookup utilities.
     - Reuse existing admin policy (`MAGIC_LINK_ADMIN_USERNAMES` via `auth.is_admin_account`).
     - Issue link via shared service and print copy-friendly output (link and token id).
     - Planned signatures:
       - `run_magic_link_command(admin_username: str, target_username: str) -> int`
   - Verification approach: Manual CLI smoke checks for success path, non-admin issuer, and missing/unknown issuer.
   - Risks/open questions:
     - CLI execution context has no session cookie; issuer identity must be explicit and validated.
   - Canonical components/API contracts touched: `scripts/pnl.py`, `app/auth.py`, `app/db.py`, shared issuance service.

4. Stage 4 - Regression coverage and docs updates
   - Goal: Keep behavior reliable and discoverable.
   - Dependencies: Stages 1-3.
   - Expected changes:
     - Add focused tests for shared issuance service and CLI command result codes/messages.
     - Update docs with exact command usage and admin requirements.
   - Verification approach: Run targeted tests and one end-to-end manual command invocation.
   - Risks/open questions:
     - Test strategy should avoid requiring a running server for CLI coverage.
   - Canonical components/API contracts touched: `tests/`, `README.md`, `AGENTS.md`.
