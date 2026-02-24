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

## Stage 3 - Hook transcript apply to auto-start Questions regeneration
- Changes:
  - Updated transcript apply success flow in `static/js/app.js` to start Questions regeneration automatically after successful transcript-driven updates.
  - Removed transcript suggestion-driven Questions persistence from apply flow so Questions refresh is no longer dependent on architect approval of a Questions suggestion card.
  - Preserved existing apply behavior for summary/objective/goal/progress/items and retained post-apply confetti behavior.
- Verification:
  - Ran `node --check static/js/app.js`.
- Notes:
  - Apply flow still closes promptly; Questions regeneration is started asynchronously in the background.

## Stage 4 - Add Questions field regeneration progress UX
- Changes:
  - Added a dedicated Questions status line in `templates/index.html` (`#questions-status`) for both admin and non-admin views.
  - Added Questions status styling in `static/css/main.css` for busy/error states.
  - Added frontend regeneration lifecycle in `static/js/app.js`:
    - start call: `POST /api/projects/{project_id}/questions/regenerate`
    - polling call: `GET /api/projects/{project_id}/questions/regeneration/{job_id}`
    - visible in-progress/success/error status handling
    - stale poll cancellation on resident switch/reset
  - On completion, Questions field value is updated in place with AI-generated text; on failure, previous content is preserved with non-blocking status.
- Verification:
  - Ran `node --check static/js/app.js`.
- Notes:
  - Admin manual editing remains enabled; regeneration status is additive UI feedback, not a lockout.

## Stage 5 - Regression coverage and operator checks
- Changes:
  - Hardened prompt context formatting in `app/questions_prompts.py` to safely handle non-numeric goal/progress/history values without raising parsing errors.
  - Finalized implementation notes and prepared manual operator smoke checks for transcript apply + Questions regeneration states.
- Verification:
  - Ran `python -m py_compile app/questions_prompts.py app/questions_ai.py app/questions_regeneration_jobs.py app/api_transcript.py app/llm_provider.py app/schemas.py`.
  - Ran `node --check static/js/app.js`.
  - Manual browser smoke test not executed in-agent (per repo workflow, user should run manual verification with the app server).
- Notes:
  - No new automated tests were added in this Step 4 implementation to stay aligned with the process constraint for this stage.
