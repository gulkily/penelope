# Unauthenticated + Lobby Disabled Handling Step 3: Development Plan

Sizing note: each stage targets <=1 hour or <=50 lines; if Stage 2 grows beyond that, split JS flow/state messaging into separate stages before implementation.

1. **Stage 1: Redirect Target Capture + Session Reset UI States**
   - Goal: Capture original unauthenticated target and prepare `/session/reset` to present a clear post-failure “not logged in” guidance state.
   - Dependencies: Existing `/session/reset` route and template context.
   - Expected changes:
     - Extend unauthenticated redirect flow to preserve intended target path for post-restore navigation.
     - Extend `templates/session_reset.html` copy/layout to support failure guidance without relying on lobby navigation.
     - Define explicit text guidance that instructs users to use a magic link or request one from admins (no CTA links required).
     - Planned signature (conceptual):
       - `_build_template_context(request: Request, current_page: str) -> dict` (reuse existing context; no new route needed).
   - Verification approach: Open `/session/reset` and confirm guidance state content is visible/readable after failure state is triggered.
   - Risks or open questions:
     - Ensure redirect-target capture does not allow unsafe external redirects.
   - Canonical components/API touched: `app/main.py` middleware/route context, `templates/session_reset.html`.

2. **Stage 2: Restore-First JS Behavior and Failure Fallback**
   - Goal: Keep auto-restore attempt, then show “not logged in” guidance on failure and redirect correctly on success.
   - Dependencies: Stage 1.
   - Expected changes:
     - Update `static/js/session_reset.js` failure branches (missing keypair, restore failure, challenge failure paths) to avoid dead-end redirect logic.
     - Redirect successful restore to original requested path, with `/lobby` normalized to `/`.
     - Keep retry button behavior aligned with the new failure state.
   - Verification approach: Manual browser checks for success and failure paths (with/without stored keypair).
   - Risks or open questions:
     - Ensure redirect-target handling is robust when target is missing/invalid.
   - Canonical components/API touched: `static/js/session_reset.js`, existing auth restore APIs.

3. **Stage 3: Decouple Magic-Link Login from Lobby-Auth Gating**
   - Goal: Keep magic-link login usable when `LOBBY_AUTH_ENABLED=false`.
   - Dependencies: Stage 2.
   - Expected changes:
     - Update lobby-auth gating in auth API surfaces so magic-link login path remains available when lobby auth is disabled.
     - Preserve disabled-lobby behavior for non-magic-link lobby request flows.
   - Verification approach: Manual smoke test in lobby-disabled mode confirming magic-link login remains functional.
   - Risks or open questions:
     - Ensure decoupling does not unintentionally re-enable general lobby request/approval paths.
   - Canonical components/API touched: `app/api_auth.py`, magic-link endpoints, related auth guards.

4. **Stage 4: Documentation and Regression Notes**
   - Goal: Document expected unauthenticated behavior and reduce future regressions.
   - Dependencies: Stage 3.
   - Expected changes:
     - Update `README.md` notes (or equivalent operator docs) to describe `/session/reset` restore-first and post-failure magic-link guidance.
     - Add implementation summary notes for manual validation scenarios.
   - Verification approach: Follow documented steps in a fresh unauthenticated browser session.
   - Risks or open questions:
     - Keep docs aligned if auth entry flow changes again.
   - Canonical components/API touched: `README.md`, Step 4 implementation summary artifact.
