# Lobby Auth Discovery Notes

## Scope Summary
This document captures the Q&A from discovery so the decisions are not lost across sessions.

## Questions And Answers
1. Keypair generation and storage: Generate in browser, store in `localStorage`. Disposable keys are allowed; multiple keypairs can link to the same identity/account.
2. Session verification concept: Half-authenticated users stay in a lobby until another authenticated user approves them. A 6-digit code is shown to the waiting user and to approvers.
3. Username handling: Prompted before access. Stored on the server and initialized from the user’s entry. Users can later change it. Duplicate usernames are allowed.
4. Access policy: Guests are limited to the lobby only. Dedicated lobby page is required.
5. Approval policy: Anyone already approved can approve others, and newly approved users can approve immediately. Approvals are recorded in a ledger.
6. Lobby code behavior: Code is linked to a specific public key. Multiple codes can be active in parallel for multiple devices. Code expires after 14 days.
7. Session lifetime: Session never expires. Use `localStorage` plus a session cookie. If cookie is missing, a page should reset the cookie and redirect.
8. Public key upload timing: Public key is sent to the server immediately.
9. Algorithm choice: Prefer the widely supported algorithm.
10. Approval UI requirements: Show username, public key fingerprint, 6-digit code, and Approve/Reject buttons.
11. Deny behavior: Reject should not permanently block yet; consider future extensibility for bans.
12. Rate limits: None required for now.
13. Public key format: Optimize for maximum compatibility and minimal brittleness in transfer/storage.
