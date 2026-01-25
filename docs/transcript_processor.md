# Transcript Processor Overview

## Purpose
The transcript processor lets mentors paste a conversation transcript, run it
through an LLM, and apply suggested updates to the existing resident fields.
The v1 flow is intentionally conservative: it proposes updates only, and the
mentor must explicitly apply them.

## End-to-end flow
1. Mentor opens the "Paste transcript" dialog from the dashboard.
2. The transcript is sent to the backend for analysis.
3. The backend builds prompt messages that include current resident data and
   the transcript.
4. Dedalus runs an OpenAI-prefixed model with structured output enabled.
5. The response is returned as a proposal (no data is saved yet).
6. The mentor reviews, edits, and applies selected updates.
7. The client uses existing update endpoints to persist changes.

## Core components
- Prompt templates:
  - `app/prompts/transcript_system.txt`: system rules and guardrails.
  - `app/prompts/transcript_output_format.txt`: JSON output contract.
  - `app/prompts/transcript_user.txt`: resident context + transcript payload.
- Prompt builder:
  - `app/transcript_prompts.py` formats current resident fields and sections
    into a compact context string and assembles the messages list.
- LLM provider:
  - `app/llm_provider.py` calls Dedalus using `chat.completions.parse()` with
    `TranscriptUpdateProposal` as the response schema.
- API endpoint:
  - `POST /api/projects/{project_id}/transcript` in `app/api_transcript.py`.
  - Returns a `TranscriptUpdateResponse` with a proposal only.
- UI dialog + apply flow:
  - Dialog markup lives in `templates/index.html`.
  - Client logic lives in `static/js/app.js`.
  - The apply step calls existing endpoints for summary, questions, objective,
    goal, progress, and new list items.

## Data contract
The transcript analysis returns a `TranscriptUpdateProposal` with:
- `summary`, `questions`, `objective`: text or null
- `goal`: integer or null
- `progress`: integer percent (0-100) or null
- `items_to_add`: list of { section, text } for new list items

If a field is not mentioned, the model should return null and the UI will not
apply any change for that field.

## Configuration
- `DEDALUS_API_KEY`: required for the Dedalus SDK.
- `LLM_MODEL`: optional override (default: `openai/gpt-4o-mini`).

`.env` is supported via `python-dotenv` loaded in `app/main.py`.

## Safety notes
- The LLM response is advisory only; no persistence happens until a mentor
  clicks "Apply selected updates."
- The client performs basic validation for numeric fields before applying.
