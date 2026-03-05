# Add Update Confetti Trigger - Step 2 Feature Description

## Problem
Confetti currently fires when North Star slider progress increases, which celebrates metric adjustment rather than update capture. The celebration should move to the Add update workflow so feedback aligns with successful update application.

## User stories
- As a dashboard user, I want a celebration after I apply updates from the Add update dialog so that progress conversations feel acknowledged.
- As a dashboard user, I want no confetti when I move the North Star slider so that routine metric edits are not noisy.
- As a motion-sensitive user, I want the celebration behavior to continue respecting reduced-motion preferences so that the dashboard remains comfortable.

## Core requirements
- Trigger confetti once after a successful Add update apply action that submits at least one selected update.
- Do not trigger confetti from North Star slider changes.
- Do not trigger confetti when update application fails or when no updates are selected.
- Keep the confetti effect non-blocking and compatible with current cooldown behavior.
- Preserve existing reduced-motion handling.

## Shared component inventory
- Add update dialog (`templates/index.html`) and its `Apply selected updates` action: reuse as the canonical trigger surface.
- Transcript update application flow (`static/js/app.js`): extend the existing success path to trigger confetti once per successful apply.
- North Star slider change handling (`static/js/app.js`): extend by removing confetti trigger behavior while keeping progress save behavior intact.
- Confetti module (`static/js/confetti.js`): reuse existing trigger API and animation behavior; no new confetti component needed.
- Existing project update APIs (`/summary`, `/questions`, `/objective`, `/goal`, `/progress`, `/items`): reuse current endpoints; no backend contract changes required.

## Simple user flow
1. User opens `Add update` and reviews suggested updates.
2. User selects one or more updates and chooses `Apply selected updates`.
3. The selected updates are saved successfully.
4. Confetti plays once as confirmation.
5. User edits the North Star slider later without confetti firing.

## Success criteria
- Confetti appears once after successful update application from Add update.
- Confetti no longer appears from slider-only progress increases.
- Failed or no-op update attempts do not trigger confetti.
- Reduced-motion users do not see full animation behavior.
