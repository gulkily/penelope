# Resident Progress Tracking - Step 3 Development Plan

1. Relabel dashboard selection and context text to residents
- Goal: Shift primary dashboard language from project to resident.
- Dependencies: Existing dashboard template and CSS.
- Expected changes: Update text in `templates/index.html` (labels, empty state copy, aria labels) to resident wording; ensure no structural layout changes.
- Verification approach: Load the dashboard and confirm all visible labels reference residents.
- Risks/open questions: None beyond missing copy spots.
- Shared components/API contracts: `templates/index.html` selector, objective, progress, empty state.

2. Relabel management view to residents
- Goal: Present the manage page as resident management without changing behavior.
- Dependencies: Existing manage projects template and styles.
- Expected changes: Update text in `templates/manage_projects.html` (headers, button labels, empty states) to resident wording; keep routes unchanged.
- Verification approach: Visit `/projects` and confirm labels/readability for resident management.
- Risks/open questions: Ensure any inline help text is updated consistently.
- Shared components/API contracts: `templates/manage_projects.html` and shared CSS.

3. Align frontend copy in JavaScript interactions
- Goal: Ensure dynamic UI text (toasts, alerts, empty states) uses resident terminology.
- Dependencies: Existing JS UI utilities and event handlers.
- Expected changes: Update copy in `static/js/app.js` for resident wording; keep event flow and data shape unchanged.
- Verification approach: Trigger add/edit/delete flows and confirm toast/alert text uses residents.
- Risks/open questions: Confirm any hard-coded "project" strings in JS are user-facing.
- Shared components/API contracts: `static/js/app.js` (client behavior), existing API endpoints.

4. Validate API and schema naming strategy documentation
- Goal: Confirm API endpoints remain `/projects` while UI uses resident labels.
- Dependencies: Existing FastAPI routes and OpenAPI metadata.
- Expected changes: Update API-facing descriptions in `app/schemas.py` (field descriptions) and any router metadata to mention residents where user-facing; no route name changes.
- Verification approach: Check the docs or inspect responses for unchanged shape; confirm no route changes.
- Risks/open questions: Ensure terminology changes don't confuse internal developers.
- Shared components/API contracts: `app/api.py` route contracts, `app/schemas.py` descriptions.

5. Update docs and helper text where projects are referenced
- Goal: Keep README and other user docs consistent with resident framing.
- Dependencies: `README.md` and any help text files.
- Expected changes: Replace user-facing "project" references with "resident" where appropriate; avoid changing technical file paths or API names.
- Verification approach: Quick scan of README for resident terminology consistency.
- Risks/open questions: Avoid over-editing technical instructions that still use project routes.
- Shared components/API contracts: Documentation only.
