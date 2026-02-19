# Unauthenticated + Lobby Disabled Handling Step 2: Feature Description

## Problem
When an unauthenticated user reaches a protected page, the current recovery flow can route them to a disabled lobby path, creating a dead-end. The flow should attempt session restore first, then provide clear login guidance when restore is not possible.

## User Stories
- As a user, I want the app to automatically try restoring my session so that I can get back in without extra steps.
- As a user who is still unauthenticated after restore, I want a clear message that I am not logged in so that I understand my current state.
- As a user, I want instructions to use a magic link or request one from admins so that I know exactly how to regain access.
- As an operator, I want this behavior to work cleanly when lobby auth is disabled so that users are not sent into dead-end pages.

## Core Requirements
- Keep `/session/reset` as the unauthenticated landing surface for protected routes.
- Attempt session restore automatically when `/session/reset` loads.
- If restore fails, show a persistent “not logged in” state with guidance to use a magic link or request one from admins.
- Do not redirect to `/lobby` as the fallback path when lobby auth is disabled.
- Preserve successful restore behavior (redirect into the app when restore succeeds).

## Shared Component Inventory
- `app/main.py` auth middleware + `/session/reset` route: reuse as canonical unauthenticated entry.
- `templates/session_reset.html`: extend/reuse as canonical UI for post-restore failure messaging.
- `static/js/session_reset.js`: extend/reuse to remove dead-end redirect behavior and present guidance state.
- `app/api_auth.py` session restore endpoints (`/api/auth/session/challenge`, `/api/auth/session/restore`): reuse as existing restore mechanism.
- Lobby/magic-link surfaces (`/lobby`, `/settings/magic-links`): no new canonical page required; only referenced in user guidance copy.

## Simple User Flow
1. User accesses a protected route without an active session.
2. App redirects user to `/session/reset`.
3. Page automatically attempts key-based session restore.
4. If restore succeeds, user is returned to the app.
5. If restore fails, page shows “not logged in” guidance: use a magic link or request one from admins.

## Success Criteria
- Unauthenticated users continue to land on `/session/reset` for protected routes.
- Restore success path still redirects users into the app.
- Restore failure path no longer sends users into a disabled-lobby dead end.
- Failure UI clearly states the user is not logged in and provides magic-link/request guidance.
