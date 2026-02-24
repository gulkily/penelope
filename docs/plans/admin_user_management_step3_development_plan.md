# Admin User List Step 3: Development Plan

Sizing note: each stage is scoped to roughly <=1 hour or <=50 lines of net change; if a stage grows past that, split before implementation.

1. Stage 1 - Define read-only user roster data contract
   - Goal: Establish a canonical backend contract for listing accounts needed by admin UI.
   - Dependencies: Existing `accounts` table and auth/session utilities.
   - Expected changes:
     - Add DB read helper for account roster retrieval (no schema change).
     - Add response schema models for users list entries including `is_admin`.
     - Planned signatures:
       - `list_accounts(limit: int = 500, offset: int = 0) -> list[dict]`
       - `class AdminUserListEntry(BaseModel): id, username, is_admin, created_at`
   - Verification approach: Manual API-shape check from local endpoint consumer (confirm fields and ordering).
   - Risks or open questions:
     - If `MAGIC_LINK_ADMIN_USERNAMES` is unset, all users are admin by current policy.
     - Decide whether to expose timestamps now or keep minimum fields.
   - Canonical components/API touched: `app/db_auth.py`, `app/db.py`, `app/schemas.py`.

2. Stage 2 - Add admin-only users list API endpoint
   - Goal: Provide a secure read-only endpoint for user roster + admin status.
   - Dependencies: Stage 1 contracts and existing `_require_admin` guard.
   - Expected changes:
     - Add `GET /api/auth/users` in auth router.
     - Derive `is_admin` using the same runtime logic used for admin authorization.
     - Return empty list when no accounts exist; no mutation operations added.
     - Planned signature:
       - `GET /api/auth/users?limit=<int>&offset=<int> -> { entries: AdminUserListEntry[], total: int }`
   - Verification approach: Manual smoke checks for admin success and non-admin `403`.
   - Risks or open questions:
     - Avoid drifting into separate permission logic just for display.
   - Canonical components/API touched: `app/api_auth.py`, `app/auth.py`, `app/schemas.py`.

3. Stage 3 - Build users page and Settings entry point
   - Goal: Add a read-only in-app surface for admins to review users/admin status.
   - Dependencies: Stage 2 endpoint availability.
   - Expected changes:
     - Add new route + template for users page (table + empty state).
     - Add frontend script to fetch `/api/auth/users` and render rows/status.
     - Extend Settings page with a navigation/action to open the users view.
   - Verification approach: Manual browser smoke test: open from Settings, see rows, verify empty state handling.
   - Risks or open questions:
     - Keep status labels clear ("Admin"/"Standard") without implying editability.
   - Canonical components/API touched: `app/main.py`, `templates/settings.html`, new `templates/users.html`, new `static/js/users.js`, shared `static/css/main.css` table patterns.

4. Stage 4 - Access-control regression checks and rollout notes
   - Goal: Confirm behavior is safe and documented before Step 4 implementation wrap-up.
   - Dependencies: Stages 1-3 complete.
   - Expected changes:
     - Add focused HTTP tests for admin access, non-admin denial, and empty-list response.
     - Add/update lightweight docs note describing that admin status is display-only and env-driven for now.
   - Verification approach: Run focused HTTP test command and one manual admin/non-admin smoke pass.
   - Risks or open questions:
     - Test fixtures must include both admin and non-admin sessions to avoid false positives.
   - Canonical components/API touched: `tests/http/`, `README.md` (or equivalent operator notes).
