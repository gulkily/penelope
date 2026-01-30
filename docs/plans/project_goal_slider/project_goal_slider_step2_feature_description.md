# Step 2: Feature Description

## Problem
The progress slider currently tops out at 100%, which makes resident goals with real-world units (clients, MRR) feel disconnected and hard to track accurately.

## User stories
- As a resident, I want to set a numeric goal for my North Star so that progress reflects the real target.
- As a coach, I want to see progress in goal units so that reviews are grounded in actual outcomes.
- As a program lead, I want progress updates to remain quick and reliable so that weekly check-ins stay lightweight.

## Core requirements
- The progress slider range uses the resident's goal value as its maximum.
- Progress is displayed in goal units, not just a percent, and stays within 0..goal.
- Each resident has an editable, persisted goal value; existing residents without a goal have a safe default.
- Progress updates remain immediate and auto-saved during slider interaction.
- Changing a goal refreshes the slider range and displayed progress without breaking saved data.

## Shared component inventory
- North Star progress slider + label on the dashboard: reuse and extend to show goal-based range and values.
- Project detail API payload: reuse and extend to include the goal value needed for the slider.
- Progress update API: reuse and extend semantics to keep saving progress from the slider (no new endpoint).

## Simple user flow
1. Select a resident from the dashboard selector.
2. Enter or adjust the resident's goal value.
3. Drag the progress slider to update current progress.
4. See the progress value update relative to the goal.
5. Return later and see the saved goal and progress restored.

## Success criteria
- For a resident with goal N, the slider max is N and the displayed value reflects goal units.
- Updating progress persists and reloads correctly with the goal applied.
- Existing residents load without errors and have a clear default goal behavior.
- Changing a goal updates the slider range without losing prior progress meaning.
