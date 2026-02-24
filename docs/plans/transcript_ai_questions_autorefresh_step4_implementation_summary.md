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
