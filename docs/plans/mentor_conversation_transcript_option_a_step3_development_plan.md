# Mentor Transcript Option A (Step 3: Development Plan)

1. Add resilient dialog status + retry states
   - Goal: Keep mentors informed during slow or failed analysis and make retries obvious.
   - Dependencies: Existing transcript dialog markup, `transcript-status`, and analyze button handlers in `static/js/app.js`.
   - Expected changes: Define status states for idle/analyzing/error/offline, update status copy, and re-enable the analyze action after failures; update `static/css/main.css` if new status styles are needed.
   - Verification: Manual: throttle network or disconnect, run analysis, confirm status messaging and retry flow are clear and functional.
   - Risks/open questions:
     - Ensure new status messaging does not conflict with recording/upload status elements.
     - Decide whether to show a distinct offline hint based on `navigator.onLine`.
   - Canonical components/APIs: Transcript dialog UI and existing analyze workflow in `static/js/app.js`.

2. Persist transcript drafts locally per resident
   - Goal: Preserve transcript input across refreshes and temporary disconnects.
   - Dependencies: Project selection state, transcript input element, and dialog open/close handlers.
   - Expected changes: Add local draft helpers keyed by project ID, save on input (with light throttling), restore on dialog open, and clear on explicit “Clear” or after a successful apply.
   - Verification: Manual: paste transcript, refresh, reopen dialog, confirm the draft returns; verify clearing removes the stored draft.
   - Risks/open questions:
     - Draft size limits in localStorage and how to handle very large transcripts.
     - Whether to keep drafts after successful apply or always clear them.
   - Canonical components/APIs: Transcript dialog UI and client state in `static/js/app.js`.

3. Harden the analysis request for low-bandwidth conditions
   - Goal: Minimize redundant network work and keep the UI responsive during slow requests.
   - Dependencies: `requestJSON` helper and existing `/api/projects/{project_id}/transcript` call.
   - Expected changes: Ensure the request payload stays minimal (transcript only), guard against duplicate submissions while busy, and add a soft timeout/abort with user-facing retry guidance.
   - Verification: Manual: throttle network, run analysis, confirm only one request is sent and the dialog recovers cleanly after timeout.
   - Risks/open questions:
     - Best timeout threshold that avoids premature aborts on high-latency networks.
   - Canonical components/APIs: Transcript analysis endpoint and client request layer.
