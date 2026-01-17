# Dark Mode - Step 2 Feature Description

Problem: The app is only optimized for light environments, making it uncomfortable to use in low-light settings and out of step with user theme preferences.

User stories:
- As a user, I want a dark theme so that I can use the app comfortably at night.
- As a user, I want the app to respect my system theme by default so that it feels native.
- As a user, I want to override the theme when needed so that I can choose the appearance that works best for me.

Core requirements:
- Provide a dark mode visual theme across the dashboard and project management pages.
- Default to the system theme preference.
- Allow users to override the theme with an in-app control.
- Persist the chosen theme so it remains consistent across sessions.
- Keep the existing layout, structure, and interactions unchanged.

Shared component inventory:
- Reuse existing layouts and components in `templates/index.html` and `templates/manage_projects.html`.
- Extend the shared styling in `static/css/main.css` (or a consistent split) to support dark mode without duplicating markup.
- Use the existing header area for any new theme control; no new pages.

Simple user flow:
1. Open the app.
2. The theme defaults to the system preference.
3. Use the theme control to switch between light and dark.
4. Reload or revisit the app and see the chosen theme preserved.

Success criteria:
- Dark mode renders with readable contrast across all primary screens.
- The theme control switches immediately without breaking layout or interactions.
- The theme choice persists across reloads.
- Default behavior follows system preference when no override is set.
