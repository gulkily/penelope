# Mentor Transcript Option B (Step 1: Solution Assessment)

## Problem statement
We need evidence-backed transcript updates with server-side validation to eliminate unsupported suggestions before mentors review them.

## Option B: Evidence schema + server validation
**Pros**
- Strong guardrails before suggestions reach the UI.
- Centralized enforcement for auditability.

**Cons**
- Requires new schema fields and backend logic.
- More effort to tune evidence requirements.

## Recommendation
Proceed with Option B when we want consistent, enforceable evidence requirements across all clients and review surfaces.
