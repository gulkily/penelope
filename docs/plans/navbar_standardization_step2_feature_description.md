# Navbar Standardization Step 2: Feature Description

## Problem
Navigation is currently duplicated across multiple templates, causing drift and extra work when links change.

## User Stories
- As a developer, I want a single navbar template so that I can update links in one place.
- As a developer, I want optional links or badges to be handled consistently so that pages remain correct.

## Core Requirements
- Replace duplicated navbar markup with a shared Jinja include.
- Support existing links (Dashboard, Lobby with badge, Manage residents, Settings, Ledger where applicable).
- Preserve per-page variations (e.g., “Back to dashboard” on debug pages) without duplicating markup.
- Keep current styles and layout intact.

## Shared Component Inventory
- Existing link button styles in `static/css/main.css`: reuse.
- Existing page headers in `templates/*.html`: update to include the shared navbar.
- Existing lobby badge behavior via `static/js/lobby-indicator.js`: reuse where needed.

## Simple User Flow
1. Developer updates the shared navbar include.
2. All pages reflect the change without manual edits.

## Success Criteria
- All pages render navigation from the shared include.
- Updating the include updates navigation everywhere.
- No visual regressions in existing page headers.
