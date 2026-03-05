# Lobby Badge Realtime Update — Step 1 Solution Assessment

## Problem Statement
The Lobby badge count in the navbar should update immediately after approve/reject actions on the Lobby page, instead of waiting for the polling interval.

## Option A — Add a shared client-side lobby-count event and trigger refresh on Lobby actions
- Pros:
  - Immediate UI update after approve/reject without waiting for the 15s poll.
  - Keeps a single source of truth for badge rendering in `static/js/lobby-indicator.js`.
  - Minimal backend risk; no API contract changes.
  - Can retain polling as fallback for cross-page/background changes.
- Cons:
  - Requires lightweight coordination between `static/js/lobby.js` and `static/js/lobby-indicator.js`.

## Option B — Update navbar badge directly inside `static/js/lobby.js` after each action
- Pros:
  - Fastest path with minimal new abstractions.
- Cons:
  - Duplicates badge logic across files and increases coupling.
  - Easier to regress when badge behavior changes in future.

## Option C — Replace polling with server push (SSE/WebSocket) for lobby counts
- Pros:
  - True realtime updates across all open sessions/pages.
- Cons:
  - Significantly larger scope and operational complexity.
  - Out of proportion for this focused UX fix.

## Recommendation
Option A. It delivers immediate updates for the targeted workflow with low risk, preserves current architecture, and keeps badge logic centralized while retaining poll-based resilience.
