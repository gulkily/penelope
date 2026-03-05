# Admin Settings Navigation Step 2: Feature Description

## Problem
Non-admin users currently encounter Settings entry points that add unnecessary navigation noise, while admins need fast, reliable access to Settings for operational tasks.

## User Stories
- As a non-admin user, I want to avoid seeing irrelevant Settings navigation so that the UI is easier to understand.
- As an admin, I want one-click access to Settings from primary navigation so that I can perform frequent admin tasks quickly.
- As an operator, I want role-based Settings visibility to work with existing environment-driven navbar configuration so that deployment behavior stays predictable.

## Core Requirements
- Show the `Settings` navbar item only when the signed-in user is recognized as admin.
- Keep `Settings` hidden for non-admin users across shared navigation surfaces.
- Require admin access for Settings pages (`/settings` and Settings subpages), not only navbar visibility.
- Continue honoring existing navbar feature-flag behavior (`NAVBAR_ENABLED_ITEMS`), so `settings` must remain enabled there for admins to see it.
- Avoid database schema changes; use current admin-resolution behavior.

## Shared Component Inventory
- `templates/partials/navbar.html`: existing canonical navbar renderer; extend/reuse to support admin-only Settings visibility.
- `templates/partials/top_nav.html`: existing shared nav wrapper; reuse unchanged except for propagated visibility behavior.
- `app/main.py` template context + page routes: existing shared context and route entry points; extend for role-based nav visibility and Settings access gating.
- `app/auth.py` admin resolution (`is_admin_account`): existing canonical admin check; reuse as source of truth.
- `app/feature_flags.py` navbar item controls: existing canonical config surface; reuse so role gating layers on top of enabled-item flags.

## Simple User Flow
1. User signs in and opens the app.
2. The app evaluates both navbar configuration and whether the user is admin.
3. Admin user sees `Settings` in the navbar and can open Settings pages.
4. Non-admin user does not see `Settings` in navigation.
5. If a non-admin opens a Settings URL directly, access is denied.

## Success Criteria
- Non-admin sessions never render a `Settings` navbar entry.
- Admin sessions render `Settings` in navbar when `settings` is enabled in `NAVBAR_ENABLED_ITEMS`.
- Non-admin attempts to open Settings URLs are blocked.
- Admin access to Settings remains one-click from primary navigation with no added menu clutter for non-admin users.
