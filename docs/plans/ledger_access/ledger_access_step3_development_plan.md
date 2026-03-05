# Ledger Access Step 3: Development Plan

1. **Stage 1: Ledger Query Surface**
   - Goal: Expose a read-only API endpoint for ledger entries.
   - Dependencies: Existing auth middleware.
   - Expected changes:
     - Add DB helper (e.g., `list_ledger_events(limit: int, offset: int) -> list[dict]`).
     - Add API route (e.g., `GET /api/auth/ledger`).
   - Verification approach: Manual curl to endpoint and confirm data shape.
   - Risks or open questions:
     - How to label approver/subject in the response (IDs vs display names).
   - Canonical components/API touched: Auth API router, DB module.

2. **Stage 2: Ledger Page UI**
   - Goal: Add a ledger page that lists approval events.
   - Dependencies: Stage 1.
   - Expected changes:
     - New template (e.g., `templates/ledger.html`).
     - New JS to fetch and render entries.
     - Add nav link to Ledger page.
   - Verification approach: Open ledger page and confirm entries render.
   - Risks or open questions:
     - Pagination or load limits for large ledgers.
   - Canonical components/API touched: Templates, static JS/CSS.

3. **Stage 3: Access Control + UX Polish**
   - Goal: Ensure only authenticated users can view ledger and UI is clear.
   - Dependencies: Stages 1–2.
   - Expected changes:
     - Reuse auth middleware or add route gating for `/ledger`.
     - Add empty-state copy when no approvals exist.
   - Verification approach: Check unauthenticated redirect and empty state behavior.
   - Risks or open questions:
     - Future admin role distinction (currently all authenticated users).
   - Canonical components/API touched: `app/main.py`, ledger UI assets.
