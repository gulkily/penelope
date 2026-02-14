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

## Stage 3 - Wire template loading, rendering, and failure handling in client logic
- Changes:
  - Added interview guide state/elements and handlers in `static/js/app.js`.
  - Implemented:
    - `loadInterviewQuestionsTemplate()`
    - `renderInterviewQuestionsTemplate(content)`
    - `setInterviewGuideStatus(message, isError)`
  - Added session-level caching so the template is fetched once and reused on subsequent guide opens.
  - Added non-blocking load failure behavior that keeps interview recording workflows usable.
  - Follow-up: switched guide rendering from plain text to Markdown-derived HTML (headings, paragraphs, and lists) using a lightweight in-app renderer.
- Verification:
  - Ran `node --check static/js/app.js` to validate JavaScript syntax after the new guide logic was added.
- Notes:
  - The guide currently renders markdown as readable plain text (`<pre>`), avoiding new frontend dependencies.

## Stage 4 - Ensure coexistence with recording/upload/analyze interactions
- Changes:
  - Added `resetInterviewGuidePanel()` in `static/js/app.js` to consistently collapse/reset guide UI state without touching transcript/recording data.
  - Integrated guide resets into transcript dialog open/reset flows so closing/reopening the dialog starts from a predictable guide state.
  - Updated guide toggle behavior to restore neutral status messaging when the panel is closed.
- Verification:
  - Ran `node --check static/js/app.js` after state-flow changes.
  - Performed code-path review for `openTranscriptDialog()`, `resetTranscriptDialog()`, and recording/upload/analyze handlers to confirm no control wiring was removed.
- Notes:
  - The guide remains independent from transcript draft/recording/upload state and does not block those actions.

## Stage 5 - Add operator documentation
- Changes:
  - Updated `README.md` notes with the canonical interview template path:
    - `static/templates/interview_questions_template.md`
  - Documented the operator workflow for updating prompts (edit template file; reload page to consume updates).
- Verification:
  - Reviewed `README.md` references for path accuracy and alignment with implemented static asset loading.
- Notes:
  - Automated regression tests were intentionally not added in this step to align with the Step 4 process constraint to rely on manual smoke verification during implementation.
