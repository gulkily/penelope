## Stage 1 – Transcription upload contracts + constants
- Changes: Added shared transcription constants and new upload session schemas to support resumable uploads; wired existing transcription endpoint to shared constants.
- Verification: Not run (manual: run server and ensure existing `/api/transcriptions` still accepts a small audio upload).
- Notes: No behavior changes yet for upload flow.

## Stage 2 – Upload session storage + chunk intake
- Changes: Added upload session storage module with temp filesystem backing and session TTL cleanup; introduced upload session creation and chunk intake endpoints with chunk tracking responses.
- Verification: Not run (manual: POST `/api/transcriptions/uploads` to get an upload id, then PUT a chunk to `/api/transcriptions/uploads/{id}/chunks` and confirm response status/received count).
- Notes: Chunked upload completion/transcription wiring comes next.

## Stage 3 – Upload completion + transcription reuse
- Changes: Added transcription helper for raw audio bytes, wired chunked upload completion endpoint to reassemble audio and reuse existing transcription flow, and normalized content-type handling for chunk uploads.
- Verification: Not run (manual: complete chunked upload then POST `/api/transcriptions/uploads/{id}/complete` and confirm transcript text response).
- Notes: Cleanup runs after successful completion only.

## Stage 4 – Client chunked uploads + dialog integration
- Changes: Added chunked upload client with retry/backoff, progress messaging, and resumable session handling; wired transcript upload/record flows to choose chunked uploads for larger files and keep transcript draft updates on success.
- Verification: Not run (manual: throttle network, upload a large audio file, observe progress/retry messaging, confirm transcript insertion).
- Notes: Resume is per-dialog session; closing the dialog cancels pending uploads.

## Stage 5 – Upload cancellation + offline messaging
- Changes: Guarded resumable sessions by file match, refined offline messaging for single vs chunked uploads, and ensured upload cancellation/cleanup on dialog reset.
- Verification: Not run (manual: start a chunked upload, toggle offline to pause, then retry; close dialog mid-upload to confirm cancel/reset).
- Notes: Chunked resume requires the same file name and size.

## Stage 6 – Disabled transcript button affordance
- Changes: Added disabled styling for link buttons and surfaced a tooltip on the transcript button when no resident is selected.
- Verification: Not run (manual: clear selection/await load, confirm button is visibly disabled and tooltip appears on hover).
- Notes: None.

## Stage 7 – Broader MIME support + error detail
- Changes: Allowed additional common audio MIME types (m4a/3gpp) for uploads and surfaced server error detail for failed single uploads.
- Verification: Not run (manual: upload an m4a file under 5MB and confirm upload succeeds; upload an unsupported type to confirm descriptive error).
- Notes: None.
