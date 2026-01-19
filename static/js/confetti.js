(() => {
  const DEFAULT_CONFIG = {
    layerId: "confetti-layer",
    pieceCount: 24,
    durationMs: 1200,
    cooldownMs: 900,
    colors: [
      "var(--accent)",
      "var(--accent-strong)",
      "var(--link)",
      "var(--danger)",
      "#f5b62f",
    ],
  };

  let config = { ...DEFAULT_CONFIG };
  let layer = null;
  let prefersReducedMotion = false;
  let lastTriggerAt = 0;
  let cleanupTimer = null;
  let motionMedia = null;

  function handleMotionChange(event) {
    prefersReducedMotion = event.matches;
  }

  function initConfetti(options = {}) {
    config = { ...DEFAULT_CONFIG, ...options };
    layer = document.getElementById(config.layerId);

    if (cleanupTimer) {
      window.clearTimeout(cleanupTimer);
      cleanupTimer = null;
    }

    if (layer) {
      layer.innerHTML = "";
    }

    motionMedia = window.matchMedia("(prefers-reduced-motion: reduce)");
    prefersReducedMotion = motionMedia.matches;

    if (motionMedia.addEventListener) {
      motionMedia.addEventListener("change", handleMotionChange);
    } else if (motionMedia.addListener) {
      motionMedia.addListener(handleMotionChange);
    }
  }

  function buildPiece(index) {
    const piece = document.createElement("span");
    piece.className = "confetti-piece";

    const left = 10 + Math.random() * 80;
    const width = 4 + Math.random() * 4;
    const height = width + 4 + Math.random() * 6;
    const drop = 110 + Math.random() * 90;
    const delay = Math.random() * 180;
    const rotate = Math.floor(Math.random() * 360);
    const color = config.colors[index % config.colors.length];

    piece.style.setProperty("--confetti-left", `${left.toFixed(1)}%`);
    piece.style.setProperty("--confetti-width", `${width.toFixed(1)}px`);
    piece.style.setProperty("--confetti-height", `${height.toFixed(1)}px`);
    piece.style.setProperty("--confetti-drop", `${drop.toFixed(1)}px`);
    piece.style.setProperty("--confetti-delay", `${Math.round(delay)}ms`);
    piece.style.setProperty("--confetti-rotate", `${rotate}deg`);
    piece.style.setProperty("--confetti-color", color);
    piece.style.setProperty("--confetti-duration", `${config.durationMs}ms`);

    return piece;
  }

  function triggerConfetti() {
    if (!layer || prefersReducedMotion) {
      return;
    }

    const now = Date.now();
    if (now - lastTriggerAt < config.cooldownMs) {
      return;
    }
    lastTriggerAt = now;

    if (cleanupTimer) {
      window.clearTimeout(cleanupTimer);
      cleanupTimer = null;
    }

    layer.innerHTML = "";
    const fragment = document.createDocumentFragment();
    for (let i = 0; i < config.pieceCount; i += 1) {
      fragment.appendChild(buildPiece(i));
    }
    layer.appendChild(fragment);

    cleanupTimer = window.setTimeout(() => {
      if (layer) {
        layer.innerHTML = "";
      }
    }, config.durationMs + 240);
  }

  window.NorthStarConfetti = {
    initConfetti,
    triggerConfetti,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => initConfetti());
  } else {
    initConfetti();
  }
})();
