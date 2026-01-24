# Mentor Conversation Transcript (Step 3: Development Plan)

1. Define transcript update data contract
   - Goal: Specify the request/response shape for LLM-driven updates that map to existing resident fields.
   - Dependencies: Approved Step 2; current project schema in `app/db_projects.py`.
   - Expected changes: Add Pydantic models (e.g., `TranscriptUpdateRequest`, `TranscriptUpdateProposal`, `TranscriptUpdateResponse`) that cover summary, questions, objective, goal, progress, and section item additions/edits; no DB changes.
   - Planned signatures: `def propose_transcript_updates(project: dict, transcript: str) -> TranscriptUpdateProposal` (service-level contract).
   - Verification: Manual validation of JSON payloads against the new schemas.
   - Risks/open questions: Do we allow list item edits/removals or only additions in v1?
   - Canonical components/APIs: Existing project data fields and sections from `/api/projects/{project_id}`.

2. Add prompt templates and prompt builder
   - Goal: Store system/user prompt content in separate template files that include resident context and output instructions.
   - Dependencies: Stage 1 schema.
   - Expected changes: New template files (e.g., `app/prompts/transcript_system.txt`, `app/prompts/transcript_user.txt`, `app/prompts/transcript_output_format.txt`) plus a loader that formats existing resident data + transcript into messages.
   - Planned signatures: `def build_transcript_messages(project: dict, transcript: str) -> list[dict]`.
   - Verification: Manual check that rendered prompts include current data and required output format.
   - Risks/open questions: Prompt injection protections and how to sanitize/limit transcript size.
   - Canonical components/APIs: Existing resident fields and section names used as prompt context.

3. Implement LLM provider abstraction (Dedalus + OpenAI models only for v1)
   - Goal: Add a single LLM interface that calls Dedalus Labs with OpenAI-prefixed models, while keeping the surface extensible for future direct OpenAI/Anthropic integrations.
   - Dependencies: Stage 1 schema, Stage 2 prompts, Dedalus Labs docs (available in `~/whiteballoon/docs/dedalus`).
   - Expected changes: New service module (e.g., `app/llm_provider.py`) that selects model via env (`LLM_MODEL`, `DEDALUS_API_KEY`) and returns structured output via Dedalus; leave placeholders for alternative providers without wiring them yet; update `requirements.txt` with `dedalus-labs`.
   - Planned signatures: `def run_transcript_llm(messages: list[dict]) -> TranscriptUpdateProposal`.
   - Verification: Manual call using a configured Dedalus key to ensure a schema-valid response.
   - Risks/open questions: Default OpenAI model alias, retry/backoff policy, and behavior when Dedalus is unavailable.
   - Canonical components/APIs: LLM output must align with the transcript update schema.

4. Add transcript analysis API endpoint
   - Goal: Provide a backend endpoint that returns proposed updates for a pasted transcript.
   - Dependencies: Stages 1-3.
   - Expected changes: New route `POST /api/projects/{project_id}/transcript` that loads the project, builds prompts, calls the LLM provider, and returns `TranscriptUpdateResponse` without persisting data.
   - Planned signatures: `def analyze_transcript(project_id: int, payload: TranscriptUpdateRequest) -> TranscriptUpdateResponse`.
   - Verification: Manual POST with sample transcript; confirm response lists only mentioned field updates.
   - Risks/open questions: Error messaging when LLM call fails; response time expectations.
   - Canonical components/APIs: `db.get_project`, existing `/api/projects/{project_id}` data contract.

5. Build transcript dialog + review workflow
   - Goal: Let mentors launch a hidden modal dialog to paste transcripts, view suggestions, and edit before applying.
   - Dependencies: Stage 4 endpoint.
   - Expected changes: Add a “Paste transcript” trigger and hidden dialog element in `templates/index.html` (native `<dialog>` preferred), UI styles in `static/css/main.css`, and client logic in `static/js/app.js` (or a dedicated module) to open/close the dialog, call the transcript endpoint, and render suggested updates with accept/edit controls.
   - Verification: Manual smoke test: open dialog, paste transcript, see suggestions, edit fields, confirm no changes applied until approval.
   - Risks/open questions: Dialog accessibility/focus management; how to visually compare existing vs suggested values without clutter.
   - Canonical components/APIs: Reuse existing dashboard fields and list sections for final edits.

6. Apply approved updates + tests
   - Goal: Persist accepted changes into existing fields and list sections.
   - Dependencies: Stage 5 UI; existing update endpoints.
   - Expected changes: Client-side apply flow that calls existing APIs (`/summary`, `/questions`, `/objective`, `/goal`, `/progress`, `/items`) based on accepted suggestions; add HTTP tests with a mock LLM provider for `/api/projects/{project_id}/transcript` and apply flow.
   - Verification: Manual: approve a subset of updates and verify persistence after reload; automated: `pytest tests/http` for transcript endpoint with mock provider.
   - Risks/open questions: Do we need a bulk-apply endpoint for atomic updates, or is sequential updates acceptable in v1?
   - Canonical components/APIs: Existing update endpoints for resident fields and items.
