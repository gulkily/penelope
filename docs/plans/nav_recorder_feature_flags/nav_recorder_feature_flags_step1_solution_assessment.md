# Nav + Recorder Feature Flags Step 1: Solution Assessment

## Problem Statement
We need a reliable way to hide `Lobby`, `Settings`, `Manage residents`, and the dashboard `Recorder` UI when disabled, with one setting controlling navbar visibility and a separate flag for lobby authentication behavior.

## Option A: Server Flags + Centralized Navbar List (Single Navbar Setting)
Pros:
- Keeps visibility decisions in one backend source of truth.
- Prevents disabled links/sections from being rendered in initial HTML.
- Fits the existing FastAPI + Jinja architecture and shared navbar partial.
- Avoids scattered template conditionals by defining nav items in one server-side list.
- Uses one navbar setting (list of enabled nav items) instead of multiple per-link toggles.
- Supports separate concerns: `lobby_auth_enabled` for auth behavior and a separate recorder visibility flag for UI.

Cons:
- Requires passing rendered/filtered navbar data plus flags into template context.
- Requires a small refactor of current navbar partial rendering.
- Needs simple validation for unknown/typoed navbar item keys.

## Option B: Client-Side Flag Fetch + DOM Hiding
Pros:
- Centralized frontend toggle logic once loaded.
- Minimal backend template changes.

Cons:
- Disabled items can flash before JS runs.
- Frontend-only hiding is easier to bypass and less trustworthy.
- Adds coupling between many pages and JS bootstrapping.

## Option C: Route-Level Access Gating Only
Pros:
- Strong backend enforcement for disabled pages.
- Minimal UI/template work.

Cons:
- Navbar/dashboard still expose links or controls unless separately hidden.
- UX degrades into dead-end navigation/redirect behavior.

## Recommendation
Option A is the best fit: use server-defined flags with a centralized navbar item list, controlled by one navbar setting, keep `lobby_auth_enabled` separate, and conditionally render navbar items plus recorder UI only (while keeping routes accessible). This gives clean UX, clear operational control, and minimal ongoing maintenance cost.
