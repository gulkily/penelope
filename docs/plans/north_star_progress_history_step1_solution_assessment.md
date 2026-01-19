# North Star Progress History - Step 1 Solution Assessment

Problem statement: Mentors need each resident's progress updates logged with timestamps so progress can be graphed later.

Option A: Append-only progress history log while keeping the current progress value as-is.
Pros:
- Preserves current UX and data access patterns.
- Enables straightforward time-series queries for graphs.
Cons:
- Requires dual writes and storage growth over time.

Option B: Make the history log the source of truth and derive current progress from the latest entry.
Pros:
- Single authoritative source for progress data.
- Guarantees history and current values never diverge.
Cons:
- Adds read complexity for current progress views.
- Requires a backfill or default for existing residents.

Option C: Store progress history inside each resident record as a serialized timeline.
Pros:
- Avoids a separate history store.
- Simple to reason about per-resident data ownership.
Cons:
- Harder to query and aggregate for graphs.
- Increased risk of update conflicts and bloated records.

Recommendation: Option A, because it adds history without disrupting current workflows and keeps graphing viable with minimal complexity.
