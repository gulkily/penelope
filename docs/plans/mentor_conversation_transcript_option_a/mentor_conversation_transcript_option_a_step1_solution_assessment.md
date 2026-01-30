# Mentor Transcript Option A (Step 1: Solution Assessment)

## Problem statement
We need the transcript dialog to be usable on slow or unstable connections by reducing the impact of network latency and low bandwidth during analysis.

## Option A: UI-only resilience + lighter requests
**Incremental path**
- Establishes baseline UI resilience (draft persistence, retries, lighter payloads) that Option B can build on with server-side jobs.

**Pros**
- No backend changes required.
- Faster perceived responsiveness with better in-dialog feedback.
- Reduces repeat uploads by persisting drafts locally.

**Cons**
- Does not reduce LLM processing time.
- Still requires a full request/response on slow connections.
- No cross-device resume.

## Recommendation
Proceed with Option A when we need the fastest relief for slow networks without backend changes.
