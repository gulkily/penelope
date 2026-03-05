# Mentor Conversation Transcript Chunked Uploads (Step 3: Development Plan)

1) Upload session API contracts
- Goal: Define resumable upload session lifecycle and response payloads.
- Dependencies: None beyond existing FastAPI router setup.
- Expected changes: New Pydantic models (e.g., UploadSessionCreateResponse, UploadChunkResponse, UploadCompleteResponse) and planned endpoint signatures:
  - POST `/api/transcriptions/uploads` -> `{upload_id, chunk_size, expires_at}`
  - PUT `/api/transcriptions/uploads/{upload_id}/chunks` (form: `chunk`, `index`, `total_chunks`) -> `{status, received_chunks}`
  - POST `/api/transcriptions/uploads/{upload_id}/complete` -> `TranscriptionResponse`
- Verification: Manual curl to create session and confirm response schema fields.
- Risks or open questions:
  - Confirm chunk size default and max file size alignment with existing 25MB limit.
- Canonical components/API touched: `app/schemas.py`, `app/api_transcription.py`.

2) Backend storage + reassembly path
- Goal: Store chunk payloads temporarily and reassemble into a single audio blob at completion.
- Dependencies: Stage 1 contract definitions.
- Expected changes: New module for upload session handling (e.g., `app/transcription_uploads.py`) with functions like:
  - `create_upload_session() -> UploadSession`
  - `store_chunk(upload_id: str, index: int, payload: bytes) -> UploadChunkResponse`
  - `assemble_upload(upload_id: str) -> tuple[bytes, str, str]`
- Verification: Manual upload of two chunks, complete session, confirm reassembly order/size.
- Risks or open questions:
  - Temp storage location and cleanup strategy for abandoned uploads.
- Canonical components/API touched: `app/api_transcription.py`, new upload helper module.

3) Backend transcription reuse
- Goal: Reuse the existing transcription request for both single and reassembled uploads.
- Dependencies: Stage 2 reassembly output.
- Expected changes: Extract transcription call into a helper signature like:
  - `async def transcribe_audio_bytes(payload: bytes, filename: str, content_type: str) -> TranscriptionResponse`
  - Wire `/api/transcriptions` and `/api/transcriptions/uploads/{upload_id}/complete` to the helper.
- Verification: Manual request to both endpoints with a small audio file.
- Risks or open questions:
  - Ensure validation (mime/size) matches current behavior for both paths.
- Canonical components/API touched: `app/api_transcription.py`, `app/schemas.py`.

4) Client chunking utility + state machine
- Goal: Implement client-side chunked upload with progress tracking and retries.
- Dependencies: Stage 1 endpoint contracts.
- Expected changes: Add upload helper functions in `static/js/app.js` (or a small new module) to:
  - Start session, upload chunks sequentially with retry/backoff.
  - Emit progress updates and status messaging for offline/failed chunks.
- Verification: Manual test with throttled network to see progress and retry messaging.
- Risks or open questions:
  - Decide retry limits and offline detection behavior.
- Canonical components/API touched: transcript upload controls, transcript status line.

5) Transcript dialog integration
- Goal: Connect chunked uploads to the existing record/upload UI and transcription flow.
- Dependencies: Stage 3 backend endpoints and Stage 4 client utility.
- Expected changes: Update record/upload submit handlers to route large files through chunked upload, then call completion to receive text and populate transcript; keep single-request path for small files.
- Verification: Manual flow for record, upload, and paste; confirm transcription inserts text and analysis still runs.
- Risks or open questions:
  - Determine file-size threshold for switching to chunked mode.
- Canonical components/API touched: transcript dialog, upload/record sections, `/api/transcriptions`, `/api/projects/{id}/transcript`.

6) Cleanup + abandonment handling
- Goal: Prevent orphaned upload data and ensure cancel/close behavior is safe.
- Dependencies: Stage 2 storage mechanism.
- Expected changes: Add server-side cleanup on completion and a best-effort pruning routine (e.g., on session create); client abort handling on dialog close.
- Verification: Manual: start upload, close dialog, confirm later uploads still work and no stale sessions block new ones.
- Risks or open questions:
  - How aggressive cleanup should be without background jobs.
- Canonical components/API touched: upload helper module, transcript dialog close handler.

7) Focused verification notes
- Goal: Ensure staged work is verified without full E2E automation.
- Dependencies: Prior stages.
- Expected changes: Add manual verification notes to the Step 4 implementation summary; optional lightweight HTTP test skeleton if time allows.
- Verification: Run through manual smoke steps documented per stage.
- Risks or open questions:
  - Decide whether to add HTTP tests now or defer to later test coverage work.
- Canonical components/API touched: `docs/plans/mentor_conversation_transcript_chunked_uploads_step4_implementation_summary.md` (future).
