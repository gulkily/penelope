## Stage 1 – Auth Data Model + Ledger Scaffold
- Changes: Added auth tables (accounts, public_keys, lobby_requests, ledger_events) and supporting DB helpers for accounts, keys, lobby requests, approvals, and ledger writes.
- Verification: Not run (requires app startup to create tables).
- Notes: Lobby requests start in `verifying` status and require signature verification before appearing in approvals.

## Stage 2 – Auth Utilities + Session Cookie Handling
- Changes: Added `app/auth.py` for cookie signing, fingerprinting, stateless challenges, and signature verification. Added `cryptography` dependency.
- Verification: Not run (will verify once endpoints are wired).
- Notes: Session cookie uses a long-lived HMAC signature and is restored via stateless challenge signing.

## Stage 3 – Lobby/Public Auth API Endpoints
- Changes: Added `/api/auth` router for registration, verification, lobby listing, approvals, username updates, session restore, and current-user lookup. Added auth request/response schemas.
- Verification: Not run (needs app running to exercise endpoints).
- Notes: Registration issues a 14-day code and challenge; approvals can optionally link a key to the approver account.

## Stage 4 – Route Gating + Session Reset Page
- Changes: Added auth middleware and lobby/reset routes in `app/main.py`, plus a session reset template and JS to restore cookies.
- Verification: Not run (requires manual browser check).
- Notes: Unauthorized API calls return 401; browser routes redirect to `/session/reset`.

## Stage 5 – Lobby UI + Approval UI
- Changes: Added lobby template and client script for key generation, registration, status polling, approvals, and username updates. Extended main styles for lobby layout.
- Verification: Not run (requires manual browser check).
- Notes: Lobby auto-restores session when approval arrives; approvers can optionally link requests to themselves.

## Stage 6 – Client Keypair Generation + Persistence
- Changes: Implemented in lobby client script (WebCrypto P-256 keypair generation, localStorage persistence, challenge signing).
- Verification: Not run (requires manual browser check).
- Notes: Signatures are sent as raw WebCrypto ECDSA and verified server-side.

## Stage 7 – Test Coverage
- Changes: Not implemented (per Step 4 guidance to avoid adding automated tests during implementation).
- Verification: Not run.
- Notes: Manual verification is required for lobby flow, approvals, and session restore.

## Stage 8 – API Validation Polish
- Changes: Added input validation for unsupported public key formats and signature verification errors.
- Verification: Not run.
- Notes: Prevents 500s on malformed auth payloads.

## Stage 9 – Lobby Status Messaging
- Changes: Improved lobby status polling messages for verifying/pending/approved/rejected states.
- Verification: Not run.
- Notes: Keeps lobby status clearer while awaiting approval.

## Stage 10 – Public Key Format Backfill
- Changes: Updated public key insert to fill missing `public_key_format` on existing rows.
- Verification: Not run.
- Notes: Avoids empty format values on repeated registrations.

## Stage 11 – Lobby Auto-Restore
- Changes: Lobby now attempts session restore when a keypair exists but no active request id is stored.
- Verification: Not run.
- Notes: Helps approved users recover without re-registering.

## Stage 12 – Bootstrap Approval
- Changes: Added account counting and bootstrap auto-approval when no accounts exist yet.
- Verification: Not run.
- Notes: First verified requester is auto-approved to avoid lockout.

## Stage 13 – Fix First-Request Insert Reads
- Changes: Read newly inserted auth rows using the same DB connection to avoid missing data before commit.
- Verification: Not run.
- Notes: Fixes initial registration KeyError on first attempt.

## Stage 14 – Lobby Link + Waiting Indicator
- Changes: Added lobby link to main nav areas with a badge showing pending lobby count, plus a polling script. Stopped auto-redirect from lobby by removing auto-restore on load.
- Verification: Not run.
- Notes: `/lobby` now stays accessible for approved users.

## Stage 15 – Prevent Lobby Redirect Loop
- Changes: Lobby status polling now detects existing sessions and clears stale request ids instead of restoring and redirecting.
- Verification: Not run.
- Notes: Visiting `/lobby` no longer bounces to `/` once signed in.

## Stage 16 – Hide Lobby Request Panel When Signed In
- Changes: Lobby page now hides the request panel once a logged-in user is detected.
- Verification: Not run.
- Notes: Keeps the lobby view focused on approvals for authenticated users.

## Stage 17 – Enter To Submit Lobby Inputs
- Changes: Enter key now triggers the single action buttons for lobby username inputs.
- Verification: Not run.
- Notes: Applies to request access and display name update fields.

## Stage 18 – Conditional Link Button
- Changes: "Approve + link to me" only renders when the pending username matches the current user name.
- Verification: Not run.
- Notes: Comparison uses trimmed, case-sensitive equality.

## Stage 19 – Logout Button
- Changes: Added logout API and UI button to clear the session cookie and return to the lobby.
- Verification: Not run.
- Notes: Logout preserves local keypair for future restores.

## Stage 20 – Move Logout To Lobby
- Changes: Removed logout from main nav and added it to the lobby page.
- Verification: Not run.
- Notes: Logout remains available wherever `/lobby` is accessible.

## Stage 21 – Persist Logout For Logged-In Lobby
- Changes: Added logout button to the approvals header so it remains visible after the request panel hides.
- Verification: Not run.
- Notes: Prevents the logout button from disappearing for signed-in users.

## Stage 22 – Remove Logout From Request Panel
- Changes: Removed the logout button from the Request Access header.
- Verification: Not run.
- Notes: Logout remains available in the approvals header for signed-in users.

## Stage 23 – Lobby Navbar Links
- Changes: Added dashboard, manage residents, and settings links to lobby headers.
- Verification: Not run.
- Notes: Links appear for both request and approvals views.

## Stage 24 – Normalize Confetti Debug Navbar
- Changes: Added lobby/manage/settings links (with lobby badge) to the confetti debug page.
- Verification: Not run.
- Notes: Keeps debug page nav aligned with the rest of the app.
