Problem: The Summary and other section lists are fixed to insertion order, so users cannot reprioritize items to reflect current status. They need a way to rearrange items and keep that order stable.

User stories:
- As a user, I want to reorder Summary items so that the most important updates are at the top.
- As a user, I want to reorder Challenges, Opportunities, and Milestones so that lists reflect current priorities.
- As a user, I want reordered lists to persist across reloads and devices so I do not have to redo the ordering.

Core requirements:
- Users can reorder items within each section (Summary, Challenges, Opportunities, Milestones).
- Reordered positions persist per resident and section across refreshes and sessions.
- Reordering does not modify item content or timestamps.
- Existing add/edit/delete flows continue to work without breaking the stored order.
- The reordering affordance is discoverable and does not conflict with edit/delete actions.

Shared component inventory:
- Dashboard section lists (`.section-list` for Summary/Challenges/Opportunities/Milestones) reuse and extend the existing list rendering to support ordering changes.
- Item action controls (edit/save/cancel/delete) reuse the current controls; ordering integrates without replacing them.
- Items API surfaces (`/api/projects/{id}` payload and `/api/projects/{id}/items`, `/api/items/{id}` endpoints) extend to accept and return ordering data consistently.

Simple user flow:
1. User selects a resident on the dashboard.
2. User reorders items within a section list.
3. The list reflects the new order immediately.
4. User refreshes or returns later and sees the same order.

Success criteria:
- Users can reorder items in all four sections.
- The new order persists after a page refresh and after switching residents.
- Add/edit/delete actions preserve the intended order and do not reset it.
