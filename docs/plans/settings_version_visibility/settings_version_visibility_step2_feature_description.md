# Settings Version Visibility - Step 2 Feature Description

## Problem
Admins currently have no in-app way to confirm which Penelope build is running. This slows support and troubleshooting when environments differ.

## User Stories
- As an admin, I want to see the running git commit SHA and commit date on Settings so that I can quickly identify the deployed build.
- As a support operator, I want a stable place in the UI for build identity so that I can confirm environment state without shell access.
- As a non-admin user, I want Settings access controls unchanged so that build metadata is only visible within admin workflows.

## Core Requirements
- Show build metadata on the `/settings` page for admin sessions.
- Metadata must include commit SHA and commit date.
- If metadata is unavailable, show a clear fallback value (for example, `Unknown`) instead of breaking the page.
- Keep existing admin-only access control for Settings routes unchanged.
- Avoid database schema changes and avoid introducing new frontend frameworks.

## Shared Component Inventory
- `templates/settings.html`: canonical admin settings surface; extend this template to display build metadata.
- `app/main.py` (`settings` route + `_build_template_context`): existing server-rendered context path for Settings; extend/reuse to provide metadata to the template.
- `templates/partials/top_nav.html` and `templates/partials/navbar.html`: shared navigation surfaces used by Settings; reuse unchanged.
- API surfaces currently rendering version/build metadata: none; this feature should stay server-rendered on Settings and not require a new API route.

## Simple User Flow
1. Admin signs in and opens `/settings`.
2. Page renders a version/build section showing commit SHA and commit date.
3. Admin uses this value for release verification or support handoff.
4. If metadata cannot be resolved, page shows fallback text and remains usable.

## Success Criteria
- Admin can see commit SHA and commit date on `/settings` in a single glance.
- Non-admin users still cannot access Settings pages.
- Settings page continues to load successfully even when commit metadata is unavailable.
- No database migration is introduced for this feature.
