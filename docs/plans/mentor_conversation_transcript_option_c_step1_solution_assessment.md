# Mentor Transcript Option C (Step 1: Solution Assessment)

## Problem statement
We need evidence-backed transcript updates with server-side validation to eliminate unsupported suggestions before mentors review them.

## Option A: Evidence fields + client-only gating
**Pros**
- Minimal backend changes.
- Faster to ship than full server validation.

**Cons**
- Evidence can be bypassed by clients.
- Harder to enforce consistency across surfaces.

## Option B: Evidence schema + server validation
**Pros**
- Strong guardrails before suggestions reach the UI.
- Centralized enforcement for auditability.

**Cons**
- Requires new schema fields and backend logic.
- More effort to tune evidence requirements.

## Option C: Two-pass extraction (evidence first, then updates)
**Pros**
- Separates evidence collection from update generation.
- Easier to debug false positives.

**Cons**
- Two LLM calls and higher latency/cost.
- More moving parts to orchestrate.

## Recommendation
Option B: require evidence in the response schema and validate it on the server so the UI only sees supported, high-trust suggestions.
