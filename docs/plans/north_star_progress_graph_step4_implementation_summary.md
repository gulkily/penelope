## Stage 1 – Residency date bounds storage
- Changes: Added residency start/end date columns with January defaults and exposed them on the resident detail payload.
- Verification: Not run (requires loading a resident and confirming bounds are present).
- Notes: Defaults are set to January 1–31 of the current UTC year at initialization.

## Stage 2 – Expandable graph shell in Objective section
- Changes: Added the expandable graph container and toggle UI in the Objective card, plus baseline styling for the graph frame and a compact bottom-right toggle.
- Verification: Not run (requires loading the dashboard and toggling the graph container).
- Notes: Data wiring comes in the next stage.

## Stage 3 – Render history into the graph
- Changes: Added graph toggle behavior, pulled progress history for the active resident, filtered it to residency bounds, rendered an SVG line with markers plus range labeling, normalized history timestamps for safer parsing, and formatted the range label in UTC to avoid off-by-one displays.
- Verification: Not run (requires expanding the graph for a resident with progress history).
- Notes: The graph auto-refreshes after progress updates when expanded.

## Stage 4 – Graph empty state copy
- Changes: Added an empty-state message for residents with no history in the selected date range.
- Verification: Not run (requires expanding the graph for a resident with no history entries).
- Notes: Empty state is shown when no history is available or range is invalid.

## Stage 5 – Demo history seeding
- Changes: Added progress history entries to the demo data seed scripts so the graph has sample data.
- Verification: Not run (requires running the seed scripts and expanding the graph).
- Notes: History uses January dates aligned to the current UTC year.
