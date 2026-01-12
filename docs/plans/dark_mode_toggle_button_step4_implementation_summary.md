## Stage 1 – Replace selector with floating toggle
- Changes: Removed the theme selector from headers and added a shared floating toggle button to both templates.
- Verification: Manual smoke test suggested (load both pages and confirm the toggle appears in the corner; not run here).
- Notes: None.

## Stage 2 – Wire toggle behavior
- Changes: Updated theme logic to drive a floating toggle button that cycles theme preferences and updates its label/aria text.
- Verification: Manual smoke test suggested (click the toggle to cycle themes and reload to confirm persistence; not run here).
- Notes: The toggle cycles System → Dark → Light.
