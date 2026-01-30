# Mentor Transcript Option B (Step 1: Solution Assessment)

## Problem statement
We need the transcript dialog to be usable on slow or unstable connections by reducing the impact of network latency and low bandwidth during analysis.

## Option B: Async analysis job + server-side transcript storage
**Incremental path**
- Builds on Option A by moving long-running analysis to a server job with a resumable status flow.

**Pros**
- Returns a job ID quickly so the UI can poll and stay responsive.
- Allows resume after disconnects without re-uploading the transcript.
- Reduces bandwidth by reusing stored transcripts for retries.

**Cons**
- Requires backend storage and cleanup policies for transcripts and job state.
- More API surface area to maintain (status + result endpoints).
- Adds privacy/retention considerations.

## Recommendation
Proceed with Option B when resilience on low-bandwidth connections is a priority and backend changes are acceptable.
