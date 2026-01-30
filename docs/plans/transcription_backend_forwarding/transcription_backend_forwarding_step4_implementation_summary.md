## Stage 1 – Transcription response contract
- Changes: Added a `TranscriptionResponse` schema for transcript text + status/progress.
- Verification: Not run (schema review only).
- Notes: Status values are coarse; progress defaults to 100% for synchronous flow.

## Stage 2 – Upload + Dedalus forwarding endpoint
- Changes: Added `/api/transcriptions` endpoint with file validation, Dedalus forwarding, and structured errors; wired into app routing.
- Verification: Not run (requires API key + audio file).
- Notes: Supports common audio MIME types up to 25MB.

## Stage 3 – Progress/status response
- Changes: Response includes status/progress fields for UI progress display.
- Verification: Not run.
- Notes: Progress is coarse since Dedalus does not stream progress in this flow.
