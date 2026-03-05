# North Star Unified Section - Step 3 Development Plan

1. Define the unified North Star layout
   - Goal: Combine objective and progress into a single dashboard section.
   - Dependencies: Existing dashboard markup in `templates/index.html`.
   - Expected changes: Move the progress block into the objective section or create a new shared wrapper that contains both; remove the now-redundant separate section container.
   - Verification: Load the dashboard and confirm objective and progress render together in one section.
   - Risks/open questions: Ensure the layout stays readable at small widths.
   - Shared components/API contracts touched: Dashboard objective input and progress slider markup in `templates/index.html`.

2. Align styling for the combined section
   - Goal: Ensure the unified section looks cohesive and responsive.
   - Dependencies: Existing styles in `static/css/main.css`.
   - Expected changes: Update `.objective` (or new wrapper) styles to handle the progress block; adjust spacing/width rules for the combined layout.
   - Verification: Resize the page and confirm the unified section wraps cleanly on mobile and desktop.
   - Risks/open questions: Avoid regressions in other `.objective` usage (if any).
   - Shared components/API contracts touched: Dashboard layout styles in `static/css/main.css`.

3. Confirm interaction wiring remains intact
   - Goal: Preserve autosave and interactivity when the layout changes.
   - Dependencies: Existing event bindings and state toggles in `static/js/app.js`.
   - Expected changes: Ensure any DOM lookups still resolve after moving elements; no change to endpoints or payloads.
   - Verification: Select a project, edit objective, adjust progress, and confirm both autosave without console errors.
   - Risks/open questions: DOM query assumptions that depend on old structure.
   - Shared components/API contracts touched: Objective and progress controls in `static/js/app.js`.
