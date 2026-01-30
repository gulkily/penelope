# Mentor Transcript Option C (Step 1: Solution Assessment)

## Problem statement
We need the transcript dialog to be usable on slow or unstable connections by reducing the impact of network latency and low bandwidth during analysis.

## Option C: Streaming/progressive results on top of async jobs
**Incremental path**
- Builds on Option B by streaming partial results as they are ready to cut perceived wait time.

**Pros**
- Shows early suggestions without waiting for the full response.
- Improves perceived latency on slow connections.
- Allows mentors to start review sooner.

**Cons**
- Highest complexity in client/server coordination.
- Requires partial-result UX and retry handling.
- More testing surface for flaky connections.

## Recommendation
Proceed with Option C when we need the best perceived responsiveness and can support streaming UX complexity.
