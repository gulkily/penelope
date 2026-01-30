# Transcription Backend Forwarding (Step 1: Solution Assessment)

## Problem statement
We need a backend endpoint that accepts uploaded audio and forwards it to Dedalus for transcription while keeping API keys server-side.

## Option A: Simple proxy endpoint
**Pros**
- Fastest path to ship.
- Minimal moving parts (single request/response).

**Cons**
- Limited observability and error handling.
- No persistence or retries for failures.

## Option B: Proxy with validation + structured errors
**Pros**
- Validates file size/type and returns clear errors.
- Safer and more reliable for user-facing uploads.

**Cons**
- Slightly more logic to maintain.

## Option C: Upload to storage + async transcription job
**Pros**
- Scales to long recordings and large files.
- Allows retries and background processing.

**Cons**
- Requires storage + job queue infrastructure.
- More complex than needed for v1.

## Recommendation
Option B: add basic validation and structured errors while keeping the flow synchronous for v1.

## Speaker labeling note
- With single-mic, turn-taking audio, transcription should be solid but speaker labels are best-effort.
- If we want labels in v1, plan a lightweight post-processing step that adds “Speaker A/B”
  only when the transcript includes explicit cues; full diarization can wait for multi-mic input.
