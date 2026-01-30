# North Star Progress Confetti - Step 2 Feature Description

## Problem
North Star progress updates feel purely transactional; the dashboard lacks a lightweight celebratory cue when progress moves upward.

## User stories
- As a dashboard user, I want a celebratory effect when progress increases so that positive movement feels acknowledged.
- As a dashboard user, I want no celebration when progress decreases so that feedback stays meaningful.
- As a motion-sensitive user, I want the effect to respect reduced-motion preferences so that the dashboard remains comfortable to use.

## Core requirements
- Trigger the confetti effect only when the current project's progress value increases.
- Do not trigger the effect on initial load or when progress stays the same or decreases.
- The effect is brief, non-blocking, and does not interfere with slider interaction.
- The effect is bounded to avoid noticeable performance impact.
- The experience respects reduced-motion preferences.
- If a JS component is required, it lives in a dedicated file rather than `static/js/app.js`.

## Shared component inventory
- North Star progress slider + labels in the main dashboard (reuse as the trigger surface).
- Progress update handling in the dashboard frontend (extend to detect positive changes and trigger the effect).
- Progress update API (`PUT /api/projects/{id}/progress`) (reuse; no new backend behavior needed).
- New lightweight confetti visual layer (new UI element; no existing component covers this).

## Simple user flow
1. User selects a resident and moves the North Star progress slider upward.
2. The updated progress value is shown immediately.
3. A brief confetti effect appears on the page and then disappears.

## Success criteria
- Confetti appears when progress increases and does not appear on decreases or initial load.
- Reduced-motion users do not see the full animation.
- The dashboard remains responsive during the effect.
