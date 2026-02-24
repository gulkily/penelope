# Transcript AI Questions Auto-Refresh - Step 4 Implementation Summary

## Stage 1 - Add AI Questions generation service
- Changes:
  - Added dedicated AI Questions prompt files at:
    - `app/prompts/questions_regeneration_system.txt`
    - `app/prompts/questions_regeneration_output_format.txt`
    - `app/prompts/questions_regeneration_user.txt`
  - Added `app/questions_prompts.py` to assemble resident context + history into prompt messages.
  - Added `app/questions_ai.py` with `generate_ai_questions(project_id)` service logic.
  - Extended `app/llm_provider.py` with `run_questions_llm(messages)`.
  - Added regeneration response/proposal models in `app/schemas.py`.
- Verification:
  - Ran `python -m py_compile app/questions_prompts.py app/questions_ai.py app/llm_provider.py app/schemas.py`.
- Notes:
  - Prompt assets are now stored as text files under `app/prompts/`, consistent with existing transcript prompt patterns.

## Stage 2 - Add background regeneration orchestration + status contract
- Changes:
  - Added in-process job orchestration module `app/questions_regeneration_jobs.py` with:
    - queued/running/completed/failed states
    - per-resident active-job coalescing
    - bounded in-memory job retention cleanup
  - Added transcript-adjacent API endpoints in `app/api_transcript.py`:
    - `POST /api/projects/{project_id}/questions/regenerate`
    - `GET /api/projects/{project_id}/questions/regeneration/{job_id}`
  - Reused the existing persisted Questions field update path once generation completes.
- Verification:
  - Pending full runtime verification in later stages; syntax and integration checks run after endpoint wiring.
- Notes:
  - Job state is process-local by design and intended for lightweight background execution.
