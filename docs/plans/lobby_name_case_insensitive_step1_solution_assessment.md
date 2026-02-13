# Lobby Name Case-Insensitive Login — Step 1 Solution Assessment

## Problem Statement
Lobby login should treat usernames case-insensitively when matching or linking identities, without breaking existing display names.

## Option A — Client-Side Comparison Only
- Pros:
  - Minimal change, no backend or data changes.
  - Preserves display casing exactly as entered.
- Cons:
  - Only affects the UI; any server-side matching remains case-sensitive.
  - Easy to miss other comparison points as the feature grows.

## Option B — Normalize for Comparisons in App Logic (No Schema Change)
- Pros:
  - Consistent case-insensitive behavior in both UI and API decisions.
  - Avoids database migrations and preserves original display casing.
- Cons:
  - Requires careful updates wherever comparisons occur.
  - Slightly more code paths to test.

## Option C — Store Normalized Username Field
- Pros:
  - Single canonical value for case-insensitive matching.
  - Simplifies future queries and reporting.
- Cons:
  - Requires schema changes and migration handling.
  - More surface area to keep in sync when names change.

## Recommendation
Option B. It delivers consistent case-insensitive behavior without a schema change and keeps display names intact. This aligns with the preference to avoid migrations while still covering both UI and server-side matching logic.
