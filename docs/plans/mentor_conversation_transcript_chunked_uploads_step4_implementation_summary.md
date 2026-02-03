## Stage 1 – Transcription upload contracts + constants
- Changes: Added shared transcription constants and new upload session schemas to support resumable uploads; wired existing transcription endpoint to shared constants.
- Verification: Not run (manual: run server and ensure existing `/api/transcriptions` still accepts a small audio upload).
- Notes: No behavior changes yet for upload flow.
