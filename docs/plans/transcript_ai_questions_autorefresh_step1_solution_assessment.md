# Transcript AI Questions Auto-Refresh - Step 1 Solution Assessment

## Problem statement
After transcript-driven updates are applied, the Questions field should refresh automatically from the AI backend (without architect approval) and visibly show regeneration progress.

## Option A: Inline regenerate during transcript apply
Pros:
- Single user action (`Apply selected updates`) handles both data updates and AI question refresh.
- Easy to show clear progress states in the Questions field (e.g., "Regenerating questions...").
- Guarantees questions are fresh immediately after a successful apply.
Cons:
- Slightly increases apply latency.
- Needs careful error handling so transcript updates still succeed if question generation fails.

## Option B: Background regenerate after apply returns
Pros:
- Faster perceived completion of transcript apply.
- Question refresh can retry independently from transcript update success.
- Easier to throttle/coalesce repeated applies.
Cons:
- More state complexity (queued/in-progress/completed/failed).
- Requires extra polling or push logic to update the Questions field progress/status.

## Option C: Synchronous overwrite in current questions update path only
Pros:
- Reuses existing questions write endpoint behavior.
- Minimal backend surface changes.
- Keeps admin manual edits available between transcript runs.
Cons:
- Harder to represent in-progress regeneration clearly during transcript apply.
- Couples AI generation too tightly to manual questions persistence paths.

## Recommendation
Option B: Background regenerate after apply returns. It matches your preferred UX where `Apply selected updates` can finish and close promptly, while the Questions field shows a short-lived regeneration state before the AI-refreshed questions appear.
