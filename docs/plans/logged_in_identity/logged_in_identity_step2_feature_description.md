# Logged-In Identity Visibility - Step 2 Feature Description

## Problem
Authenticated users cannot reliably confirm which account is active while navigating the app, which increases the risk of taking actions under the wrong identity.

## User Stories
- As an authenticated user, I want to see who I am logged in as so that I can confirm I am using the correct account.
- As an admin approving lobby requests, I want my active identity to be visible so that I avoid approving actions from the wrong session.
- As a teammate sharing a workstation, I want immediate account visibility so that I can detect when I need to log out or switch users.

## Core Requirements
- A clear "signed in as" identity label is visible on authenticated pages.
- The label shows the current account username from the active session.
- The identity display is consistent across dashboard, lobby, projects, settings, and ledger pages.
- Unauthenticated users do not see identity data.
- Existing authentication behavior and session enforcement remain unchanged.

## Shared Component Inventory
- Shared top navigation include (`templates/partials/top_nav.html`, `templates/partials/navbar.html`): extend as the canonical UI surface for account identity visibility.
- Session identity API (`GET /api/auth/me`): reuse as the canonical source of current account `id` and `username`.
- Auth/session middleware (`app/main.py` + `app/auth.py`): reuse to ensure identity is only shown for authenticated requests.
- Existing page templates that already include top navigation (`templates/index.html`, `templates/lobby.html`, `templates/manage_projects.html`, `templates/settings.html`, `templates/ledger.html`): reuse without creating new pages.

## Simple User Flow
1. User authenticates and enters any authenticated page.
2. The page shows a visible "signed in as" identity label in the shared navigation area.
3. User navigates to another authenticated page.
4. The same account identity remains visible and consistent.

## Success Criteria
- Users can state their active logged-in username from any authenticated page without opening a separate settings form.
- Identity display remains consistent when navigating between authenticated routes.
- No identity label appears on unauthenticated screens such as session reset.
