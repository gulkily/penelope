## Stage 1 – Define theme state and root attribute
- Changes: Added a shared theme script that applies a resolved theme to the root element, and loaded it on both main templates.
- Verification: Manual smoke test suggested (load a page and confirm `data-theme` is set on the `<html>` element; not run here).
- Notes: Preference is initialized to system until persistence is added.

## Stage 2 – Add theme toggle control
- Changes: Added a theme selector to both headers and wired it to switch the active theme preference in the shared script.
- Verification: Manual smoke test suggested (change the theme select and confirm the page colors update; not run here).
- Notes: Preference is not persisted yet.

## Stage 3 – Implement dark theme styling
- Changes: Converted shared styles to use theme variables and added dark-mode overrides, including layout tweaks for the theme selector.
- Verification: Manual smoke test suggested (switch themes and check contrast on dashboard and project management pages; not run here).
- Notes: Focus styles and key component colors are now theme-driven.
