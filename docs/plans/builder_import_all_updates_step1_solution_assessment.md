# Builder Import All Updates - Step 1 Solution Assessment

Problem statement: The importer currently brings in only the latest check-in per builder, but we need the imported data to include all weekly updates from the source export.

Option A - Full historical import into section items (append all check-ins)
- Pros:
  - Meets the requirement directly: every weekly update is imported.
  - Preserves chronological history in app content, not just source DB.
  - Makes timeline/audit questions easier to answer in the app.
- Cons:
  - Higher risk of UI noise from many imported items per resident.
  - Needs stronger idempotency rules to avoid duplicates on reruns.

Option B - Keep latest snapshot in sections, store all older updates only as import notes
- Pros:
  - Lower risk to existing dashboard readability.
  - Smaller behavior change from current importer.
- Cons:
  - Does not truly satisfy "include all updates" in primary section content.
  - Historical updates become harder to use and compare in the app.

Option C - Two-mode import (default latest-only, optional `--include-history`)
- Pros:
  - Preserves current behavior for operators who want concise snapshots.
  - Enables full-history imports when needed.
  - Lower rollout risk through explicit operator choice.
- Cons:
  - Adds mode complexity and testing matrix overhead.
  - Can create inconsistent datasets across environments if mode choice differs.

Recommendation: Option A.

It best matches your stated goal and removes ambiguity around "missing" updates. We should keep idempotent mapping and deterministic ordering as non-negotiable guardrails in Step 2/3 so reruns stay safe.
