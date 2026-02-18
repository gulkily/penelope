# Nav + Recorder Feature Flags Step 3: Development Plan

Sizing note: Each stage targets <=1 hour or <=50 lines of change; if Stage 4 grows beyond that, split it into separate recorder and lobby-auth implementation stages before coding.

1. **Stage 1: Feature Flag Configuration Contract**
   - Goal: Define the runtime settings contract for navbar visibility, lobby auth behavior, and recorder visibility.
   - Dependencies: Existing environment parsing helpers in `app/main.py`.
   - Expected changes:
     - Add one navbar setting (list of enabled nav item keys).
     - Add separate settings for lobby auth behavior and recorder visibility.
     - Define canonical nav item keys and fallback behavior for invalid/unknown keys.
     - Planned signatures (conceptual):
       - `get_navbar_enabled_items() -> set[str]`
       - `get_feature_flags() -> dict[str, bool | set[str]]`
   - Verification approach: Manual startup check with default env and overridden env values.
   - Risks or open questions:
     - Final nav item key names must stay stable once documented.
   - Canonical components/API touched: `app/main.py` config/context helpers.

2. **Stage 2: Shared Template Context Wiring**
   - Goal: Make feature settings available to all templates that render nav and dashboard UI.
   - Dependencies: Stage 1.
   - Expected changes:
     - Extend shared template context to include filtered navbar items and recorder visibility flag.
     - Preserve current route behavior (no route blocking based on navbar visibility).
     - Planned signature (conceptual):
       - `_build_template_context(request: Request, current_page: str) -> dict`
   - Verification approach: Open representative pages and confirm context-driven rendering does not break existing pages.
   - Risks or open questions:
     - Ensure pages using `top_nav` get identical nav behavior.
   - Canonical components/API touched: `app/main.py`, `templates/partials/top_nav.html`.

3. **Stage 3: Navbar Rendering via Single Navbar Setting**
   - Goal: Render nav links strictly from the centralized navbar setting.
   - Dependencies: Stage 2.
   - Expected changes:
     - Refactor `templates/partials/navbar.html` to iterate/render only enabled items from the shared list.
     - Keep current visual styles and active-page treatment.
     - Ensure lobby badge markup only appears when Lobby nav item is enabled.
   - Verification approach: Manual page-by-page nav smoke test (dashboard, lobby, projects, settings, session reset, ledger).
   - Risks or open questions:
     - Ensure hidden current-page nav items do not create confusing active-state gaps.
   - Canonical components/API touched: `templates/partials/navbar.html`, `static/js/lobby-indicator.js` integration points.

4. **Stage 4: Recorder and Lobby-Auth Behavior Controls**
   - Goal: Apply separate controls for dashboard recorder visibility and lobby auth behavior.
   - Dependencies: Stages 1-2.
   - Expected changes:
     - Condition recorder section rendering in `templates/index.html` on recorder visibility setting.
     - Apply lobby auth setting in existing auth/lobby flow surfaces without coupling to nav visibility.
     - Preserve direct URL accessibility for `/lobby`, `/settings`, and `/projects` regardless of navbar visibility.
   - Verification approach: Manual flow checks for recorder shown/hidden and lobby auth enabled/disabled scenarios.
   - Risks or open questions:
     - Exact lobby-auth disabled behavior (e.g., informative message vs. no-op flow) must be explicitly defined in implementation.
   - Canonical components/API touched: `templates/index.html`, `app/api_auth.py`, `templates/lobby.html` and related auth entry points.

5. **Stage 5: Test and Documentation Updates**
   - Goal: Add focused regression coverage and operator-facing configuration notes.
   - Dependencies: Stages 1-4.
   - Expected changes:
     - Add/adjust HTTP or E2E tests for nav visibility, recorder visibility, and lobby-auth independence.
     - Update README/env docs with new settings, defaults, and valid navbar item keys.
   - Verification approach: Run targeted test commands plus a quick manual smoke pass.
   - Risks or open questions:
     - E2E selectors may need small updates if nav items are conditionally absent.
   - Canonical components/API touched: `tests/http/*` and/or `tests/e2e/*`, `README.md` (or env documentation surface).
