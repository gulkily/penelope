const debugIds = {
  ready: "debug-ready",
  motion: "debug-motion",
  layer: "debug-layer",
  layerSize: "debug-layer-size",
  module: "debug-module",
  trigger: "debug-trigger",
  pieceCount: "debug-piece-count",
};

function setDebugText(id, value) {
  const node = document.getElementById(id);
  if (node) {
    node.textContent = value;
  }
}

function boolLabel(value) {
  return value ? "true" : "false";
}

function readDiagnostics() {
  const layer = document.getElementById("confetti-layer");
  const module = window.NorthStarConfetti;
  const hasModule = Boolean(module);
  const hasTrigger = Boolean(module && typeof module.triggerConfetti === "function");
  const pieceCount = document.querySelectorAll(".confetti-piece").length;
  const motionMatch = window.matchMedia("(prefers-reduced-motion: reduce)");

  setDebugText(debugIds.ready, document.readyState);
  setDebugText(debugIds.motion, boolLabel(motionMatch.matches));
  setDebugText(
    debugIds.layer,
    layer ? `present (connected: ${boolLabel(layer.isConnected)})` : "missing"
  );

  if (layer) {
    const rect = layer.getBoundingClientRect();
    setDebugText(
      debugIds.layerSize,
      `${Math.round(rect.width)} x ${Math.round(rect.height)}`
    );
  } else {
    setDebugText(debugIds.layerSize, "n/a");
  }

  setDebugText(debugIds.module, hasModule ? "available" : "missing");
  setDebugText(debugIds.trigger, boolLabel(hasTrigger));
  setDebugText(debugIds.pieceCount, String(pieceCount));
}

function wireDebugControls() {
  const triggerButton = document.getElementById("trigger-confetti");
  const forceButton = document.getElementById("trigger-confetti-force");
  const refreshButton = document.getElementById("refresh-debug");

  if (triggerButton) {
    triggerButton.addEventListener("click", () => {
      const confetti = window.NorthStarConfetti;
      if (confetti && typeof confetti.triggerConfetti === "function") {
        confetti.triggerConfetti();
      }
      window.setTimeout(readDiagnostics, 60);
    });
  }

  if (forceButton) {
    forceButton.addEventListener("click", () => {
      const confetti = window.NorthStarConfetti;
      if (confetti && typeof confetti.triggerConfetti === "function") {
        confetti.triggerConfetti({ force: true });
      }
      window.setTimeout(readDiagnostics, 60);
    });
  }

  if (refreshButton) {
    refreshButton.addEventListener("click", readDiagnostics);
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    wireDebugControls();
    readDiagnostics();
  });
} else {
  wireDebugControls();
  readDiagnostics();
}
