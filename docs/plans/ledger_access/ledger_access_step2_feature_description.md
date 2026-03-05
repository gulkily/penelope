# Ledger Access Step 2: Feature Description

## Problem
Admins need an in-app view of the approval ledger to answer who approved which user and when without touching the database directly.

## User Stories
- As an admin, I want to see a ledger of approval actions so that I can audit who approved which user.
- As an admin, I want to filter or scan recent approval activity so that I can respond to access questions quickly.
- As an admin, I want to access the ledger from the UI so that I do not need database access.

## Core Requirements
- Provide an authenticated, read-only ledger view in the app UI.
- Ledger entries must include: approver identity, approved user identity, action type, and timestamp.
- Access is limited to authenticated users (admin role assumption until roles are formalized).
- Ledger data is sourced from existing ledger events; no schema changes required.

## Shared Component Inventory
- Existing auth ledger storage (`ledger_events` table): reuse as source of truth.
- Existing page layouts (cards, tables, link buttons in `templates/` and `static/css/main.css`): reuse for ledger display.
- Existing auth middleware: reuse to gate access.
- New ledger page: new canonical UI surface for ledger browsing.

## Simple User Flow
1. Admin opens the Ledger page from the navigation.
2. The page loads recent ledger entries.
3. Admin scans entries for approvals and usernames.

## Success Criteria
- Admin can open a Ledger page and see approval entries with approver, approved user, and time.
- Ledger page is not accessible to unauthenticated visitors.
- Ledger data displayed matches events recorded in the database.
