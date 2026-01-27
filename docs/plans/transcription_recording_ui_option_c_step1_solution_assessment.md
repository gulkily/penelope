# Transcription Recording UI Option C (Step 1: Solution Assessment)

## Problem statement
We may need to support long recordings and unreliable networks, which requires chunked recording and resumable uploads.

## Option A: Browser chunking + single POST finalize
**Pros**
- Minimal backend changes.
- Still improves resilience over single-blob uploads.

**Cons**
- Large in-memory buffers on the client.
- Upload retries are still coarse-grained.

## Option B: Client chunking + server reassembly
**Pros**
- Allows retry per chunk.
- Keeps backend in control of final file integrity.

**Cons**
- Requires temporary storage and cleanup logic.
- More moving parts on both client and server.

## Option C: Direct-to-storage + async transcription
**Pros**
- Best scalability for long recordings.
- Decouples upload time from transcription time.

**Cons**
- Requires storage + job queue infrastructure.
- More operational overhead.

## Recommendation
Option B if we must support long recordings soon; otherwise defer to Option C only when storage/job infrastructure exists.
