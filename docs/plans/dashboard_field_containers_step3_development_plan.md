# Dashboard Field Containers - Step 3 Development Plan

1. Wrap Project selector in a card container
   - Goal: Apply the existing card styling to the Project selector area.
   - Dependencies: Dashboard markup in `templates/index.html` and card styles in `static/css/main.css`.
   - Expected changes: Wrap the Project field block in a `.card` container; keep existing label/select intact.
   - Verification: Load the dashboard and confirm the Project selector appears inside a card without layout issues.
   - Risks/open questions: Ensure the page header layout remains readable with the new card.
   - Shared components/API contracts touched: Dashboard layout in `templates/index.html`, card styles in `static/css/main.css`.

2. Wrap North Star Objective in a card container
   - Goal: Apply card styling to the objective section to match other cards.
   - Dependencies: Objective markup in `templates/index.html`.
   - Expected changes: Nest the objective section inside a `.card` container; preserve objective/progress layout.
   - Verification: Confirm the objective section appears carded and remains aligned at desktop/mobile widths.
   - Risks/open questions: Avoid excessive vertical spacing between header and cards.
   - Shared components/API contracts touched: Objective layout in `templates/index.html`.

3. Wrap Questions in a card container
   - Goal: Apply card styling to the Questions section.
   - Dependencies: Questions markup in `templates/index.html`.
   - Expected changes: Wrap the Questions block in a `.card` container; keep existing textarea behavior.
   - Verification: Confirm Questions renders inside a card and retains spacing consistency with other sections.
   - Risks/open questions: Maintain the hint/empty state positioning.
   - Shared components/API contracts touched: Questions layout in `templates/index.html`.

4. Adjust spacing for the new card layout
   - Goal: Ensure the new carded sections align cleanly with existing grid and spacing.
   - Dependencies: Shared spacing rules in `static/css/main.css`.
   - Expected changes: Minor spacing adjustments if needed to avoid double padding or awkward gaps.
   - Verification: Manual scan on desktop and mobile for consistent vertical rhythm.
   - Risks/open questions: Avoid unintended changes to the existing card grid.
   - Shared components/API contracts touched: Shared layout styles in `static/css/main.css`.
