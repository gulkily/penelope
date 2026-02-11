# Lobby Auth Step 2: Feature Description

## Problem
The dashboard currently has no authentication, but the product requires a lobby-based approval flow where new visitors generate a keypair, submit a username, and wait for an existing user to approve their access.

## User Stories
- As a first-time visitor, I want to enter a username and be placed in a lobby so that I can request access without a password.
- As an approved user, I want to see a list of waiting users with codes and fingerprints so that I can approve or reject access.
- As a returning user, I want my session to persist so that I can access the app without repeating the lobby flow.
- As a multi-device user, I want separate approval codes per device so that each device can be approved independently.

## Core Requirements
- Client generates a disposable keypair in the browser, stores it in `localStorage`, and sends the public key to the server immediately.
- New visitors are blocked to a dedicated lobby page until approved; anonymous browsing outside the lobby is not allowed.
- The lobby issues a 6-digit code tied to a specific public key, supports multiple active codes per user, and expires codes after 14 days.
- Any already approved user can approve or reject pending lobby entries, and approvals/rejections are recorded in a ledger.
- Sessions never expire once approved; a missing session cookie triggers a reset/redirect page to restore the session state.

## Shared Component Inventory
- `templates/index.html` (main dashboard): reuse existing page, gated behind lobby approval.
- `templates/manage_projects.html`: reuse existing page, gated behind lobby approval.
- `templates/settings.html`: reuse existing page, gated behind lobby approval.
- `templates/confetti_debug.html`: reuse existing page, gated behind lobby approval.
- `/api/*` endpoints (`app/api.py`, `app/api_transcript.py`, `app/api_transcription.py`): reuse existing APIs, gated behind lobby approval.
- New lobby page: new canonical UI surface for username prompt, code display, and approval list.

## Simple User Flow
1. Visitor arrives and is prompted for a username.
2. Client generates a keypair, stores it locally, and sends the public key + username to the server.
3. Lobby page shows a 6-digit code and a waiting status.
4. Approved user sees the pending entry, reviews username + fingerprint + code, and approves or rejects.
5. On approval, the user gains full access and the session persists; rejection leaves them in the lobby.

## Success Criteria
- Unapproved visitors cannot access dashboard pages or APIs outside the lobby.
- Approved users can access all gated pages without re-approval, even across browser restarts.
- The lobby queue displays username, public key fingerprint, and code for each pending entry.
- Ledger records are created for approvals and username changes.
- Multiple devices for one identity can be approved independently via separate codes.
