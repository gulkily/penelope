# Transcription Recording UI (Step 3: Development Plan)

1. Add recording UI controls in transcript dialog
   - Goal: Provide record/stop controls, timer, and status within the modal.
   - Dependencies: Existing transcript dialog markup.
   - Expected changes: Add UI elements in `templates/index.html` and styles in `static/css/main.css`.
   - Verification: Manual: open dialog and confirm controls render correctly.
   - Risks/open questions: Browser support for MediaRecorder.
   - Canonical components/APIs: Existing dialog layout and button styles.

2. Implement MediaRecorder logic
   - Goal: Capture audio via microphone and create a playable recording.
   - Dependencies: Stage 1 UI.
   - Expected changes: Client logic in `static/js/app.js` to manage MediaRecorder, timer, and audio preview.
   - Planned signatures: `startRecording()`, `stopRecording()`, `resetRecording()`.
   - Verification: Manual: record short clip, playback in dialog.
   - Risks/open questions: Permission denial handling.
   - Canonical components/APIs: None new.

3. Add pre-recorded file upload option
   - Goal: Allow users to select an audio file from disk for transcription.
   - Dependencies: Stage 1 UI.
   - Expected changes: File input in dialog, client state for selected file, preview using `<audio>`.
   - Verification: Manual: select file, see filename and playback.
   - Risks/open questions: File size/type validation.
   - Canonical components/APIs: `/api/transcriptions` endpoint.

4. Wire upload + progress feedback
   - Goal: Upload recorded/selected audio and show status/progress.
   - Dependencies: Stages 2–3, backend transcription endpoint.
   - Expected changes: Client upload logic (XHR or fetch stream) with progress updates and status messaging; write transcript text into the transcript textarea on success.
   - Verification: Manual: upload a file and see status + transcript inserted.
   - Risks/open questions: Progress accuracy when using fetch; may need XHR for reliable progress events.
   - Canonical components/APIs: `/api/transcriptions` response contract.
