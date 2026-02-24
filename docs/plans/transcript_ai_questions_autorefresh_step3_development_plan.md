# Transcript AI Questions Auto-Refresh - Step 3 Development Plan

1. Stage 1 - Add AI Questions generation service
   - Goal: Create a dedicated backend capability that generates fresh mentor follow-up questions from current resident context.
   - Dependencies: Existing LLM provider and resident context retrieval.
   - Expected changes: Add a small service module plus prompt asset for profitability/success-oriented follow-up questions; keep output as plain Questions field text.
   - Planned function signature reference: `async generate_ai_questions(project: dict) -> str`.
   - Verification approach: Manual API-level call path review and local smoke run confirming non-empty text output for a valid resident context.
   - Risks or open questions:
     - Prompt quality may require quick iteration for consistent usefulness.
     - Need deterministic fallback when LLM returns empty/invalid output.
   - Canonical components/API contracts touched: Reuse existing `questions` field and LLM provider contract; no schema changes.

2. Stage 2 - Add background regeneration orchestration + status contract
   - Goal: Support Option B by running Questions regeneration after transcript apply returns.
   - Dependencies: Stage 1 generation service.
   - Expected changes: Add start/status backend contract for question regeneration and a lightweight in-process job tracker for queued/in-progress/completed/failed states.
   - Planned signature reference:
     - `start_questions_regeneration(project_id: int) -> QuestionsRegenerationStartResponse`
     - `get_questions_regeneration_status(project_id: int, job_id: str) -> QuestionsRegenerationStatusResponse`
   - Verification approach: Manual endpoint checks that status transitions are observable and completed jobs persist refreshed Questions.
   - Risks or open questions:
     - In-memory job tracking is process-local; restart behavior should degrade safely.
     - Overlapping jobs for one resident need a clear coalescing/cancel rule.
   - Canonical components/API contracts touched: New transcript-adjacent backend API surface; existing `PUT /projects/{id}/questions` persistence path remains canonical for stored data.

3. Stage 3 - Hook transcript apply to auto-start Questions regeneration
   - Goal: Ensure transcript-driven updates automatically trigger Questions refresh without architect approval.
   - Dependencies: Stage 2 status/start contract, existing transcript apply flow.
   - Expected changes: Extend transcript apply success path to trigger regeneration start after core updates succeed; stop depending on transcript Questions suggestion selection for this flow.
   - Planned signature reference: `startQuestionsRegeneration(projectId: number): Promise<{ job_id: string }>` (frontend API helper).
   - Verification approach: Manual flow check that `Apply selected updates` still closes promptly and always starts Questions regeneration when transcript updates succeed.
   - Risks or open questions:
     - Must avoid blocking dialog close on long-running generation.
     - Clarify whether transcript proposal still renders a Questions suggestion card (recommended: hide/remove to avoid conflicting UX).
   - Canonical components/API contracts touched: Reuse `Apply selected updates` flow and transcript apply orchestration; no DB changes.

4. Stage 4 - Add Questions field regeneration progress UX
   - Goal: Make regeneration state visible in the Questions field until refresh completes.
   - Dependencies: Stage 3 trigger + Stage 2 status contract.
   - Expected changes: Extend dashboard Questions UI state with regenerating/success/error status and polling lifecycle; hydrate refreshed Questions when job completes while preserving admin manual edit capability.
   - Planned signature reference:
     - `setQuestionsRegenerationState(state: "idle" | "regenerating" | "error")`
     - `pollQuestionsRegeneration(projectId: number, jobId: string): Promise<void>`
   - Verification approach: Manual UI smoke test showing visible in-progress state, successful replacement, and non-blocking error fallback.
   - Risks or open questions:
     - Polling cadence must balance responsiveness and request volume.
     - Need guardrails so resident switching cancels stale polling updates.
   - Canonical components/API contracts touched: Existing Questions field rendering/editing surface and project reload flow.

5. Stage 5 - Regression coverage and operator checks
   - Goal: Protect the new background flow from regressions.
   - Dependencies: Stages 1-4.
   - Expected changes: Add focused tests for transcript apply kickoff, job status transitions, successful Questions replacement, and failure fallback preserving existing text.
   - Verification approach: Run focused HTTP + e2e tests plus manual spot checks for admin edit behavior after AI refresh.
   - Risks or open questions:
     - Async timing can make tests flaky; keep assertions state-based rather than delay-based.
   - Canonical components/API contracts touched: Existing transcript/apply tests and Questions persistence APIs.
