# Admin User List Step 2: Feature Description

## Problem
Admins can currently issue/revoke magic links but cannot see a complete in-app list of user accounts or quickly confirm who is considered admin under current auth rules.

## User Stories
- As an admin, I want to see all user accounts in one place so that I can understand who has access.
- As an admin, I want each user row to show admin status so that I can verify who can use admin-only tools.
- As an operator, I want this screen to be read-only so that we can ship visibility now without introducing permission-editing scope.

## Core Requirements
- Provide an authenticated, admin-only users view that lists all accounts.
- Show an admin indicator per user derived from the same logic that protects admin-only APIs.
- Keep the feature read-only (no promote/demote, delete, or other permission mutation actions).
- Non-admin users must be denied access to both the users API surface and users page content.
- Display a clear empty state when no accounts are present.

## Shared Component Inventory
- `templates/settings.html`: extend existing admin tools page with navigation entry to the users list (reuse existing card/button patterns).
- `templates/partials/top_nav.html`: reuse existing signed-in identity header to keep session context consistent.
- `/api/auth/me`: existing current-user identity surface; reuse as-is (no extension) since it is not a user roster endpoint.
- `/api/auth/magic-links` + `templates/magic_links.html` + `static/js/magic-links.js`: existing partial user identity rendering (`created_by_username`); keep as-is and do not repurpose as user source.
- `/api/auth/ledger` + `templates/ledger.html` + `static/js/ledger.js`: existing admin read-only table pattern with username fields; reuse display pattern and access expectations, but keep ledger and users as separate canonical surfaces.
- New users list page/API: add a new canonical read-only surface for full account listing plus admin status.

## Simple User Flow
1. Admin opens Settings and navigates to the users list.
2. Users page loads all accounts and shows admin status for each row.
3. Admin reviews the list; no edit actions are available.

## Success Criteria
- An authenticated admin can open the users view and see all existing accounts with admin status.
- A non-admin authenticated user receives a forbidden response and cannot view the users list data.
- Displayed admin status matches current runtime admin logic for sampled accounts.
- Users list behaves correctly when there are zero accounts (clear empty state, no errors).
