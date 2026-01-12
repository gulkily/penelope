# Dark Mode - Step 3 Development Plan

1. Define theme strategy and storage
   - Goal: Establish the theme selection rules (system default with optional override).
   - Dependencies: Existing base stylesheet and HTML templates.
   - Expected changes: Add a lightweight theme state model (e.g., stored preference and system detection); plan a class or data attribute on the root element to control theme.
   - Verification: Toggle theme state and confirm the correct attribute/class is applied on load.
   - Risks/open questions: Decide where to store preference (local storage) and how to handle “system” selection.
   - Shared components/API contracts touched: Root HTML structure and shared styles in `static/css/main.css`.

2. Add theme toggle control in the UI
   - Goal: Provide an in-app way to switch between light and dark (and potentially system default).
   - Dependencies: Shared header layout in `templates/index.html` and `templates/manage_projects.html`.
   - Expected changes: Add a compact toggle control in the header area; ensure it is accessible and consistent across pages.
   - Verification: Switch themes and confirm the control updates and persists state.
   - Risks/open questions: Placement should not overcrowd existing header content.
   - Shared components/API contracts touched: Header markup in both templates.

3. Implement dark theme styling
   - Goal: Provide readable, high-contrast dark mode styles across all UI surfaces.
   - Dependencies: Existing styles in `static/css/main.css`.
   - Expected changes: Introduce theme variables or scoped overrides for backgrounds, text, borders, inputs, cards, buttons, and highlights; ensure focus states remain visible.
   - Verification: Manual pass on dashboard and project management screens in dark mode.
   - Risks/open questions: Ensure contrast ratios remain acceptable; watch for hardcoded colors that should be themed.
   - Shared components/API contracts touched: Shared component styles in `static/css/main.css`.

4. Wire theme persistence and system detection
   - Goal: Persist the user’s theme choice and default to system when no override is set.
   - Dependencies: The theme state model and UI toggle.
   - Expected changes: Add a small script to read/write preference, listen to system theme changes when in “system” mode, and apply updates across pages.
   - Verification: Reload the app and confirm the theme persists; change system theme and verify it updates when in system mode.
   - Risks/open questions: Handling cross-tab updates if users toggle in one tab.
   - Shared components/API contracts touched: Shared theme script included in templates, root theme attribute/class.
