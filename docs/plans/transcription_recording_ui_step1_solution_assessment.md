# Transcription Recording UI (Step 1: Solution Assessment)

## Problem statement
We need an in-browser recording experience that captures audio and prepares it for transcription without leaking API keys.

## Option A: Minimal MediaRecorder flow
**Pros**
- Fastest to ship and lowest complexity.
- Works in modern browsers without extra dependencies.

**Cons**
- Limited UX (basic start/stop, no waveform).
- Harder to manage long recordings or retries.

## Option B: Enhanced recorder with status + preview
**Pros**
- Better UX: timer, file size, and playback preview before upload.
- Easier to catch mistakes before transcription.

**Cons**
- More UI and state handling.
- Slightly longer implementation time.

## Option C: Chunked recording with resumable uploads
**Pros**
- Handles long sessions and unstable connections.
- Scales better for future large audio files.

**Cons**
- Highest complexity and backend coordination.
- Overkill for v1.

## Recommendation
Option B: add a small layer of UX polish (timer + preview) without the complexity of chunked uploads.
