# Mentor Transcript Option C (Step 1: Solution Assessment)

## Problem statement
We need evidence-backed transcript updates with server-side validation to eliminate unsupported suggestions before mentors review them.

## Option C: Two-pass extraction (evidence first, then updates)
**Pros**
- Separates evidence collection from update generation.
- Easier to debug false positives.

**Cons**
- Two LLM calls and higher latency/cost.
- More moving parts to orchestrate.

## Recommendation
Proceed with Option C when debugging precision and traceability outweigh the added latency and orchestration complexity.
