## Stage 1 – Residency date bounds storage
- Changes: Added residency start/end date columns with January defaults and exposed them on the resident detail payload.
- Verification: Not run (requires loading a resident and confirming bounds are present).
- Notes: Defaults are set to January 1–31 of the current UTC year at initialization.

## Stage 2 – Expandable graph shell in Objective section
- Changes: Added the expandable graph container and toggle UI in the Objective card, plus baseline styling for the graph frame.
- Verification: Not run (requires loading the dashboard and toggling the graph container).
- Notes: Data wiring comes in the next stage.
