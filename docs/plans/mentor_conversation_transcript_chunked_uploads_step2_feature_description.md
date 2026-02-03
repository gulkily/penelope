# Mentor Conversation Transcript Chunked Uploads (Step 2: Feature Description)

## Problem
Audio uploads for transcription fail on slow or unstable connections because they rely on a single request, forcing mentors to restart and risking lost work.

## User stories
- As a mentor, I want large audio uploads to resume after a connection drop so I do not have to start over.
- As a mentor, I want clear upload progress and retry guidance so I know the recording is still moving forward.
- As an admin, I want fewer support issues tied to failed uploads so transcription is dependable for low-bandwidth users.

## Core requirements
- Support resumable audio uploads with reliable chunk retry on transient failures.
- Preserve existing audio format limits and validation expectations.
- Provide explicit upload progress and state messaging during slow connections.
- Automatically continue the transcription flow once the upload is complete.
- Avoid regressions for small uploads and existing transcript analysis behavior.

## Shared component inventory
- Transcript dialog (add update flow): reuse and extend the existing upload/record sections for resumable progress and retry cues.
- Transcript status line: reuse for upload/transcription state messaging.
- Audio preview blocks (recording/upload): reuse without introducing new preview surfaces.
- Transcription upload API surface: extend the existing transcription upload workflow to accept resumable uploads.
- Transcript analysis API (`/api/projects/{id}/transcript`): reuse as-is after transcription returns text.

## Simple user flow
1. Mentor opens the transcript dialog and chooses record or upload.
2. The app uploads the audio with resumable progress and retries on connection drops.
3. Once the upload completes, transcription runs and inserts text into the transcript field.
4. Mentor reviews suggested updates and applies them.

## Success criteria
- Uploads complete without restart after a simulated connection drop on low bandwidth.
- Users see a clear progress indicator and actionable retry messaging during failures.
- Transcription success rate improves for larger files without impacting small uploads.
- No changes required to the transcript analysis step after text is generated.
