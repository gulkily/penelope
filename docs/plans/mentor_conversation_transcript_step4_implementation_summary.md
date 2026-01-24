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
