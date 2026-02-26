# Pitch to Penelope Feedback Feature Brainstorm

## Concept
"Pitch to Penelope" lets a resident submit a short pitch and receive immediate, structured coaching feedback before sharing it publicly.

## Product goal
- Help residents improve pitch quality in minutes, not days.
- Turn vague feedback into concrete revision actions.
- Build confidence by showing strengths and specific next steps.

## Primary user stories
- As a resident, I want to practice a pitch privately so that I can improve before presenting to others.
- As a resident, I want clear feedback categories so I know what to fix first.
- As a mentor, I want residents to arrive with stronger drafts so coaching sessions can focus on strategy instead of first-pass edits.

## What the experience could look like
1. User opens a "Pitch to Penelope" dialog/page.
2. User chooses input mode:
   - Paste pitch text
   - Upload audio/video and transcribe
3. User optionally sets pitch context:
   - Audience (investor, customer, team, partner)
   - Pitch type (30-second intro, 2-minute demo pitch, fundraising)
4. User clicks `Get Feedback`.
5. Penelope returns a response with:
   - Overall readiness score (simple 1-5 or percentage)
   - Category scores (clarity, problem, solution, evidence, ask)
   - "What is strong"
   - "What is missing"
   - "Rewrite this section" suggestions
6. User edits pitch and reruns feedback ("Version 2", "Version 3").

## Feedback format ideas
- Keep output skimmable first, detailed second.
- Suggested structure:
  - Summary verdict: "Promising but unclear ask."
  - Scorecard: 4-6 dimensions with short rationale.
  - Top 3 fixes: highest-impact improvements first.
  - Suggested rewrite snippets for weak lines.
  - Follow-up prompt: one question Penelope asks the resident to sharpen thinking.

## MVP scope (recommended)
- Text input first (paste pitch).
- One-click analysis returning:
  - Overall score
  - 5 category scores
  - Strengths and gaps
  - 3 concrete edit suggestions
- Manual apply only (resident copies edits intentionally).
- Save previous pitch drafts + feedback history per resident.

## Phase 2 extensions
- Audio upload/recording with transcription reuse from existing transcript pipeline.
- "Audience mode" tuning (investor vs customer feedback lens).
- Side-by-side diff showing how pitch improved across versions.
- Coach mode: "be more direct", "be more skeptical", "be more beginner-friendly."

## Reuse opportunities in current codebase
- Reuse transcript analysis pattern: propose changes first, no auto-save.
- Reuse existing structured LLM response approach and schema validation.
- Reuse dialog/status/suggestions UI patterns from transcript workflow.
- Reuse existing project/resident context model for personalization.

## Risks and mitigations
- Risk: Feedback is too generic.
  - Mitigation: require explicit context fields and enforce concrete output schema.
- Risk: Residents over-trust AI feedback.
  - Mitigation: include "AI coaching draft, not final truth" framing and encourage mentor review.
- Risk: Too much text overwhelms users.
  - Mitigation: default to Top 3 fixes with expandable detail.
- Risk: Inconsistent scoring across runs.
  - Mitigation: define fixed rubric language and calibrate prompt examples.

## Success signals
- Residents iterate at least once after first feedback.
- Median time from first draft to final pitch decreases.
- Mentors report higher first-review quality.
- Repeat usage by same resident across weeks.

## Open product questions
- Should score be numeric, letter-grade, or readiness bands?
- Should we optimize for one default pitch type first?
- Should the system generate a full rewritten pitch, or only targeted edits?
- Do we store every draft by default, or let residents opt out?
- What guardrails are needed for sensitive/confidential pitch content?

