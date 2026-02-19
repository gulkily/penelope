# Multi House Support - Step 2 Feature Description

## Problem
The app currently treats residents as one undifferentiated list, which makes it hard to operate across multiple houses.  
We need structured house support so imported builders and day-to-day workflows can be filtered and understood by house.

## User stories
- As a community architect, I want each resident tied to a house so that I can manage residents by location/group.
- As a community architect, I want to filter the resident selector by house so that I can focus on one house at a time.
- As an operator, I want to filter resident lists by house so that I can run house-specific reviews and updates.
- As a mentor, I want to see a resident's house context while viewing their dashboard so that coaching context is clear.
- As a user, I want my house filter choice to persist so that I do not need to reselect it after navigation or refresh.

## Core requirements
- Each resident has one structured house value stored with their profile.
- House is required on resident creation/update and must be selected from a fixed normalized list.
- The fixed house list for this phase is exactly: `Unassigned`, `Actioners`, `SF2`.
- House data is included in resident/project API payloads used by the UI.
- Dashboard and resident management views provide a basic house filter control.
- Resident management supports editing resident house values directly in the table workflow.
- House filter defaults to `All houses`.
- House filtering is a UX/data convenience feature in this phase (no role-based permission changes).
- Dashboard resident selector only shows residents that match the active house filter.
- House filter state persists in URL query parameters and is remembered for the user.
- Existing residents without house data are auto-assigned to `Unassigned` during migration/backfill.
- House metadata remains optional for now; the feature focuses on reliable house assignment and filtering.

## Shared component inventory
- Dashboard resident selector (`templates/index.html`, `static/js/app.js`): reuse existing selector flow; extend it to expose house context/filtering rather than creating a separate dashboard.
- Resident management table (`templates/manage_projects.html`, `static/js/manage-projects.js`): reuse existing management surface; extend it to display and manage house values.
- Projects list API (`GET /api/projects` in `app/api.py` + `app/db_projects.py`): reuse existing canonical list endpoint; extend response/query behavior to carry house and support house-based filtering.
- Project detail API (`GET /api/projects/{project_id}` in `app/api.py` + `app/db_projects.py`): reuse existing detail payload; extend it to include the resident's house.
- Project create/update API surfaces (`POST /api/projects` and existing update surfaces): extend canonical resident lifecycle APIs so house assignment stays in the same workflow.

## Simple user flow
1. Open resident management and assign or confirm a house for each resident.
2. Filter residents by house in management to verify grouping.
3. Open the dashboard and filter/select residents by the same house context.
4. View resident details with house context visible for coaching and operations.

## Success criteria
- Residents can be consistently assigned to a house and retrieved with that value across app sessions.
- Resident creation cannot complete without a valid house selection from the fixed list.
- Existing residents with missing house values are automatically set to `Unassigned`.
- House filtering returns correct subsets in both management and dashboard views.
- Dashboard selector options always match the active house filter.
- House filter defaults to `All houses`, persists across refresh/navigation, and is shareable via URL state.
- House values are normalized consistently regardless of input casing.
- Imported residents from multi-house data appear under the expected houses without manual relabeling.
- Existing resident workflows (selection, updates, archiving) continue to work with house support enabled.
