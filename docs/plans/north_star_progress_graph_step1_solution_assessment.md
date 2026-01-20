# North Star Progress Graph - Step 1 Solution Assessment

Problem statement: Residents and mentors need a graph of North Star progress over time with per-resident date bounds that can expand from the Objective section.

Option A: Client-rendered graph powered by progress history, with per-resident graph bounds stored alongside resident data.
Pros:
- Reuses existing progress history data and keeps UI responsive.
- Minimal new backend logic; straightforward to expand within the Objective section.
Cons:
- Requires a small schema addition for per-resident bounds.
- Larger history sets may need client-side thinning later.

Option B: Backend-delivered graph series with server-side aggregation and stored bounds.
Pros:
- Centralizes graph logic and supports large histories efficiently.
- Keeps client rendering lighter and consistent across views.
Cons:
- More backend complexity and new API surface area.
- Higher upfront effort for aggregation and testing.

Option C: Write-time snapshots (daily/weekly) plus stored bounds, graph reads snapshots.
Pros:
- Produces clean, stable series for graphs.
- Avoids client-side thinning for long histories.
Cons:
- Adds data processing logic and storage of derived metrics.
- Harder to adjust if graph needs change later.

Recommendation: Option A, because it delivers the requested expandable graph fastest by reusing history data, while keeping the backend surface area small and leaving room to add aggregation later if history volume grows.
