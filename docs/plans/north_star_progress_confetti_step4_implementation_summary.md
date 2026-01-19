## Stage 1 – Confetti module scaffold
- Changes: Added `static/js/confetti.js` with a small init + trigger API, reduced-motion detection, and cooldown-controlled bursts.
- Verification: Not run (needs manual browser load to confirm module initializes without console errors).
- Notes: Uses a global `window.NorthStarConfetti` to integrate with existing non-module scripts.

## Stage 2 – Visual layer + styling
- Changes: Added a confetti layer container in `templates/index.html`, loaded `static/js/confetti.js`, and introduced confetti styles/animation in `static/css/main.css`.
- Verification: Not run (needs manual browser load to confirm visuals render and do not block the slider).
- Notes: Confetti layer uses `pointer-events: none` and sits above the progress slider.
