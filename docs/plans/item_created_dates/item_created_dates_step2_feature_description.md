# Step 2: Feature Description

## Problem
List items do not show when they were added, which makes it harder to review timelines and recent updates at a glance.

## User stories
- As a resident, I want to see when each item was added so that I can track recent activity quickly.
- As a coach, I want item dates shown in a compact format so that I can scan updates without clutter.
- As a program lead, I want item dates captured automatically so that reporting stays consistent.

## Core requirements
- Each item records its creation date automatically and keeps it immutable afterward.
- Item dates are displayed alongside each list entry in a compact, readable format.
- Existing items load with their stored creation date; missing dates degrade gracefully.
- Item add, edit, delete, and undo flows continue to work without extra steps.

## Shared component inventory
- Dashboard section list items: reuse and extend the existing list rendering to include a compact date label.
- Project detail API payload: reuse and extend item data to include the creation date field.

## Simple user flow
1. Select a resident to view their lists.
2. Scan list items and see the compact date on each entry.
3. Add a new item and see its date appear immediately.
4. Edit or delete items without altering their original date.

## Success criteria
- Every item in the dashboard lists displays a creation date.
- New items show a date immediately after being added.
- Existing data continues to load without errors, even if a date is missing.
