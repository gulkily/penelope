# Dark Mode Toggle Button - Step 3 Development Plan

1. Replace the theme selector with a floating toggle control
   - Goal: Remove the header selector and add a small toggle button in a fixed corner position.
   - Dependencies: Existing templates and theme logic in `static/js/theme.js`.
   - Expected changes: Remove the theme select markup from `templates/index.html` and `templates/manage_projects.html`, add a shared toggle button element, and ensure it is present on both pages.
   - Verification: Load both pages and confirm the toggle appears in the corner and no header layout shifts remain.
   - Risks/open questions: Decide which corner is least intrusive on mobile and desktop.
   - Shared components/API contracts touched: Shared templates and the theme control UI.

2. Wire toggle behavior to theme preference
   - Goal: Allow a single control to cycle through available theme modes or toggle light/dark while respecting system defaults.
   - Dependencies: Theme state and persistence in `static/js/theme.js`.
   - Expected changes: Add a toggle handler that updates the stored preference and updates accessible label text.
   - Verification: Click the toggle and confirm the theme changes immediately and persists after reload.
   - Risks/open questions: Determine whether to cycle System → Light → Dark or only toggle Light/Dark when already overridden.
   - Shared components/API contracts touched: Theme preference logic in `static/js/theme.js`.

3. Style the floating toggle for visibility and accessibility
   - Goal: Ensure the toggle is discoverable, compact, and does not overlap content.
   - Dependencies: Shared stylesheet in `static/css/main.css`.
   - Expected changes: Add a fixed-position button style, hover/focus states, and spacing adjustments for mobile safe areas.
   - Verification: Resize to mobile widths and confirm the toggle stays visible without covering key UI elements.
   - Risks/open questions: Avoid conflicting with the undo toast position.
   - Shared components/API contracts touched: Global styles in `static/css/main.css`.
