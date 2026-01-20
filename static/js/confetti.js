(() => {
  const DEFAULT_CONFIG = {
    layerId: "confetti-layer",
    pieceCount: 360,
    durationMs: 7000,
    cooldownMs: 900,
    delaySpreadMs: 1800,
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

  function resolveLayer() {
    if (!layer) {
      layer = document.getElementById(config.layerId);
    }
    return layer;
  }

  function updateMotionPreference() {
    if (!motionMedia) {
      motionMedia = window.matchMedia("(prefers-reduced-motion: reduce)");
    }
    prefersReducedMotion = motionMedia.matches;
    return prefersReducedMotion;
  }

  function buildPiece(index, dropRange) {
    const piece = document.createElement("span");
    piece.className = "confetti-piece";

    const left = 10 + Math.random() * 80;
    const width = 4 + Math.random() * 4;
    const height = width + 4 + Math.random() * 6;
    const drop =
      dropRange.min + Math.random() * (dropRange.max - dropRange.min);
    const delaySpread = Number(config.delaySpreadMs);
    const delayRange = Number.isFinite(delaySpread) ? Math.max(0, delaySpread) : 0;
    const delay = Math.random() * delayRange;
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

  function triggerConfetti(options = {}) {
    const targetLayer = resolveLayer();
    const reduceMotion = updateMotionPreference();
    if (!targetLayer || (reduceMotion && !options.force)) {
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

    targetLayer.innerHTML = "";
    const rect = targetLayer.getBoundingClientRect();
    const layerHeight = rect.height || window.innerHeight || 0;
    const minDrop = Math.max(180, layerHeight * 0.85);
    const maxDrop = Math.max(minDrop + 80, layerHeight * 1.1);
    const dropRange = { min: minDrop, max: maxDrop };

    const fragment = document.createDocumentFragment();
    for (let i = 0; i < config.pieceCount; i += 1) {
      fragment.appendChild(buildPiece(i, dropRange));
    }
    targetLayer.appendChild(fragment);

    cleanupTimer = window.setTimeout(() => {
      if (targetLayer) {
        targetLayer.innerHTML = "";
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
