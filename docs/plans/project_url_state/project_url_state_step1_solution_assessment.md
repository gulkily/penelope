# Project URL State - Step 1 Solution Assessment

Problem statement: Ensure the selected project is reflected in the URL so links are shareable and reloads preserve selection.

Option A - Use query string parameter (e.g., `?project=2`)
- Pros: Simple to implement, no routing changes, easy to share.
- Cons: Less clean URL than path-based routing.

Option B - Use path-based routing (e.g., `/projects/2`)
- Pros: Clean, semantic URLs; aligns with REST conventions.
- Cons: Requires server-side routing changes and potential template adjustments.

Option C - Use hash fragment (e.g., `#/project/2`)
- Pros: No server changes; client-only routing.
- Cons: Less standard for share links; can conflict with accessibility expectations.

Recommendation: Option A. Query parameters are low-effort, work with current routing, and are easy to implement in vanilla JS.
