## Stage 1 – Relabel dashboard selection and context text
- Changes: Updated dashboard selector label, placeholder, manage link text, and empty state copy to use resident terminology.
- Verification: Not run (manual). Load the dashboard and confirm the selector, manage link, and empty state refer to residents.
- Notes: None.

## Stage 2 – Relabel management view to residents
- Changes: Updated the manage page title, headers, form labels, table labels, and helper copy to use resident terminology.
- Verification: Not run (manual). Visit `/projects` and confirm the page reads as resident management throughout.
- Notes: None.

## Stage 3 – Align frontend copy in JavaScript interactions
- Changes: Updated the console warning message to reference residents instead of projects.
- Verification: Not run (manual). Trigger a load failure and confirm the warning references residents.
- Notes: No user-facing JS copy required changes.

## Stage 4 – Validate API and schema naming strategy documentation
- Changes: Updated API error details and schema descriptions to reference residents while keeping `/projects` routes intact.
- Verification: Not run (manual). Call a non-existent resident ID and confirm the error detail uses resident terminology.
- Notes: Route paths and response shapes are unchanged.

## Stage 5 – Update docs and helper text where projects are referenced
- Changes: Updated settings helper copy and README wording to align with resident terminology while keeping technical routes intact.
- Verification: Not run (manual). Review settings copy and README for resident framing consistency.
- Notes: None.
