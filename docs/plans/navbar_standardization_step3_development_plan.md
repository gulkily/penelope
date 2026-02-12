# Navbar Standardization Step 3: Development Plan

1. **Stage 1: Shared Navbar Include**
   - Goal: Create a reusable navbar partial with the standard links.
   - Dependencies: None.
   - Expected changes:
      - New template include (e.g., `templates/partials/navbar.html`).
     - Parameterize optional links/badge visibility and allow hiding the current page link.
     - Exclude logout from the navbar (logout will live in Settings).
   - Verification approach: Render include in a single page and confirm output.
   - Risks or open questions:
     - How to handle per-page title variations without duplicating markup.
   - Canonical components/API touched: `templates/` only.

2. **Stage 2: Page Integration**
   - Goal: Replace duplicated nav markup in all templates with the include.
   - Dependencies: Stage 1.
   - Expected changes:
      - Update `templates/index.html`, `templates/manage_projects.html`, `templates/settings.html`, `templates/lobby.html`, `templates/confetti_debug.html`, `templates/ledger.html`, `templates/session_reset.html`.
      - Ensure each page passes its current page identifier so the navbar omits that link.
     - Keep the “Back to dashboard” label where it currently appears.
     - Ensure Lobby appears on every page where a navbar is shown (with badge).
   - Verification approach: Open each page and confirm nav links render correctly.
   - Risks or open questions:
     - Ensuring lobby badge script is loaded where needed.
   - Canonical components/API touched: `templates/*.html`.

3. **Stage 3: Clean-Up and Consistency**
   - Goal: Remove obsolete nav-specific styles or scripts and ensure consistency.
   - Dependencies: Stage 2.
   - Expected changes:
      - Remove unused nav markup or scripts if any.
     - Ensure links follow the agreed label conventions and omit current-page links.
   - Verification approach: Visual scan of pages and nav actions.
   - Risks or open questions:
     - None.
   - Canonical components/API touched: `static/css/main.css`, `static/js/*` as needed.
