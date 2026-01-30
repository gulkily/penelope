# Mentor Conversation Transcript (Step 2: Feature Description)

## Problem
Mentors need to paste a conversation transcript that an LLM can use alongside existing resident data to update progress without disrupting the mentoring flow. The updates must land in the current dashboard fields so progress tracking stays consistent.

## User stories
- As a mentor, I want to paste a transcript and get suggested updates so that I do not have to rewrite the conversation into multiple fields.
- As a mentor, I want to review and edit suggested changes before saving so that the resident record stays accurate.
- As a program lead, I want transcript-driven updates to use the existing resident fields so that reporting remains consistent.

## Core requirements
- Provide a way to paste a transcript for the currently selected resident.
- Use an LLM to propose updates based on the transcript and existing resident data.
- Allow mentors to accept, reject, or edit the proposed updates before saving.
- Save updates into the existing resident fields and lists (no parallel data store in v1).
- Support partial updates when the transcript only mentions some fields.

## Shared component inventory
- Resident selector + dashboard context: reuse as the canonical way to scope updates to the active resident.
- Resident summary textarea: reuse for the final summary update.
- Questions textarea: reuse for open questions/risks updates.
- North Star objective input: reuse for objective updates.
- North Star goal + progress slider + progress graph: reuse for goal/progress updates and immediate visualization.
- Summary/Challenges/Opportunities/Milestones lists: reuse existing list sections for new or updated items.
- Existing resident data APIs (fetch + update endpoints): reuse to load current context and persist approved changes.
- Transcript input and review surface: new UI area is required to capture the transcript and show suggested updates.

## Simple user flow
1. Mentor selects a resident on the dashboard.
2. Mentor pastes the transcript into the transcript input.
3. The system analyzes the transcript with current resident data and presents suggested updates.
4. Mentor reviews, edits, and confirms the updates.
5. The dashboard reflects the updated fields and lists.

## Success criteria
- A mentor can paste a transcript and apply updates without leaving the dashboard.
- Approved updates appear in the existing fields and persist on page reload.
- Transcripts that do not mention a field result in no change to that field.
