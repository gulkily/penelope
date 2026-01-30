# North Star Progress Confetti - Step 1 Solution Assessment

## Problem statement
Display a celebratory confetti effect when North Star progress increases so the UI acknowledges positive updates without disrupting core workflows.

## Option A: DOM/CSS confetti burst
Pros:
- No new dependencies; fits the existing vanilla JS/CSS stack.
- Easy to theme with existing styles and respect reduced-motion preferences.
- Straightforward to layer within current layout.
Cons:
- More DOM nodes; can affect performance on slower devices.
- Animation tuning can be finicky across browsers.

## Option B: Canvas overlay animation
Pros:
- Performance-friendly for many particles.
- Single overlay element keeps DOM light.
- Smooth visuals and flexible particle motion.
Cons:
- Requires custom rendering logic and cleanup handling.
- Harder to integrate with existing CSS theming.

## Option C: SVG burst animation
Pros:
- Compact, crisp visuals with scalable vectors.
- Easy to author a reusable burst motif.
- Simple lifecycle control (insert/remove).
Cons:
- Less variety in particle motion and randomness.
- Can look repetitive without multiple variants.

## Recommendation
Option A: DOM/CSS confetti burst. It keeps the stack simple and avoids new rendering complexity while still delivering a celebratory moment; performance can be kept in check by limiting particle count and duration.
