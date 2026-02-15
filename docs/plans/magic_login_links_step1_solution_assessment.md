# Magic Login Links (Preconfigured Username) — Step 1 Solution Assessment

## Problem Statement
Admins need to send one-click magic login links that log a user in with a preconfigured username, without manual lobby entry.

## Option A — Stateless Signed Link (No Stored Token State)
- Pros:
  - Fastest implementation path.
  - No new persistence model for link lifecycle.
  - Easy to generate links server-side with HMAC/JWT-style signing.
- Cons:
  - Cannot guarantee single-use (replay risk) without server-side state.
  - Revocation is limited once link is issued.
  - Weak auditability for “who used which link” events.

## Option B — Stored One-Time Invite Token (Admin-Issued, Short TTL)
- Pros:
  - Supports true one-click + single-use semantics.
  - Enables revocation, expiry, and clear audit trail for admin actions.
  - Cleanly binds link to intended username and controlled login behavior.
- Cons:
  - Requires new token lifecycle handling (issue/redeem/expire/revoke).
  - More backend and testing scope than a stateless link.

## Option C — Prefilled Lobby Link (Username Auto-Fill Only)
- Pros:
  - Lowest risk and smallest change set.
  - Reuses current lobby verification and approval flow.
  - Avoids introducing a new login primitive.
- Cons:
  - Not true one-click login (still requires lobby flow and approval).
  - Does not meet the stated admin expectation for magic login links.

## Recommendation
Option B. It is the only option that fully meets the one-click requirement while maintaining strong security properties (single-use, expiry, revocation, auditability) appropriate for admin-issued login links.
