# Mentor Transcript Improvements (Step 2: Feature Description)

## Problem
Transcript suggestions can surface unrelated or unclear updates and the dialog lacks resident context, which risks accidental changes during review.

## User stories
- As a mentor, I want suggested updates to only appear when the transcript supports them so that I can trust what I apply.
- As a mentor, I want to see the resident context while reviewing suggestions so that I avoid applying changes to the wrong person.
- As a program lead, I want the review flow to reduce accidental progress changes so that metrics remain accurate.

## Core requirements
- Suppress suggested updates when they match the current value or lack transcript support.
- Show the active resident name in the transcript dialog.
- Clarify progress suggestions by showing percent and units/goal context.
- Preserve the current apply/approve workflow and existing update endpoints.

## Shared component inventory
- Transcript dialog UI: extend the existing dialog in `templates/index.html` rather than creating a new page.
- Transcript prompt templates: reuse the existing prompt files and tighten rules (no new prompt system).
- Resident data API: reuse `/api/projects/{project_id}` for context and existing update endpoints for apply.
- Progress slider display: reuse current progress calculations for units/goal context.

## Simple user flow
1. Mentor opens the transcript dialog for a selected resident.
2. Mentor pastes a transcript and requests analysis.
3. The dialog shows only supported, meaningful suggestions with resident context.
4. Mentor reviews and applies a subset of suggested updates.

## Success criteria
- Suggestions do not appear for fields not mentioned in the transcript.
- The dialog clearly shows the resident name and progress context.
- Applying updates only changes the selected fields and persists on reload.
