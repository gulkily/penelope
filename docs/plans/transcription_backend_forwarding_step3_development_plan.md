# Transcription Backend Forwarding (Step 3: Development Plan)

1. Define transcription request/response contract
   - Goal: Formalize the payloads the UI will send/receive.
   - Dependencies: Step 2 requirements.
   - Expected changes: Add Pydantic models for transcription requests/responses, including progress status fields.
   - Planned signatures: `TranscriptionResponse(text: str, status: str, progress: int | None)`.
   - Verification: Manual validation of example payloads against schemas.
   - Risks/open questions: How to represent processing vs upload progress distinctly.
   - Canonical components/APIs: Existing API schema patterns in `app/schemas.py`.

2. Add upload + forwarding endpoint
   - Goal: Accept multipart audio uploads and forward to Dedalus.
   - Dependencies: Stage 1 schemas, Dedalus API key available in env.
   - Expected changes: New FastAPI route (e.g., `POST /api/transcriptions`) with file validation (size/type), Dedalus call via `httpx`, and structured errors.
   - Planned signatures: `async def transcribe_audio(file: UploadFile) -> TranscriptionResponse`.
   - Verification: Manual POST with a small audio file; confirm transcription text returns.
   - Risks/open questions: File size limits and supported MIME types.
   - Canonical components/APIs: `DEDALUS_API_KEY` config, FastAPI router patterns.

3. Progress/status reporting shape
   - Goal: Provide upload/transcription progress feedback to the UI.
   - Dependencies: Stage 2 endpoint.
   - Expected changes: Include simple status fields in the response (`status: queued|processing|complete|error`), and support `Retry-After` or polling guidance if needed.
   - Planned signatures: `status: str`, `progress: int | None` in the response model.
   - Verification: Manual smoke test of status values for success/error.
   - Risks/open questions: If Dedalus does not return progress, we may only provide coarse status.
   - Canonical components/APIs: Response contract for the new transcription endpoint.
