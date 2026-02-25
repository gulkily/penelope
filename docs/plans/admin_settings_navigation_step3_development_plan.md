# Admin Settings Navigation Step 3: Development Plan

Sizing note: each stage is scoped to roughly <=1 hour or <=50 lines of net change; if Stage 4 exceeds that, split tests into separate HTTP and E2E follow-ups.

1. Stage 1 - Add canonical role-aware navbar filtering
   - Goal: Ensure shared navbar item generation hides `settings` for non-admin sessions while preserving existing feature-flag behavior.
   - Dependencies: Existing navbar definitions in `app/feature_flags.py` and admin detection via `auth.is_admin_account`.
   - Expected changes:
     - Extend shared navbar-item builder to accept role context.
     - Keep `NAVBAR_ENABLED_ITEMS` as the first-level filter, then apply admin-only filtering for `settings`.
     - Planned signature updates (conceptual):
       - `_build_navbar_items(enabled_keys: set[str], *, session_is_admin: bool) -> list[dict]`
       - `_build_template_context(request: Request, current_page: str) -> dict`
   - Verification approach: Manual page smoke test with one admin and one non-admin session; confirm `Settings` link visibility differs only by role.
   - Risks or open questions:
     - Ensure no page bypasses shared context and accidentally renders stale nav behavior.
   - Canonical components/API touched: `app/main.py`, `templates/partials/navbar.html` (render behavior remains canonical).

2. Stage 2 - Enforce admin-only access to Settings routes
   - Goal: Align backend authorization with navbar visibility so direct URL access cannot bypass role restrictions.
   - Dependencies: Stage 1 role context and existing admin-check logic.
   - Expected changes:
     - Add a shared guard for admin-only page routes.
     - Apply guard to `/settings` and `/settings/magic-links` (and preserve existing admin guard on `/settings/users`).
     - Standardize denial behavior for non-admin users (consistent `403` response path for these routes).
     - Planned signature (conceptual):
       - `_require_admin_session(request: Request) -> auth.SessionInfo`
   - Verification approach: Manual request checks for admin success and non-admin `403` on all Settings routes.
   - Risks or open questions:
     - Decide whether future UX should redirect non-admin users instead of returning `403` (out of scope here).
   - Canonical components/API touched: `app/main.py`, `app/auth.py` (reused admin contract only).

3. Stage 3 - Keep Settings surface internally consistent for admins
   - Goal: Confirm the Settings page and subpage entry points still work for admins after route/visibility hardening.
   - Dependencies: Stage 2 access guard in place.
   - Expected changes:
     - Validate Settings page actions/links remain accessible for admins.
     - Ensure no new UI controls are introduced for non-admin users.
     - Keep existing copy/labels intact unless required for clarity.
   - Verification approach: Manual admin smoke path: Dashboard -> Settings -> Magic links -> Users.
   - Risks or open questions:
     - If operations prefer a softer non-admin experience, copy or error-page treatment may be revisited later.
   - Canonical components/API touched: `templates/settings.html`, `templates/partials/top_nav.html`, existing Settings subpages.

4. Stage 4 - Regression coverage for role-gated nav and Settings access
   - Goal: Add focused automated checks so role-based navbar and Settings authorization remain stable.
   - Dependencies: Stages 1-3 behavior finalized.
   - Expected changes:
     - Add or extend tests to verify:
       - Admin sees `Settings` nav entry when `settings` is enabled.
       - Non-admin does not see `Settings` nav entry.
       - Non-admin receives `403` for `/settings` and `/settings/magic-links`.
     - Keep coverage targeted; no broad test-suite refactor.
   - Verification approach: Run focused test command(s) plus a brief manual confirmation.
   - Risks or open questions:
     - Test fixtures may need explicit admin/non-admin session setup if current defaults assume admin behavior.
   - Canonical components/API touched: `tests/http/` and/or `tests/e2e/`, shared auth/session test helpers if present.
