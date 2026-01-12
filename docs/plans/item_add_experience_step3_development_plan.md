# Item Add Experience - Step 3 Development Plan

1. Stage 1 - Add inline add rows to each section
   - Goal: Provide always-visible add inputs within each card.
   - Dependencies: Existing section card markup and add-item API.
   - Expected changes: Update HTML to include an input (or textarea) and add button per section; add data attributes for section identification.
   - Verification: Load the dashboard and confirm add rows appear under each section.
   - Risks/open questions: Ensure layout stays compact on smaller screens.
   - Shared components/API contracts: Reuse `POST /api/projects/{project_id}/items`.

2. Stage 2 - Wire inline add rows to backend
   - Goal: Submit new items without modal dialogs.
   - Dependencies: Stage 1.
   - Expected changes: Add JS handlers to submit on Enter or button click; clear inputs on success; refresh the list.
   - Verification: Add items to each section and confirm persistence after refresh.
   - Risks/open questions: Decide on validation for empty or whitespace-only input.
   - Shared components/API contracts: Uses existing create-item endpoint.

3. Stage 3 - Make add and edit inputs expandable
   - Goal: Allow longer text to expand the input height for readability.
   - Dependencies: Stage 1 (markup) and existing edit flow.
   - Expected changes: Replace add inputs with auto-growing textareas; extend edit inputs to use the same auto-grow behavior.
   - Verification: Enter multi-line text and confirm the input expands in both add and edit modes.
   - Risks/open questions: Ensure Enter still submits while allowing line breaks (maybe Shift+Enter for newline).
   - Shared components/API contracts: None.

4. Stage 4 - Styling and UX polish
   - Goal: Keep inline add rows visually consistent with the card layout.
   - Dependencies: Stages 1–3.
   - Expected changes: Add CSS for inline add rows, focus states, and expanded inputs.
   - Verification: Visual check on desktop and mobile widths.
   - Risks/open questions: Avoid making cards feel crowded.
   - Shared components/API contracts: None.
