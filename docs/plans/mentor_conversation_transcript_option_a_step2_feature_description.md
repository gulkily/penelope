# Mentor Transcript Option A (Step 2: Feature Description)

## Problem
The transcript dialog becomes frustrating on slow or unstable connections because mentors must wait for a full request/response cycle to see results or recover from a failed attempt.

## User stories
- As a mentor, I want the transcript dialog to feel responsive even on slow networks so that I can keep the conversation moving.
- As a mentor, I want my pasted transcript preserved if the connection drops so that I do not have to re-enter it.
- As a program lead, I want low-bandwidth users to complete transcript analysis without abandoning the flow so that updates remain consistent.

## Core requirements
- Keep mentors informed of analysis status, errors, and retry options within the transcript dialog.
- Preserve transcript input locally so it is not lost on refresh or temporary disconnects.
- Avoid extra network payload where possible during analysis requests.
- Maintain the existing review/apply workflow and existing update endpoints.

## Shared component inventory
- Transcript dialog UI: extend the existing dialog and its states in `templates/index.html`.
- Transcript analysis API: reuse the current `/api/projects/{project_id}/transcript` endpoint.
- Transcript prompt templates: reuse existing prompt files without introducing a new prompt system.
- Update endpoints: reuse current endpoints for summary, questions, objective, goal, progress, and list items.

## Simple user flow
1. Mentor opens the transcript dialog for a selected resident.
2. Mentor pastes a transcript; the dialog preserves the draft locally.
3. Mentor requests analysis and sees progress/status feedback with retry guidance if needed.
4. Mentor reviews suggestions and applies selected updates.

## Success criteria
- A mentor can retry analysis without re-pasting the transcript after a temporary failure.
- The dialog provides clear, in-context status and error feedback during analysis.
- Applying updates only changes selected fields and persists after reload.
