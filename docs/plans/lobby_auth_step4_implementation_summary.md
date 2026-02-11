## Stage 1 – Auth Data Model + Ledger Scaffold
- Changes: Added auth tables (accounts, public_keys, lobby_requests, ledger_events) and supporting DB helpers for accounts, keys, lobby requests, approvals, and ledger writes.
- Verification: Not run (requires app startup to create tables).
- Notes: Lobby requests start in `verifying` status and require signature verification before appearing in approvals.
