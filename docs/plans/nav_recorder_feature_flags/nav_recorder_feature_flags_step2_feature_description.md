# Nav + Recorder Feature Flags Step 2: Feature Description

## Problem
Operators need to turn off selected navigation items (`Lobby`, `Settings`, `Manage residents`) and the dashboard recorder UI without changing code. Lobby authentication behavior also needs an independent control that does not depend on navbar visibility.

## User Stories
- As an operator, I want one navbar setting that defines which nav items are shown so that I can quickly tailor the visible navigation per deployment.
- As an operator, I want lobby authentication to be controlled separately so that I can disable auth workflow behavior without coupling it to navbar display.
- As a user, I want hidden features to disappear from the UI so that the app surface matches what is enabled.
- As a user, I want direct URLs to remain reachable so that existing bookmarks and operational links continue to work.

## Core Requirements
- Provide a single configuration setting that controls the enabled navbar item list (covering `Lobby`, `Settings`, `Manage residents`).
- Keep lobby authentication behavior behind a separate, independent setting.
- Control recorder visibility with its own UI-facing setting.
- Hide disabled navbar items and recorder UI from initial server-rendered HTML.
- Keep underlying routes/pages accessible even when their navbar item is hidden.

## Shared Component Inventory
- `templates/partials/navbar.html`: existing canonical navbar surface; extend/reuse as the only renderer of nav items.
- `templates/partials/top_nav.html`: existing wrapper include used across pages; reuse unchanged except for passing navbar data.
- `templates/index.html`: existing canonical recorder surface; extend to conditionally render recorder UI.
- `app/main.py` template context and page routes: extend to provide shared feature settings to templates while preserving route accessibility.
- `app/api_auth.py` + auth flow entry points: extend existing lobby auth surface to respect the separate lobby-auth setting.
- `static/js/lobby-indicator.js`: existing lobby badge behavior; reuse when Lobby nav item is enabled.

## Simple User Flow
1. Operator configures enabled navbar items, lobby-auth behavior, and recorder visibility.
2. User opens the app and sees only enabled navbar links plus enabled dashboard recorder UI.
3. User can still open direct URLs for pages whose navbar links are hidden.
4. Lobby authentication behavior follows its dedicated setting regardless of navbar visibility.

## Success Criteria
- Changing the single navbar setting reliably shows/hides `Lobby`, `Settings`, and `Manage residents` in navigation.
- Changing the recorder setting reliably shows/hides recorder UI on the dashboard.
- Changing the lobby-auth setting affects lobby authentication behavior independently of navbar visibility.
- Hidden navbar items are absent from server-rendered HTML, and direct page URLs remain accessible.
