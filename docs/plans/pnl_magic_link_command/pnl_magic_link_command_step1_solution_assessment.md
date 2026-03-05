# PNL Magic Link Command - Step 1 Solution Assessment

## Problem Statement
Admins need a `pnl` command that generates a magic login link for a given username from the command line.

## Option A - `pnl` calls existing HTTP API (`POST /api/auth/magic-links`)
- Pros:
  - Reuses current authorization and auditing path.
  - Keeps one canonical magic-link issuance flow.
  - Minimal duplication of business logic.
- Cons:
  - Requires a running server.
  - Requires an authenticated admin session/cookie in CLI context.
  - More fragile local DX due to auth/session setup.

## Option B - `pnl` generates magic links directly via app DB/auth modules
- Pros:
  - Best CLI ergonomics (single local command).
  - No server/session dependency.
  - Works reliably for local and ops workflows.
- Cons:
  - Duplicates issuance path unless carefully shared.
  - Admin authorization is implicit from host access unless extra checks are added.
  - Must ensure ledger/audit parity with API behavior.

## Option C - New internal service used by both API and `pnl`
- Pros:
  - Single source of truth for issuance and ledger behavior.
  - Supports both web-admin and CLI-admin workflows.
  - Reduces long-term drift between API and CLI behavior.
- Cons:
  - Slightly larger initial refactor.
  - Requires touching both auth API and task-runner surfaces.

## Recommendation
Option C. It best matches the requirement while keeping long-term behavior consistent: one shared issuance path, surfaced through both the existing API and a new `pnl` command.
