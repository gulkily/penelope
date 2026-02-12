## Stage 1 – Shared Navbar Include
- Changes: Added `templates/partials/navbar.html` with configurable link set, current-page hiding, lobby badge support, and optional wrapper control. Standardized “Back to dashboard” label for all non-dashboard pages.
- Verification: Not run.
- Notes: Navbar omits the current page and can render “Back to dashboard” when requested.

## Stage 2 – Page Integration
- Changes: Replaced per-page nav markup with the shared include across all templates and wired per-page context from `app/main.py`.
- Verification: Not run.
- Notes: Lobby badge script is included wherever the navbar appears; logout moved out of the navbar.

## Stage 3 – Clean-Up and Consistency
- Changes: Added a Settings “Session” card with a logout action and removed logout from other pages. Added a session reset header using the navbar include.
- Verification: Not run.
- Notes: Ledger link only appears via Settings (link button and CTA), while Lobby remains in all navbars except the lobby page itself.

## Stage 4 – Top-Level Navbar Placement
- Changes: Added a dedicated top navbar partial and moved navigation out of module headers across all pages.
- Verification: Not run.
- Notes: Navbar now sits as the first element in each page layout.
