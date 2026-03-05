# Add Update Confetti Trigger - Step 1 Solution Assessment

## Problem statement
Confetti currently celebrates North Star slider increases, but it should celebrate successful update additions in the Add update workflow instead.

## Option A: Trigger on every successful item add
Pros:
- Directly maps celebration to adding new content.
- Covers both inline section adds and transcript-driven item adds.
- Keeps behavior deterministic and easy to explain.
Cons:
- Can fire multiple times during bulk update application.
- Does not celebrate non-item updates applied from the dialog.

## Option B: Trigger once after successful "Apply selected updates"
Pros:
- Matches the explicit "Add update" action users initiate.
- Produces one clear celebration per update session.
- Avoids bursty/confusing repeats during multi-change apply.
Cons:
- Inline section adds would not trigger confetti.
- Requires a clear rule for whether empty/no-op applies should celebrate.

## Option C: Trigger on any successful update mutation
Pros:
- Broad coverage across all update types.
- Simple mental model: any saved update can celebrate.
- Avoids dependence on one specific UI surface.
Cons:
- Too noisy for routine edits.
- Lowers celebration meaning because frequent updates all trigger effects.

## Recommendation
Option B: trigger once after a successful "Apply selected updates" action and remove slider-based triggering. This best matches user intent around "Add update," keeps the celebration meaningful, and avoids repeated/confusing confetti during multi-field saves.
