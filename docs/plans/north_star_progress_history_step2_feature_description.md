# Step 2: Feature Description

## Problem
North Star progress updates overwrite the previous value, so mentors cannot see how a resident's progress changes over time.
Without timestamped history, the team cannot generate accurate progress graphs later.

## User stories
- As a mentor, I want each resident's progress updates logged with timestamps so that I can generate progress graphs.
- As a program lead, I want progress history to be captured without slowing down the current dashboard workflow so that check-ins stay fast.
- As a resident, I want progress adjustments to be tracked over time so that my growth is transparent.

## Core requirements
- Every progress update for a resident is recorded as a timestamped history entry.
- Current progress behavior stays unchanged for the dashboard and existing APIs.
- History entries are tied to the correct resident and preserve the update value.
- Progress history is stored durably so it can be queried later for graphing.
- Logging happens for all progress updates triggered from the existing UI.

## Shared component inventory
- North Star progress slider + label on the dashboard: reuse as the primary input for progress updates; no new UI surface needed for logging.
- Progress update API used by the slider: reuse and extend behavior to capture history without changing the contract.
- Resident/project detail payload that provides current progress: reuse as-is so the dashboard stays stable.

## Simple user flow
1. Select a resident from the dashboard selector.
2. Drag the North Star progress slider to a new value.
3. See the current progress update immediately as it does today.
4. The system records the progress change with a timestamp for future graphing.

## Success criteria
- Each progress change results in a new timestamped history entry for that resident.
- The dashboard still displays and saves current progress with no visible regressions.
- Multiple updates on the same day are stored as distinct history entries.
- Progress history is retrievable per resident for future graphing work.
