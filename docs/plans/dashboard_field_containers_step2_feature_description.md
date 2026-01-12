# Dashboard Field Containers - Step 2 Feature Description

Problem: The Project selector, North Star Objective, and Questions fields lack the same container styling used by the Summary/Challenges/Opportunities/Milestones cards, creating visual inconsistency on the dashboard.

User stories:
- As a designer, I want top-level fields to use the same container styling as the cards so the page feels cohesive.
- As a user, I want the Project, Objective, and Questions areas to be visually framed so that key inputs are easy to find.
- As a user, I want the dashboard hierarchy to stay clear while improving consistency.

Core requirements:
- Wrap the Project selector, North Star Objective, and Questions in card-style containers.
- Preserve existing layout, labels, and interactions for these fields.
- Maintain responsive behavior on desktop and mobile.
- Do not change the existing Summary/Challenges/Opportunities/Milestones cards.
- Keep all current data flows and autosave behaviors unchanged.

Shared component inventory:
- Reuse the existing card container styling in `static/css/main.css`.
- Update the dashboard layout in `templates/index.html` to wrap the three target sections in card containers.
- Keep existing input components and labels intact; no new fields.

Simple user flow:
1. Open the dashboard.
2. See Project selector, Objective, and Questions framed in card containers.
3. Interact with each field as usual.

Success criteria:
- The Project selector, Objective, and Questions appear inside card-style containers matching other sections.
- The dashboard still functions normally with no layout regressions on mobile.
- Visual hierarchy feels consistent across the page.
