# Interview Questions Template — Step 2 Feature Description

## Problem
Interview questions currently live in an image, which is hard to maintain and not convenient to reference while recording interviews in the app. We need a text-based source of truth and a built-in way to review it during interview capture.

## User Stories
- As a community architect, I want interview questions stored as a text template file so that updates are easy to maintain and version-control.
- As a community architect, I want to review the question list while recording an interview so that I can stay on script without switching tools.
- As a maintainer, I want the interview guide to be read-only in the app so that content governance stays in the template file workflow.

## Core Requirements
- The current question set from `screenshot/questions_from_architect_for_review.jpeg` is transcribed into a canonical text template file in the repository.
- Interviewers can access and read the template during the interview recording workflow without leaving the app.
- Reviewing the template does not alter resident/project data and does not interfere with recording/upload actions.
- The template preserves clear section structure so prompts are easy to scan live.
- If the template cannot be loaded, the UI shows a clear non-blocking message.

## Shared Component Inventory
- `templates/index.html` (`Add update` transcript dialog): extend this existing interview workflow surface to host or trigger question review; no separate interview page needed.
- `static/js/app.js` (transcript dialog behavior/state): extend existing dialog interactions so question review works alongside recording/upload/transcript analysis states.
- `templates/index.html` + `static/js/app.js` (`Questions` textarea + `/api/projects/{id}/questions` autosave path): keep as-is; this stores resident-specific notes and is not the canonical interview template.
- New read-only template-delivery surface: needed because current API/UI surfaces do not provide repository text assets for in-app display.

## Simple User Flow
1. Interviewer opens a resident and clicks `Add update`.
2. Interviewer opens the interview question guide from within that workflow.
3. Interviewer records audio (or uploads/pastes transcript) while referencing the guide.
4. Interviewer closes or minimizes the guide as needed and continues capture.
5. Interviewer completes transcript analysis/apply flow.

## Success Criteria
- A single canonical text template exists in-repo and contains the interview prompts from the screenshot.
- From the interview workflow, the question guide is reachable in one action and readable on desktop/mobile.
- Recording/upload/analyze controls remain usable while the guide is being referenced.
- No project fields are changed by viewing the guide.
- Missing-template scenarios show a clear message instead of breaking the interview flow.
