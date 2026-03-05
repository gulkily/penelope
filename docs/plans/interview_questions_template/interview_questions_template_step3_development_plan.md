# Interview Questions Template — Step 3 Development Plan

Database changes: none.

1. Stage 1 - Transcribe screenshot questions into the canonical text template
   - Goal: Convert `screenshot/questions_from_architect_for_review.jpeg` into a maintainable text template file that becomes the source of truth.
   - Dependencies: Approved Step 2 scope; access to the screenshot artifact.
   - Expected changes:
     - Add template file at `static/templates/interview_questions_template.md`.
     - Preserve section grouping and prompt wording from the screenshot, with clean headings and bullet/number formatting for fast live scanning.
   - Verification approach: Manual side-by-side check of screenshot vs template content, section order, and completeness.
   - Risks/open questions:
     - Some phrasing may be ambiguous from image quality; decide whether to keep exact wording or lightly normalize for readability.
   - Canonical components/API contracts touched: `screenshot/questions_from_architect_for_review.jpeg`, `static/templates/interview_questions_template.md`.

2. Stage 2 - Add interview guide UI affordance inside the existing Add Update workflow
   - Goal: Make the question guide reachable without leaving the transcript/recording flow.
   - Dependencies: Stage 1 template file.
   - Expected changes:
     - Extend `templates/index.html` transcript dialog with an `Interview Guide` open/close control and a read-only content container.
     - Reuse existing dialog layout patterns so the new guide does not create a separate page.
   - Verification approach: Manual smoke test that the guide can be opened/closed from the `Add update` dialog on desktop and mobile widths.
   - Risks/open questions:
     - Decide whether guide should appear inline, collapsible, or as a secondary panel for best small-screen usability.
   - Canonical components/API contracts touched: `templates/index.html`, transcript dialog UX contract in `static/js/app.js`.

3. Stage 3 - Wire template loading, rendering, and failure handling in client logic
   - Goal: Load and display the canonical template text reliably during interviews.
   - Dependencies: Stages 1-2.
   - Expected changes:
     - Add client fetch/render flow in `static/js/app.js` for `/static/templates/interview_questions_template.md`.
     - Planned signatures:
       - `async function loadInterviewQuestionsTemplate(): Promise<string>`
       - `function renderInterviewQuestionsTemplate(content: string): void`
       - `function setInterviewGuideStatus(message: string, isError?: boolean): void`
     - Cache loaded template for the current page session to avoid repeated network calls.
   - Verification approach: Manual test for first-load success, reopen behavior (no re-fetch needed), and missing-file/error fallback message.
   - Risks/open questions:
     - Markdown rendering approach (plain text `<pre>` vs lightweight parser) should be chosen for readability without adding new frontend dependencies.
   - Canonical components/API contracts touched: `static/js/app.js`, static asset path contract `/static/templates/interview_questions_template.md`.

4. Stage 4 - Ensure coexistence with recording/upload/analyze interactions
   - Goal: Prevent the new guide from breaking existing interview capture behavior.
   - Dependencies: Stage 3.
   - Expected changes:
     - Adjust transcript dialog state handling so guide open/close does not interfere with recording, upload, draft restore, or analyze flows.
     - Keep existing transcript controls and status messaging intact.
   - Verification approach: Manual end-to-end dialog walkthrough: open guide, start/stop recording, upload audio, analyze transcript, apply suggestions.
   - Risks/open questions:
     - Focus management and keyboard navigation may need explicit handling to keep dialog accessibility predictable.
   - Canonical components/API contracts touched: `static/js/app.js`, `templates/index.html`.

5. Stage 5 - Add regression coverage and operator documentation
   - Goal: Lock in behavior and make the template workflow discoverable for future updates.
   - Dependencies: Stages 1-4.
   - Expected changes:
     - Add focused UI test coverage for guide visibility and load/fallback behavior (within existing e2e test structure).
     - Update user-facing docs to describe where the canonical template file lives and how to edit it.
   - Verification approach: Run focused test command(s) against a running server and perform one doc-following smoke pass.
   - Risks/open questions:
     - Existing UI tests may not yet cover transcript dialog internals; add minimal stable assertions to avoid flaky selectors.
   - Canonical components/API contracts touched: `tests/e2e/`, `README.md` or `docs/` hosting guidance.
