# Dark Mode Toggle Button - Step 2 Feature Description

Problem: The current theme selector takes up header space and feels heavier than needed for a quick light/dark toggle.

User stories:
- As a user, I want a compact theme toggle so that I can switch modes quickly without extra UI clutter.
- As a user, I want the toggle to be easy to find so that I can change the theme from anywhere in the app.
- As a user, I want the toggle to preserve my preference so that the app stays in my chosen mode.

Core requirements:
- Replace the theme selector with a compact toggle button.
- Place the toggle in a fixed corner position that is visible on all pages.
- Keep existing theme preference persistence and system default behavior.
- Ensure the toggle is accessible and usable on mobile and desktop.
- Do not change existing page layout content beyond removing the selector.

Shared component inventory:
- Reuse the existing theme preference logic in `static/js/theme.js`.
- Update shared templates (`templates/index.html`, `templates/manage_projects.html`) to remove the selector and add the toggle control.
- Extend shared styling in `static/css/main.css` for the corner toggle.

Simple user flow:
1. Open any page in the app.
2. Find the theme toggle in the corner.
3. Tap/click to switch theme modes.
4. Refresh the page and see the theme persist.

Success criteria:
- The theme toggle appears in a consistent corner location on all primary pages.
- Toggling changes the theme immediately.
- The chosen theme persists across reloads.
- The toggle does not overlap or obscure core content on mobile or desktop.
