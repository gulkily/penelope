# Step 1: Solution Assessment

## Problem statement
The project progress slider should top out at each resident's goal value (e.g., 20 clients, 5K MRR) instead of a fixed 100%.

## Option A: Store goal + absolute progress values per project
**Pros**
- Slider value matches real-world units directly.
- Clear, consistent meaning across UI, API, and storage.
- Future-proof for reporting and calculations.

**Cons**
- Requires schema change and data handling for existing percent values.
- More UI fields and validation needed (goal + unit + progress).

## Option B: Store goal per project but keep progress as percent under the hood
**Pros**
- Minimal backend changes; existing percent progress data stays valid.
- UI can show goal-based slider while API remains stable.
- Easier rollout with backward compatibility defaults.

**Cons**
- UI and storage use different units, which can be confusing.
- Percent rounding may feel imprecise for small goals.

## Option C: Infer goal from the objective text
**Pros**
- No schema changes or new fields.
- Leverages already-entered resident goals.

**Cons**
- Parsing is brittle and ambiguous (multiple numbers, units, formats).
- Hard to validate or correct reliably.

## Recommendation
Option B: add a structured goal field per project and map the slider to that value in the UI while keeping percent progress stored. It best balances user intent with minimal disruption and preserves existing progress data.
