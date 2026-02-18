# Logged-In Identity Visibility - Step 3 Development Plan

1. Stage 1: Add shared template context for current session identity
   - Goal: Ensure authenticated template pages can consistently access the current account username without duplicating per-route logic.
   - Dependencies: Existing `auth.get_session_account(request)` and page route handlers in `app/main.py`.
   - Expected changes:
     - Add a shared helper signature in `app/main.py` to build template context, e.g. `_build_template_context(request: Request, current_page: str) -> dict`.
     - Include session identity data (or `None`) in that context for authenticated and mixed-access pages.
     - Keep auth middleware behavior unchanged; no database/schema changes.
   - Verification approach: Manually load `/`, `/projects`, `/settings`, `/ledger`, and `/lobby` while authenticated and confirm page render behavior is unchanged.
   - Risks/open questions:
     - `/lobby` is accessible without authentication, so context must safely handle missing session identity.
   - Canonical components/API contracts touched: `app/main.py`, `app/auth.py`.

2. Stage 2: Extend shared top navigation with a signed-in identity label
   - Goal: Surface "Signed in as {username}" in the canonical nav area across authenticated pages.
   - Dependencies: Stage 1 session context availability; shared nav partials and existing nav CSS.
   - Expected changes:
     - Update shared nav partial(s) to conditionally render an identity label when session identity is present.
     - Add minimal styling for the identity label that works across desktop/mobile and existing light/dark themes.
     - Preserve existing nav links and lobby badge behavior.
   - Verification approach: Manual cross-page check that the label is visible and consistent on authenticated pages, and absent when not authenticated.
   - Risks/open questions:
     - Long usernames may wrap or crowd nav controls on smaller screens.
   - Canonical components/API contracts touched: `templates/partials/top_nav.html`, `templates/partials/navbar.html`, `static/css/main.css`.

3. Stage 3: Add regression checks for identity visibility rules
   - Goal: Reduce regressions where identity display disappears or leaks to unauthenticated screens.
   - Dependencies: Stages 1-2 completed.
   - Expected changes:
     - Add one focused automated UI assertion in existing smoke coverage (or closest equivalent) for authenticated page identity visibility.
     - Add a complementary check that unauthenticated surfaces (for example `/session/reset`) do not render a signed-in identity label.
     - Document a short manual smoke script for local verification when full auth state is hard to seed in tests.
   - Verification approach: Run targeted pytest command for the updated test module; then perform manual smoke checks for authenticated and unauthenticated routes.
   - Risks/open questions:
     - Current test suite has limited explicit auth setup, so automated coverage may need lightweight assumptions about local test state.
   - Canonical components/API contracts touched: `tests/e2e/test_smoke.py` (or equivalent smoke module), auth-gated page routes in `app/main.py`.
