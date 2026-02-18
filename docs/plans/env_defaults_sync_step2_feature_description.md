# Env Defaults Sync Step 2: Feature Description

## Problem
Operational settings evolve in `.env.example`, but existing `.env` files can miss newly introduced keys. Admins need launch-time behavior that keeps `.env` current with missing defaults while preserving already configured values.

## User Stories
- As an admin, I want missing default settings from `.env.example` added to `.env` on launch so that new features have visible configurable keys.
- As an admin, I want existing `.env` values preserved so that launch-time sync does not override my deployment-specific configuration.
- As a developer, I want the sync behavior to run consistently regardless of launch path so that local and production startup behavior stays predictable.

## Core Requirements
- On app launch, append missing keys from `.env.example` into `.env`.
- Never overwrite existing keys already present in `.env`.
- Preserve existing `.env` key ordering/content and avoid duplicate keys.
- If `.env` does not exist, create it from `.env.example` defaults.
- Keep launch resilient: sync issues should be surfaced clearly without silently corrupting `.env`.

## Shared Component Inventory
- `app/main.py`: existing startup/bootstrapping entrypoint; extend/reuse as canonical launch-time hook for env sync.
- `.env.example`: existing canonical source of default settings; reuse as authoritative defaults catalog.
- `.env`: existing operator-managed runtime config file; extend/reuse by appending only missing keys.
- `start.sh` and `scripts/pnl.py`: existing launch helpers; no new canonical logic needed if sync is centralized in app startup.

## Simple User Flow
1. Admin updates app code containing new settings in `.env.example`.
2. Admin launches the app.
3. Startup sync checks `.env` against `.env.example` and appends only missing keys.
4. App continues startup with existing configured values unchanged.

## Success Criteria
- After launch, any key in `.env.example` missing from `.env` is present in `.env`.
- Existing keys in `.env` keep their original values.
- Launch from standard entrypoints results in the same `.env` synchronization behavior.
- No duplicate keys are introduced for settings that already existed in `.env`.
