# Resident Summary Section - Step 2 Feature Description

Problem: Residents need a single narrative summary that captures the current state at a glance; today the dashboard only offers list-based items and does not provide a concise per-resident summary block.

User stories:
- As a resident manager, I want to record a short summary for each resident so that I can quickly understand their status.
- As a team member, I want to scan a resident's summary before the detailed sections so that I can orient myself fast.
- As an owner, I want the summary to persist per resident so that it stays consistent across sessions.

Core requirements:
- Each resident has exactly one summary field that stores free-form text.
- The summary is visible and editable within the same header section as the resident selector.
- Summary content persists per resident and reloads correctly when switching between residents.
- The summary is distinct from the existing item-based Summary list and does not alter those items.
- Empty summaries display a clear prompt without blocking other dashboard interactions.

Shared component inventory:
- Resident selector header (existing) — extend to include the summary field in the same section.
- Field input styling (existing) — reuse standard text area/input styling for consistency.
- Resident detail API payload (existing) — extend to include the summary field for load/save.
- Questions text editing behavior (existing) — reuse the same interaction pattern for text updates to minimize new UX patterns.

Simple user flow:
1. User selects a resident.
2. The summary section displays the current saved text or an empty prompt.
3. User edits the summary.
4. The summary is saved and remains when the user switches residents or reloads.

Success criteria:
- Summary text is unique per resident and persists across reloads.
- Switching between residents updates the summary field to the correct content.
- Existing dashboard sections (Summary items, Challenges, Opportunities, Milestones) behave unchanged.
- Users can update the summary without leaving the dashboard.
