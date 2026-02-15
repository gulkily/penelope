# Interview Guide UI Improvements Checklist

## 1. Split View (Desktop) + Drawer (Mobile)
- [x] Define responsive breakpoints and interaction rules (desktop split pane, mobile drawer).
- [x] Update transcript dialog markup to include a resizable/split guide container on desktop.
- [x] Add mobile drawer toggle/open/close controls and close-on-backdrop behavior.
- [x] Add CSS layout rules for desktop split + mobile drawer states.
- [x] Verify guide remains readable and transcript controls remain accessible at common viewport sizes.

## 2. Section Checklist + Progress Count
- [x] Parse guide sections/questions into renderable checklist items.
- [x] Add per-question checkbox UI in the rendered guide.
- [x] Add progress indicator (e.g., `3/9 asked`) that updates live.
- [x] Ensure checklist toggles do not modify the underlying template file.
- [ ] Verify toggling works while recording/uploading/analyzing.

## 3. Accessibility Polish
- [x] Audit focus order for open/close guide, drawer controls, and checklist controls.
- [x] Add keyboard shortcuts (e.g., toggle guide) with conflict-safe handling.
- [x] Add/confirm ARIA live updates for load and error messages.
- [x] Ensure touch targets and contrast meet accessibility expectations.
- [ ] Run a manual keyboard-only walkthrough of the full interview flow.

## 4. Regression Coverage + Docs
- [x] Add focused E2E checks for guide visibility and checklist updates.
- [x] Add/update docs for interviewer usage and operator-maintained template workflow.
- [x] Add concise release note in the Step 4 summary after implementation is complete.
