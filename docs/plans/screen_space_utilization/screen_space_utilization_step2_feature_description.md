# Screen Space Utilization - Step 2 Feature Description

Problem: The dashboard layout feels sparse on large screens, leaving useful space unused and increasing vertical scrolling.

User stories:
- As a user on a large display, I want the dashboard to use more of the available width so that key content is visible without excess empty space.
- As a user, I want the layout to remain familiar while feeling less spread out vertically.
- As a designer, I want consistent spacing and proportions across screen sizes.

Core requirements:
- Improve large-screen density by expanding container width and tuning spacing at large breakpoints.
- Preserve the existing layout structure and visual hierarchy.
- Keep the layout responsive and readable on smaller screens.
- Avoid introducing new controls or settings for layout changes.
- Maintain existing interactions and content order.

Shared component inventory:
- Reuse existing layout containers in `templates/index.html`.
- Adjust shared layout styles in `static/css/main.css` (e.g., `.page`, grids, spacing).
- Keep existing card and section styles intact, only adjusting spacing/width rules.

Simple user flow:
1. Open the dashboard on a large screen.
2. See a wider layout with reduced empty space and improved density.
3. Interact with the page as normal without layout confusion.

Success criteria:
- The dashboard uses more horizontal space on large screens.
- Vertical spacing feels tighter without harming readability.
- The layout remains stable and responsive across common breakpoints.
