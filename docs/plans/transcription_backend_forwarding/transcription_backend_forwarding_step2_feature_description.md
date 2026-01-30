# Transcription Backend Forwarding (Step 2: Feature Description)

## Problem
We need a backend endpoint that accepts audio uploads, forwards them to Dedalus for transcription, and returns text to the UI without exposing API keys.

## User stories
- As a mentor, I want to upload a recording and receive a transcript so that I can review it before applying updates.
- As an admin, I want the API key to remain server-side so that credentials stay secure.
- As a developer, I want clear validation errors so that the UI can guide users when uploads fail.

## Core requirements
- Accept audio uploads via `multipart/form-data`.
- Forward the file to Dedalus transcription and return the transcript text.
- Validate file type and size before forwarding.
- Return structured, user-friendly error responses on failure.
- Provide upload/transcription progress feedback to the UI (percent + status).

## Shared component inventory
- Dedalus API integration: extend the existing `DEDALUS_API_KEY` configuration.
- API routing: reuse the FastAPI router structure and error handling patterns.
- Transcript UI: reuse the existing transcript dialog as the consumer of the endpoint.

## Simple user flow
1. User records or selects an audio file and uploads it.
2. Backend validates and forwards the file to Dedalus.
3. Backend returns the transcript text to the UI.
4. User reviews and uses the transcript in the analysis flow.

## Success criteria
- Valid audio uploads return a transcript response within expected limits.
- Invalid file type/size returns a clear error without calling Dedalus.
- No API keys are exposed to the browser.
