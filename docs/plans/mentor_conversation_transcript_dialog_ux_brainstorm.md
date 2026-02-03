# Transcript Dialog UX Brainstorm

## Goals
- Reduce visual noise and perceived complexity.
- Reduce clicks across three entry paths: paste text, record audio, upload audio.
- Keep the review/apply flow clear and safe.
- Preserve existing capabilities: paste transcript, record, upload file, transcribe, review suggestions.

## Key observations
- The dialog currently shows all input modes at once, which increases scanning cost.
- Record/upload sections are large and compete with the primary task (getting a transcript).
- Transcription actions are separated from analysis actions, adding extra steps.

## Proposed structural changes (reduce busy look)
- Use a single "Get transcript" section with three compact entry methods:
  - Paste text (default visible)
  - Record audio (collapsed by default)
  - Upload file (collapsed by default)
- Turn record/upload into expandable cards or segmented tabs so only one mode is open at a time.
- Use a single status line for the active mode (not one per block) to reduce repeated hints.
- Move "Analyze transcript" next to the transcript text field and auto-enable it when text exists.
- Collapse the "Suggested updates" section until analysis returns.

## Click reduction by scenario

### 1) Paste transcript
Current: click dialog open -> paste -> click analyze -> review -> click apply.
Proposed:
- Auto-enable and auto-run analysis on paste (with a small delay) when transcript length exceeds a threshold.
- Provide a single "Analyze now" button only if auto-analyze is disabled or transcript is short.
Result: remove the explicit analyze click for most cases.

### 2) Record audio
Current: click start -> click stop -> click upload recording -> wait -> click analyze.
Proposed:
- Auto-upload immediately after stop (no separate "Upload recording" click).
- On successful transcription, auto-insert text and auto-run analysis.
- Keep a single "Stop" button during recording and a "Record again" link after completion.
Result: removes upload + analyze clicks.

### 3) Upload audio file
Current: click choose file -> click upload file -> wait -> click analyze.
Proposed:
- Auto-upload immediately on file selection.
- On successful transcription, auto-insert text and auto-run analysis.
- Add a small "Change file" link rather than a full button row.
Result: removes upload + analyze clicks.

## Streamlined flow proposal (single pipeline)
1. User selects a transcript input mode (paste / record / upload).
2. Transcript text is produced (paste or transcription).
3. Analysis auto-runs unless the user toggles "Analyze automatically" off.
4. Suggestions appear; user applies selected updates.

## Suggested UI layout (wireframe-level)
- Header: title + resident name + close button.
- Section: "Transcript" with textarea and inline status line.
  - Right side action: "Analyze" button (only shown if auto-analyze off).
  - Below textarea: toggle "Analyze automatically" (default on).
- Section: "Add transcript" with three compact tabs/cards:
  - Paste (selected by default, minimal UI)
  - Record (collapsed; small recorder controls only when open)
  - Upload (collapsed; file picker only when open)
- Section: "Suggested updates" appears only after analysis.

## Interaction details to reduce clicks
- Auto-analyze on paste/insert if transcript length >= N characters.
- Auto-insert transcript and auto-analyze after transcription.
- Disable analyze when offline and show a single inline notice.
- Keep one primary CTA visible at a time (Analyze or Apply).

## Safeguards
- Provide a small "Undo analysis" or "Clear suggestions" link if auto-analyze runs unexpectedly.
- Show a one-line confirmation when transcription inserts text ("Transcript ready. Analyzing...").
- Always require explicit "Apply selected updates" to persist changes.

## Open questions
- Should we auto-analyze by default for paste, or ask once and remember preference?
- What is the ideal transcript length threshold for auto-analyze?
- Should we allow analysis retry without clearing the transcript?
