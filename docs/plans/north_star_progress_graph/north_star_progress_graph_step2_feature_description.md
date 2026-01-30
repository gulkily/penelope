# Step 2: Feature Description

## Problem
Residents and mentors cannot see progress trends over time because North Star progress is only shown as a current value.
The dashboard needs an expandable graph in the Objective section that visualizes progress history with per-resident date bounds.

## User stories
- As a resident, I want to see my North Star progress over time so that I can understand momentum.
- As a mentor, I want to review progress trends for a resident so that coaching conversations are grounded in data.
- As a program lead, I want the graph to be expandable from the Objective section so that the main dashboard stays compact.

## Core requirements
- The Objective section includes an expandable/collapsible progress graph per resident.
- The graph uses the resident's progress history data as its series input.
- Each resident has a stored graph start date and end date; for now these default to January 1 and January 31.
- The graph only displays data within the stored date bounds.
- Expanding or collapsing the graph does not disrupt current objective/goal/progress interactions.

## Shared component inventory
- Objective card in `templates/index.html`: reuse and extend to host the expandable graph surface.
- Progress history API (`GET /api/projects/{project_id}/progress/history`): reuse as the data source for the graph.
- Project/resident detail payload: reuse for current progress/goal/objective; extend only if the graph needs date bounds in the same payload.

## Simple user flow
1. Select a resident from the dashboard selector.
2. View the Objective section and expand the progress graph.
3. The graph renders progress history within the resident's start/end bounds.
4. Collapse the graph and continue updating objective, goal, or progress as usual.

## Success criteria
- Expanding the Objective section graph shows a time-series of progress for the selected resident.
- The graph respects the stored start (Jan 1) and end (Jan 31) bounds for every resident.
- Switching residents refreshes the graph to the correct resident data and bounds.
- Existing Objective/Goal/Progress interactions remain unchanged and responsive.
