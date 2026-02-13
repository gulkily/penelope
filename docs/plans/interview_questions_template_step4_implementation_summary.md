## Stage 1 - Transcribe screenshot questions into the canonical text template
- Changes:
  - Added `static/templates/interview_questions_template.md` as the canonical text template.
  - Transcribed prompts from `screenshot/questions_from_architect_for_review.jpeg` into sectioned markdown for live readability.
- Verification:
  - Performed a manual side-by-side content check against `screenshot/questions_from_architect_for_review.jpeg` to confirm section coverage and prompt order.
- Notes:
  - Kept the source wording intact from the screenshot to avoid semantic drift.

## Stage 2 - Add interview guide UI affordance inside the existing Add Update workflow
- Changes:
  - Extended `templates/index.html` transcript dialog with an `Interview guide` section, show/hide toggle button, status line, and read-only content container.
  - Added supporting styles in `static/css/main.css` for guide layout and readability within the existing dialog visual language.
- Verification:
  - Reviewed the dialog markup and CSS integration to confirm the new section stays within the existing `Add update` workflow structure and remains hidden by default.
- Notes:
  - Kept this stage to structure/styling only; loading behavior is implemented in Stage 3.
