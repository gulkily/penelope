# PNL Magic Link Command - Step 2 Feature Description

## Problem
Admins can issue magic links in the web UI, but they need a fast command-line path to generate a link for a specific username during operational support and onboarding.

## User Stories
- As an admin, I want a `pnl` command that generates a magic link for a provided username so that I can issue access quickly from terminal workflows.
- As an operator, I want CLI-generated links to follow the same authorization and audit behavior as the existing web flow so that security and traceability remain consistent.
- As a maintainer, I want one canonical issuance path reused by both web and CLI so that future changes do not drift between interfaces.

## Core Requirements
- Add a `pnl` subcommand that accepts a target username and returns a generated magic link.
- Restrict issuance to admin-authorized contexts; non-admin attempts must fail with a clear error.
- Ensure CLI-generated links are functionally equivalent to web-issued links.
- Record issuance in the existing ledger/event trail.
- Provide command output that is copy-friendly for operators (link plus minimal metadata).

## Shared Component Inventory
- `./pnl` and `scripts/pnl.py`: extend as the canonical command surface for project operations.
- Existing magic-link issuance behavior (current web-admin path): reuse/extend as canonical business behavior rather than adding a separate rule set.
- Existing auth/admin gating and ledger event flow: reuse as the canonical access-control and audit mechanism.
- `README.md` and `AGENTS.md`: extend command documentation so CLI usage stays aligned with project conventions.

## Simple User Flow
1. Admin runs `./pnl ...` with a username argument.
2. System validates the operator context and input.
3. System issues a magic link via the shared issuance path.
4. Command prints the link and identifier for immediate use.

## Success Criteria
- Admin can generate a magic link for any valid username using a single `pnl` command.
- Non-admin or invalid invocation paths fail safely with actionable error output.
- CLI-issued links match web-issued link behavior.
- Ledger contains issuance records for CLI-generated links.
