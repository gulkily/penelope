# Staging E2E Setup

This guide explains how to run the full E2E suite safely on staging, and how to run a read-only subset against production.

## 1) Staging Environment Requirements
- Use an isolated staging database (never production DB).
- Deploy the same code revision as `main`.
- Keep staging URL and credentials separate from production.
- Start app with staging `.env` values (feature flags + auth settings) and restart app after `.env` changes.

Suggested staging `.env` values for test coverage:
- `MAGIC_LINK_ADMIN_USERNAMES=<staging-admin-username>`
- `NAVBAR_ENABLED_ITEMS=lobby,projects,settings`
- `LOBBY_AUTH_ENABLED=true`
- `RECORDER_ENABLED=true` (or false, depending on target behavior you want covered)

## 2) Run Full E2E Against Staging
The full suite uses injected local auth cookies and is intended for local/staging targets reachable as localhost.

1. On the staging host, start app:
   - `./start.sh`
2. In another terminal on the same host, run:
   - `./pnl test e2e`
   - or `python3 -m pytest tests/e2e -q`
3. Optional Firefox run:
   - `python3 -m playwright install firefox`
   - `python3 -m pytest tests/e2e --browser firefox -q`

## 3) Run Safe Read-Only Smoke Against Production
Use the `prod_smoke` marker for production-like checks.

Command:
- `E2E_BASE_URL=https://<your-production-host> python3 -m pytest tests/e2e -m prod_smoke -v -rs --maxfail=1`

What `prod_smoke` covers:
- `/welcome` reachable
- `/lobby` reachable (enabled or disabled message)
- `/api/projects` requires auth (401)

What it does not do:
- No resident creation/updates/deletes
- No archive toggles
- No transcript/apply mutation flows

## 4) Common Failure Mode: Every Test Shows `E`
If almost all tests error:
- app is not running/reachable
- app was not restarted after `.env` changes
- Playwright browsers are missing

Quick checks:
- `curl -I http://127.0.0.1:8000/welcome`
- `python3 -m playwright install`
- `python3 -m pytest tests/e2e -x -vv -rs`
