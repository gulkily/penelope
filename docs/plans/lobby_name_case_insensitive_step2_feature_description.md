# Lobby Name Case-Insensitive Login — Step 2 Feature Description

## Problem
Users who enter a username with different casing (e.g., “Alex” vs “alex”) are treated as separate identities, but they should be linked to the same account.

## User Stories
- As a lobby user, I want logging in with a different-cased version of my name to link to my existing account so that I can access the same identity across devices.
- As an approver, I want approvals to respect case-insensitive name matching so that I don’t accidentally create duplicate accounts.
- As an admin, I want display names to preserve the original casing so that the UI remains consistent and human-friendly.

## Core Requirements
- Username matching for lobby linking is case-insensitive.
- The stored display name keeps the user’s chosen casing (no forced lowercasing in the UI).
- Case-insensitive linking applies to both initial approvals and subsequent login attempts.
- No behavior changes for distinct names that are not case-insensitive matches.
- The flow continues to allow multiple keys to link to one account.

## Shared Component Inventory
- Lobby request form + approvals list (`/lobby`, `static/js/lobby.js`): reuse, extend matching logic.
- Auth register/verify/approve APIs (`/api/auth/*`): reuse, extend name matching behavior.
- Account read/write (`/api/auth/me`, `/api/auth/username`): reuse as-is; display casing remains unchanged.
- Ledger events (approval + username updates): reuse; no new surface required.

## Simple User Flow
1. User enters a display name and submits a lobby request.
2. Approver sees the request and approves it.
3. If the submitted name is a case-insensitive match to an existing account, the request links to that account.
4. The approved user logs in and sees their existing identity preserved.

## Success Criteria
- Logging in with “Alex” and “alex” results in a single shared account after approval.
- No new accounts are created when a case-insensitive match already exists.
- The UI continues to show the original display name casing for the account.
