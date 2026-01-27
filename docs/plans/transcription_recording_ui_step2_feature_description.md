# Transcription Recording UI (Step 2: Feature Description)

## Problem
Mentors need an in-browser way to record audio, preview it, and upload it for transcription without leaving the dashboard.

## User stories
- As a mentor, I want to record an interview and preview it so that I know I captured the right audio.
- As a mentor, I want to upload the recording and see progress so that I understand when transcription is ready.
- As a program lead, I want the UI to be simple and consistent with the existing dashboard.

## Core requirements
- Provide start/stop recording controls using the browser microphone.
- Show a timer and basic recording status.
- Allow playback preview before upload.
- Allow uploading a pre-recorded audio file.
- Upload the audio file to the backend transcription endpoint.
- Show upload/transcription status and errors.

## Shared component inventory
- Transcript dialog: extend the existing transcript modal rather than creating a new page.
- Action buttons and field styles: reuse existing button and input styles.
- Backend transcription API: reuse `/api/transcriptions` for upload and response.

## Simple user flow
1. Mentor opens the transcript dialog and selects “Record”.
2. Mentor records the conversation and stops recording.
3. Mentor previews the recording and uploads it.
4. The transcript returns and is inserted into the transcript field for analysis.
5. (Alternate) Mentor uploads a pre-recorded file, then reviews the transcript.

## Success criteria
- A mentor can complete a record → preview → upload → transcript flow within the dialog.
- Upload progress/status is visible and errors are actionable.
- The transcript is inserted into the existing analysis flow without manual copy/paste.
