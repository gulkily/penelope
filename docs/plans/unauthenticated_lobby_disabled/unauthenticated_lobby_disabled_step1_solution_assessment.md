# Unauthenticated + Lobby Disabled Handling Step 1: Solution Assessment

## Problem Statement
When an unauthenticated user lands in the app while lobby auth is disabled, the current session-reset flow sends them to `/lobby`, resulting in a dead-end instead of clear login recovery guidance.

## Option A: Session Reset as the Canonical Unauthenticated Entry
Pros:
- Reuses existing `/session/reset` surface and avoids adding new routes.
- Lets approved users still attempt key-based session restore.
- Can branch UX when `lobby_auth_enabled=false` (no redirect to lobby; show clear next steps).

Cons:
- Requires updating both server template context and `session_reset.js` redirect behavior.
- Session reset page copy/UI becomes slightly more stateful.

## Option B: New Dedicated Access-Unavailable Page
Pros:
- Very clear operator/user messaging for disabled-auth deployments.
- Clean separation from session-restore mechanics.

Cons:
- Adds another route/page to maintain.
- Requires additional redirect logic in auth middleware and JS.

## Option C: Keep Current Routes, Add Minimal Banner Only
Pros:
- Lowest engineering effort.
- Minimal routing changes.

Cons:
- Does not resolve the core dead-end redirect behavior.
- Users can still be pushed into a flow that cannot succeed.

## Recommendation
Option A is the best fit: keep `/session/reset` as the unauthenticated entry, attempt session restore first, and if restore fails show a clear “you are not logged in” state that tells the user to use a magic link or request one from admins. Do not redirect to `/lobby` when lobby auth is disabled. This fixes the dead end with minimal architectural change.
