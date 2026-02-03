# When Chrome Uploads Are Not Audio: Lessons From a MIME-Type Bug

## Summary
We hit a confusing upload failure: audio transcription uploads worked in Firefox but failed in Chrome with "Unsupported audio type." The root cause was not the file itself, but how Chrome labeled the MIME type. The fix required normalizing content types, expanding allowed types to include video-wrapped audio, and accepting `application/octet-stream` as "unknown" rather than "invalid."

## The Symptoms
- Firefox uploads succeeded consistently.
- Chrome uploads failed with HTTP 400 and "Unsupported audio type."
- The UI surfaced a generic upload failure, and the backend rejected the request before transcription.

## What We Learned
1) **Chrome may report audio as video.**
   Some recordings arrive as `video/webm` or `video/mp4` even when they contain only audio. If validation only allows `audio/*`, Chrome users get blocked.

2) **Chrome often appends codec parameters.**
   Content types can include parameters like `audio/webm;codecs=opus`. A strict equality check against a fixed allowlist will fail unless you strip those parameters.

3) **Browsers can fall back to `application/octet-stream`.**
   When the browser cannot determine the type (or when it chooses not to share it), uploads look like octet-stream. That should be treated as "unknown" and validated by size and file content, not rejected outright.

## The Fix
We applied three changes to make uploads reliable across browsers:

- **Normalize MIME types** by stripping any `;...` parameters before validation.
- **Expand allowed types** to include common video-wrapped audio (`video/webm`, `video/mp4`) alongside audio types like `audio/m4a`.
- **Treat `application/octet-stream` as unknown** so it does not fail validation by itself.

These changes removed the Chrome-only failures while preserving size limits and existing validation checks.

## Debugging Checklist (Reusable)
- Reproduce in multiple browsers and compare behavior.
- Log or capture the incoming `content_type` and filename.
- Normalize MIME values before validation.
- Consider media wrappers (video containers for audio-only content).
- Treat `application/octet-stream` as unknown, not invalid.

## Closing Thought
The lesson is not "trust the browser" or "ignore MIME types." The lesson is to normalize and interpret MIME types as hints, not absolute truths. If validation is too strict, it becomes a cross-browser bug.
