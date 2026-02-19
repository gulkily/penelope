# Multi House Support - Step 1 Solution Assessment

Problem statement: The app needs to support residents/builders across multiple houses so data import, filtering, and operations are accurate per house.

Option A: Keep house as unstructured text in existing fields (for example, name/summary tags)
- Pros:
  - No schema or API changes.
  - Fastest short-term path.
- Cons:
  - Brittle parsing and inconsistent labels.
  - Weak filtering/reporting and poor long-term maintainability.

Option B: Add a structured `house` field to resident/project records (string enum-like value)
- Pros:
  - Simple model that fits current app architecture.
  - Enables clean filtering, grouping, and import mapping with low complexity.
  - Supports current known houses (`Actioners`, `SF2`) and future additions.
- Cons:
  - Requires a small schema and API contract update.
  - House metadata (location, manager, etc.) stays out-of-band unless expanded later.

Option C: Introduce normalized house entities plus foreign-key membership
- Pros:
  - Most scalable model for richer house-level features and governance.
  - Supports dedicated house metadata and stronger integrity.
- Cons:
  - Highest implementation and migration complexity.
  - More backend/UI surface area than needed for immediate import and operations.

Recommendation: Option B. It adds the minimum structure needed to reliably support multi-house workflows now, while keeping the system simple and leaving a clear upgrade path to Option C if house-level functionality expands.
