# Transcript AI Questions Auto-Refresh - Step 2 Feature Description

## Problem
Questions can become stale after transcript-driven updates because they still depend on explicit human selection and apply choices. The system should automatically refresh Questions from the AI backend after transcript apply, while showing visible regeneration progress in the Questions field.

## User stories
- As a community architect, I want Questions to auto-refresh after transcript apply so that follow-up prompts stay current without extra review clicks.
- As a community architect, I want to see a clear Questions regeneration state so that I know fresh prompts are still being prepared.
- As an admin, I want to retain manual Questions editing so that I can override or refine AI-generated prompts when needed.

## Core requirements
- After a successful transcript-driven apply action, trigger backend AI Questions regeneration automatically without requiring a separate approval checkbox for Questions.
- Use the background pattern so transcript apply can finish and close promptly while Questions regeneration continues.
- Show a visible status in the Questions field while regeneration is in progress, then replace it with refreshed AI output when complete.
- If regeneration fails, preserve existing Questions content and show a non-blocking failure state.
- Keep admin manual Questions editing available outside the automatic regeneration flow.

## Shared component inventory
- Add update transcript apply flow (`Apply selected updates` in transcript dialog): extend as the canonical trigger surface for automatic Questions refresh.
- Questions field surface on dashboard (editable for admins, read-only display for others): extend to render regeneration-in-progress and completion/error states.
- Existing transcript update apply orchestration and resident reload flow: reuse for post-apply background regeneration kickoff and result hydration.
- Existing Questions persistence contract (`PUT /api/projects/{id}/questions`): reuse for saving AI-generated Questions; no schema change required.
- Transcript analysis proposal surface: extend behavior so Questions generation no longer depends on architect selecting a proposed Questions change.

## Simple user flow
1. Architect opens `Add update`, reviews suggestions, and clicks `Apply selected updates`.
2. Selected transcript updates are applied and the dialog closes.
3. Questions field shows a regeneration-in-progress status.
4. Backend AI generation completes and Questions updates on the dashboard.
5. Admin can optionally edit the refreshed Questions afterward.

## Success criteria
- Transcript apply no longer requires architect approval of a Questions suggestion to refresh Questions.
- Questions field shows an observable in-progress state during regeneration.
- On success, Questions is replaced with fresh AI-generated follow-up questions.
- On failure, existing Questions remains intact and a non-blocking error state is visible.
- Admin users can still manually edit Questions after automatic refresh.
