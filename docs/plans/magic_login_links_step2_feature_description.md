# Magic Login Links (Preconfigured Username) — Step 2 Feature Description

## Problem
Admins currently need the lobby flow to grant access, but they need a faster “send link and log in” path for trusted users. The product needs one-click magic links that log in the recipient with a preconfigured username.

## User Stories
- As an admin, I want to generate a one-click login link tied to a username so that I can onboard users quickly.
- As a recipient, I want a single link click to sign me in so that I can access the dashboard without manual lobby steps.
- As an admin, I want issued links to be short-lived and single-use so that accidental forwarding or replay does not create uncontrolled access.
- As an operator, I want issuance and redemption recorded so that account access actions are auditable.

## Core Requirements
- Admin-only workflow can generate magic login links for a specified username.
- Each link is single-use, expires after a defined TTL, and cannot be reused after successful redemption.
- Redeeming a valid link creates an authenticated session and lands the user in the normal app experience.
- Invalid, expired, or already-used links show a clear failure state without signing in the user.
- Issuance and redemption events are captured in the existing ledger/audit flow.

## Shared Component Inventory
- `templates/settings.html` + `static/js/settings.js`: extend as the canonical admin surface for link generation/revocation controls.
- `app/api_auth.py` + existing auth session model: extend with magic-link issue/redeem endpoints while reusing current session-cookie behavior.
- `app/auth.py` session cookie utilities: reuse for final authenticated session creation after token redemption.
- `templates/lobby.html` + `static/js/lobby.js`: keep existing lobby flow intact; magic links are an additional path, not a replacement.
- New redeeming surface (route/page or redirect endpoint): needed so recipients can open a link and complete one-click sign-in safely.

## Simple User Flow
1. Admin opens Settings and enters a username for a new magic login link.
2. System returns a single-use link with expiry information.
3. Admin shares the link with the intended recipient.
4. Recipient opens the link; system validates token state (valid, unexpired, unused).
5. On success, session is created and user lands in the app; on failure, user sees an explicit expired/invalid/used message.

## Success Criteria
- Admin can issue a magic link for a username in one action from the app.
- Valid links produce login in one click without manual lobby interaction.
- Used or expired links fail safely and do not create sessions.
- Ledger includes both “magic link issued” and “magic link redeemed/failed” visibility for operators.
- Existing lobby-based onboarding remains functional and unchanged for users not using magic links.
