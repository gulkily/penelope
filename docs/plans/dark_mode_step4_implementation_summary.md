## Stage 1 – Define theme state and root attribute
- Changes: Added a shared theme script that applies a resolved theme to the root element, and loaded it on both main templates.
- Verification: Manual smoke test suggested (load a page and confirm `data-theme` is set on the `<html>` element; not run here).
- Notes: Preference is initialized to system until persistence is added.
