## Stage 1 – Recording UI controls
- Changes: Added recording and upload UI sections inside the transcript dialog.
- Verification: Not run (manual UI review recommended).
- Notes: Recording section includes timer and preview; upload section handles files.

## Stage 2 – MediaRecorder logic
- Changes: Added MediaRecorder start/stop flow, timer, and audio preview handling in the dialog.
- Verification: Not run (requires mic permission).
- Notes: Recording resets on dialog close.

## Stage 3 – Pre-recorded file upload
- Changes: Added file input, preview, and clear flow for pre-recorded audio.
- Verification: Not run (manual file select recommended).
- Notes: Uses `<audio>` for playback preview.

## Stage 4 – Upload + status feedback
- Changes: Added upload logic for recordings and files, wired to `/api/transcriptions`, and display upload/transcription status in the dialog.
- Verification: Not run (requires backend endpoint + API key).
- Notes: Uses fetch for uploads; status is coarse without byte-level progress.
