# Test Suite Updates for Transcript + Transcription (Step 1: Solution Assessment)

## Problem statement
The new transcript analysis, goal/progress heuristics, and audio transcription flows have no automated coverage, leaving regressions likely in critical paths.

## Option A: Minimal HTTP tests only
**Pros**
- Fastest to implement.
- Covers API contracts and basic validation.

**Cons**
- Does not cover dialog UI behavior or end-to-end flows.
- Risk of UI regressions remains high.

## Option B: HTTP tests + targeted E2E smoke
**Pros**
- Verifies API behavior and key UI flows (dialog open, upload, apply).
- Balanced effort vs coverage.

**Cons**
- Requires test data setup and mocking external calls.
- Slightly longer to implement.

## Option C: Full E2E flows + API mocks
**Pros**
- Highest confidence; validates user journeys end-to-end.
- Catches UI/JS regressions and backend validation issues.

**Cons**
- Highest time investment and maintenance cost.
- More brittle without robust fixtures.

## What’s missing today
- HTTP coverage for `/api/projects/{id}/transcript` (LLM proposal handling, goal inference, units-based progress).
- HTTP coverage for `/api/transcriptions` (file validation, success response, error handling).
- E2E flow for “Add update” dialog: open/close, analyze, review, apply updates.
- E2E flow for recording/upload UI: record controls, file upload, status handling.

## Recommendation
Option B: add HTTP tests for both endpoints and a small set of E2E smoke tests for the dialog and upload flow to catch regressions without overbuilding.
