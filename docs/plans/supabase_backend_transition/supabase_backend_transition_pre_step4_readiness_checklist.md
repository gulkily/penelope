# Supabase Backend Transition - Pre-Step-4 Readiness Checklist

Purpose: Prepare everything needed for a future Step 4 execution without starting implementation now.
Status: Planning is ready for future execution (Steps 1-3 complete); implementation has not started.

Current status:
- Step 1-3 planning docs are drafted.
- Step 4 implementation is intentionally deferred.
- Team currently lacks Supabase credentials and in-house Supabase experience.

## 1) Business and scope gate (PM + manager)
- [ ] Confirm this transition is officially prioritized.
- [ ] Confirm Option B scope remains locked: database backend swap only (no auth/UI contract redesign).
- [ ] Define target window (quarter/month) and owner for cutover decision.
- [ ] Confirm success criteria that must be met before production cutover.

## 2) Access and environment gate (admin + security/IT)
- [ ] Obtain Supabase non-production project access for development/testing.
- [ ] Obtain credentials needed by the app (`DATABASE_URL` and any required secret handling path).
- [ ] Confirm where secrets are stored and who can rotate/revoke them.
- [ ] Confirm network/IP allowlist and compliance requirements (if any).

## 3) Knowledge ramp gate (developer)
- [ ] Complete a short Supabase fundamentals pass focused on Postgres usage, roles, and connection settings.
- [ ] Document team conventions for local/staging/prod Supabase configuration.
- [ ] Validate ability to connect from local app to Supabase non-prod with a minimal read/write smoke test.

## 4) Operational readiness gate (developer + admin)
- [ ] Define backup/restore expectations for Supabase-backed runs (replacing SQLite file-copy assumptions).
- [ ] Define rollback trigger and authority (who can decide to revert to SQLite and within what window).
- [ ] Define migration dry-run dataset and data parity sign-off format.
- [ ] Define staging verification checklist for critical flows (projects/items/progress/auth/lobby/magic links/users/ledger).

## 5) Pre-implementation artifact pack (prepare now)
- [ ] One-page executive brief for manager: scope, risk, timeline, prerequisites, rollback.
- [ ] Credential request template (who needs what access and why).
- [ ] Supabase onboarding notes for this repo (env vars, local run, test run).
- [ ] Draft cutover runbook skeleton (fill details during actual Step 4).

## 6) Go/No-Go to start Step 4
Step 4 should start only when all statements are true:
- [ ] Scope approval is documented.
- [ ] Non-prod Supabase access is working for the developer.
- [ ] Secrets handling path is approved.
- [ ] Rollback owner and rollback window are defined.
- [ ] Staging verification checklist and parity-report format are agreed.

Decision record:
- Sponsor/manager:
- Technical owner:
- Earliest Step 4 start date:
- Notes:
