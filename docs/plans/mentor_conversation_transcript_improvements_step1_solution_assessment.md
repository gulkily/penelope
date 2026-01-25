# Mentor Transcript Improvements (Step 1: Solution Assessment)

## Problem statement
Transcript analysis should only surface relevant, evidence-based updates and show clearer context in the review dialog to prevent accidental changes.

## Option A: Prompt-only tightening
**Pros**
- Fastest change (prompt updates only).
- No backend or UI logic changes.

**Cons**
- Relies on model compliance; may still suggest unrelated fields.
- Limited ability to enforce evidence or suppress unchanged values.

## Option B: Prompt + client-side filtering
**Pros**
- Adds guardrails by dropping suggestions that are unchanged or lack evidence.
- Small UI changes can add resident context and units/percent clarity.

**Cons**
- More logic in the client; potential duplication with backend rules.
- Filtering may hide legitimate suggestions if rules are too strict.

## Option C: Structured evidence + server validation
**Pros**
- Strongest reliability: model must provide evidence snippets.
- Server can reject unsupported updates before the UI sees them.

**Cons**
- Requires schema changes and more backend logic.
- Higher effort; more risk of edge cases in v1.

## Recommendation
Option B: tighten prompts and add client-side filtering plus UI context improvements now, while keeping the path open to Option C if false positives persist.
