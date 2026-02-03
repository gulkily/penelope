## Stage 1 – Transcription upload contracts + constants
- Changes: Added shared transcription constants and new upload session schemas to support resumable uploads; wired existing transcription endpoint to shared constants.
- Verification: Not run (manual: run server and ensure existing `/api/transcriptions` still accepts a small audio upload).
- Notes: No behavior changes yet for upload flow.

## Stage 2 – Upload session storage + chunk intake
- Changes: Added upload session storage module with temp filesystem backing and session TTL cleanup; introduced upload session creation and chunk intake endpoints with chunk tracking responses.
- Verification: Not run (manual: POST `/api/transcriptions/uploads` to get an upload id, then PUT a chunk to `/api/transcriptions/uploads/{id}/chunks` and confirm response status/received count).
- Notes: Chunked upload completion/transcription wiring comes next.
