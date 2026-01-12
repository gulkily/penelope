# Project Progress Update - Step 2 Feature Description

Problem: Admins need to adjust the project progress percentage directly so the dashboard reflects current status without database edits.

User stories:
- As an admin, I want to update a project's progress percentage so that the dashboard stays accurate.
- As a project lead, I want progress changes to be visible immediately after updates so that reviews are current.
- As a stakeholder, I want to see a single source of truth for progress so that status discussions stay aligned.

Core requirements:
- Allow admins to set a numeric progress percentage per project.
- Updates persist per project across sessions.
- The UI uses a slider control with clear feedback on the exact value.
- Progress changes update the visual progress bar and percentage display.
- Use the existing FastAPI + vanilla frontend stack (no new frameworks).

Shared component inventory:
- Reuse the project selector and project detail fetch flow.
- Extend the existing project API payload to include updated progress value (already present).
- Reuse the progress bar display; add an admin-only edit control adjacent to it.

Simple user flow:
1. Open the North Star dashboard.
2. Select a project.
3. Drag the progress slider to the desired percentage.
4. Save or confirm the new value.
5. See the progress bar and percentage reflect the update.

Success criteria:
- Progress updates persist and reappear after refresh or reselect.
- The slider shows the exact saved value and updates the display instantly.
- Non-selected states keep the slider disabled or hidden.
