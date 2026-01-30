## Stage 1 – Resilient status + retry messaging
- Changes: Added transcript status states (busy/offline/error), online/offline status updates, and dialog-close abort handling to keep the UI responsive on slow connections.
- Verification: Not run (manual: open transcript dialog, toggle offline/online, confirm status messaging and retry guidance).
- Notes: None.

## Stage 2 – Local transcript draft persistence
- Changes: Added local draft save/restore keyed by resident, save on input/upload, restore on dialog open, and clear on explicit clear/apply.
- Verification: Not run (manual: paste transcript, refresh, reopen dialog, confirm draft restoration; clear and confirm removal).
- Notes: Drafts depend on browser storage limits.

## Stage 3 – Analysis timeout + request hardening
- Changes: Added analysis timeout/abort handling, guarded duplicate submissions, and improved failure messaging for slow or dropped connections.
- Verification: Not run (manual: throttle network and confirm timeout messaging and retry path).
- Notes: Timeout set to 45 seconds.
