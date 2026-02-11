const LOBBY_POLL_INTERVAL_MS = 15000;

function updateLobbyIndicators(count) {
  const indicators = document.querySelectorAll("[data-lobby-count]");
  indicators.forEach((indicator) => {
    if (count > 0) {
      indicator.textContent = String(count);
      indicator.hidden = false;
    } else {
      indicator.textContent = "";
      indicator.hidden = true;
    }
  });
}

async function fetchLobbyCount() {
  try {
    const response = await fetch("/api/auth/lobby", { credentials: "same-origin" });
    if (!response.ok) {
      updateLobbyIndicators(0);
      return;
    }
    const data = await response.json();
    const count = Array.isArray(data.entries) ? data.entries.length : 0;
    updateLobbyIndicators(count);
  } catch (error) {
    updateLobbyIndicators(0);
  }
}

fetchLobbyCount();
setInterval(fetchLobbyCount, LOBBY_POLL_INTERVAL_MS);
