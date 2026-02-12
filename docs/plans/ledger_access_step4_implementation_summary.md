## Stage 1 – Ledger Query Surface
- Changes:
- Verification:
- Notes:

## Stage 1 – Ledger Query Surface
- Changes: Added ledger DB helpers and `/api/auth/ledger` endpoint with pagination and metadata parsing.
- Verification: Not run.
- Notes: Response includes actor/subject usernames when available.

## Stage 2 – Ledger Page UI
- Changes: Added ledger page template, client script to fetch/render entries, and nav links to the Ledger page.
- Verification: Not run.
- Notes: Ledger uses existing table styling for consistent layout.

## Stage 3 – Access Control + UX Polish
- Changes: Added `/ledger` route; access is gated by existing auth middleware. Added empty-state copy on the ledger page.
- Verification: Not run.
- Notes: Ledger page relies on standard auth redirect when unauthenticated.
