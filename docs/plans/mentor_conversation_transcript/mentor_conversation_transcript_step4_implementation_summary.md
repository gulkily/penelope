## Stage 1 – Transcript update data contract
- Changes: Added transcript request/response schemas and proposal structure for field updates and new section items.
- Verification: Not run (manual check of schema shapes recommended).
- Notes: Proposal supports additions only for list items in v1.

## Stage 2 – Prompt templates + builder
- Changes: Added transcript prompt templates under `app/prompts` and a prompt builder in `app/transcript_prompts.py` to render resident context and transcripts into messages.
- Verification: Not run (manual prompt rendering check recommended).
- Notes: Prompts instruct the model to propose only additions for list items.

## Stage 3 – Dedalus LLM provider (OpenAI models)
- Changes: Added `app/llm_provider.py` to call Dedalus structured outputs with OpenAI-prefixed models and added `dedalus-labs` dependency.
- Verification: Not run (requires configured `DEDALUS_API_KEY`).
- Notes: Provider defaults to `openai/gpt-4o-mini` via `LLM_MODEL` override.

## Stage 4 – Transcript analysis endpoint
- Changes: Added `/api/projects/{project_id}/transcript` endpoint in `app/api_transcript.py` and wired router in `app/main.py`.
- Verification: Not run (requires Dedalus key and server running).
- Notes: Endpoint returns a proposal without persisting changes.

## Stage 5 – Transcript dialog + review UI
- Changes: Added a transcript modal dialog to `templates/index.html`, dialog styling in `static/css/main.css`, and review/apply workflow in `static/js/app.js`.
- Verification: Not run (manual UI check recommended).
- Notes: Dialog is disabled until a resident is selected; suggestions can be edited and selectively applied.

## Stage 6 – Apply updates via existing APIs
- Changes: Apply workflow in the dialog now posts approved updates to existing summary/questions/objective/goal/progress/item endpoints and reloads the resident data.
- Verification: Not run (manual flow needed with a live Dedalus key).
- Notes: Automated tests not added in Step 4 per process; recommend manual verification. Goal/progress inputs require explicit values.

## Stage 7 – .env support for Dedalus key
- Changes: Added `python-dotenv` dependency, loaded `.env` in `app/main.py`, and ignored `.env` in `.gitignore`.
- Verification: Not run (manual run with `.env` recommended).
- Notes: `.env` can now include `DEDALUS_API_KEY` and `LLM_MODEL`.

## Stage 8 – Recording/transcription recommendations
- Changes: Added `docs/recommendations_transcription_tools.md` with tool suggestions for in-person recording + transcription.
- Verification: Not applicable.
- Notes: Intended as a lightweight guide for mentors before using the transcript dialog.
