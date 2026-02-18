## Stage 1 - Shared template session context
- Changes:
  - Added `_build_template_context(request: Request, current_page: str) -> dict` in `app/main.py`.
  - Updated all template-rendering routes to use shared context so `session_account` is consistently available.
  - Updated auth middleware to cache session info on `request.state.session_account` for reuse during rendering.
- Verification:
  - Ran `python -m py_compile app/main.py`.
  - Confirmed all HTML routes still render through `TemplateResponse` with the shared context helper.
- Notes:
  - No auth flow, API contract, or database schema changes.

## Stage 2 - Shared nav identity label
- Changes:
  - Extended `templates/partials/top_nav.html` to conditionally render `Signed in as {username}` when `session_account` exists.
  - Added `.session-identity` and `.session-identity-name` styles in `static/css/main.css`.
  - Kept existing nav links, current-page highlighting, and lobby badge hooks unchanged.
- Verification:
  - Reviewed all templates that include `partials/top_nav.html` to ensure they inherit the same identity display behavior.
  - Confirmed the label is conditional on `session_account`, so unauthenticated routes can omit it.
- Notes:
  - Long usernames are allowed to wrap and remain visible without breaking the nav row.

## Stage 3 - Manual smoke verification handoff
- Changes:
  - Reorganized planning artifacts into `docs/plans/logged_in_identity/` now that the feature has Step 1-4 docs.
  - Updated `docs/plans/README.md` to include the new `logged_in_identity/` feature folder.
- Verification:
  - Manual browser verification is required and should be run by the user:
    1. Sign in, open `/`, `/projects`, `/settings`, `/ledger`, and `/lobby`; confirm the nav shows `Signed in as <username>`.
    2. Sign out, open `/session/reset` and `/lobby`; confirm no signed-in identity label is shown.
    3. Sign back in as a different account and confirm the label updates to that username.
- Notes:
  - Followed repository guidance not to start the server from this environment for manual checks.
