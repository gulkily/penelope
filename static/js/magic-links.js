const magicUsernameInput = document.getElementById("magic-link-username");
const magicGenerateButton = document.getElementById("magic-link-generate");
const magicCopyButton = document.getElementById("magic-link-copy");
const magicLinkTableBody = document.getElementById("magic-link-table-body");
const magicStatus = document.getElementById("magic-link-status");

let latestMagicLink = "";

function setMagicStatus(message, isError = false) {
  if (!magicStatus) {
    return;
  }
  magicStatus.textContent = message;
  magicStatus.classList.toggle("status-error", isError);
}

function parseError(payload, fallback) {
  if (payload && payload.detail) {
    return payload.detail;
  }
  return fallback;
}

function formatTimestamp(raw) {
  const date = new Date(raw);
  if (Number.isNaN(date.getTime())) {
    return raw;
  }
  return date.toLocaleString();
}

function shortToken(tokenId) {
  if (!tokenId) {
    return "";
  }
  return tokenId.slice(0, 8);
}

function syncMagicControls() {
  if (magicCopyButton) {
    magicCopyButton.disabled = !latestMagicLink;
  }
}

function renderActiveMagicLinks(entries) {
  if (!magicLinkTableBody) {
    return;
  }
  magicLinkTableBody.innerHTML = "";
  if (!entries.length) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 5;
    cell.className = "hint";
    cell.textContent = "No active links.";
    row.appendChild(cell);
    magicLinkTableBody.appendChild(row);
    return;
  }

  entries.forEach((entry) => {
    const row = document.createElement("tr");
    const usernameCell = document.createElement("td");
    usernameCell.textContent = entry.configured_username;
    const tokenCell = document.createElement("td");
    tokenCell.className = "mono";
    tokenCell.textContent = shortToken(entry.token_id);
    const issuedByCell = document.createElement("td");
    issuedByCell.textContent = entry.created_by_username || `#${entry.created_by_account_id}`;
    const createdAtCell = document.createElement("td");
    createdAtCell.textContent = formatTimestamp(entry.created_at);
    const actionsCell = document.createElement("td");

    const revokeButton = document.createElement("button");
    revokeButton.type = "button";
    revokeButton.className = "link-button danger";
    revokeButton.textContent = "Revoke";
    revokeButton.addEventListener("click", () => {
      revokeMagicLink(entry.token_id).catch((error) => {
        console.error(error);
        setMagicStatus("Failed to revoke magic link.", true);
      });
    });
    actionsCell.appendChild(revokeButton);

    row.appendChild(usernameCell);
    row.appendChild(tokenCell);
    row.appendChild(issuedByCell);
    row.appendChild(createdAtCell);
    row.appendChild(actionsCell);
    magicLinkTableBody.appendChild(row);
  });
}

async function loadActiveMagicLinks() {
  if (!magicLinkTableBody) {
    return;
  }
  const response = await fetch("/api/auth/magic-links");
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    if (response.status === 403) {
      renderActiveMagicLinks([]);
      setMagicStatus("Admin access required to view active links.", true);
      return;
    }
    throw new Error(parseError(payload, "Failed to load active magic links."));
  }
  renderActiveMagicLinks(payload.entries || []);
}

async function generateMagicLink() {
  if (!magicUsernameInput || !magicGenerateButton) {
    return;
  }
  const configuredUsername = magicUsernameInput.value.trim();
  if (!configuredUsername) {
    setMagicStatus("Enter a configured username.", true);
    return;
  }

  magicGenerateButton.disabled = true;
  setMagicStatus("Generating magic link...");
  try {
    const response = await fetch("/api/auth/magic-links", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ configured_username: configuredUsername }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(parseError(payload, "Failed to generate magic link."));
    }

    latestMagicLink = payload.magic_link || "";
    syncMagicControls();
    await loadActiveMagicLinks();
    setMagicStatus(`Link created for ${payload.configured_username}.`);
  } catch (error) {
    setMagicStatus(error.message || "Failed to generate magic link.", true);
  } finally {
    magicGenerateButton.disabled = false;
  }
}

async function copyMagicLink() {
  if (!latestMagicLink) {
    return;
  }
  try {
    await navigator.clipboard.writeText(latestMagicLink);
    setMagicStatus("Magic link copied.");
  } catch (error) {
    console.error(error);
    setMagicStatus("Copy failed. Generate a new link and try again.", true);
  }
}

async function revokeMagicLink(tokenId) {
  const response = await fetch(
    `/api/auth/magic-links/${encodeURIComponent(tokenId)}/revoke`,
    {
      method: "POST",
    }
  );
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(parseError(payload, "Failed to revoke magic link."));
  }
  await loadActiveMagicLinks();
  setMagicStatus("Magic link revoked.");
}

if (magicGenerateButton) {
  magicGenerateButton.addEventListener("click", () => {
    generateMagicLink().catch((error) => {
      console.error(error);
      setMagicStatus("Failed to generate magic link.", true);
    });
  });
}

if (magicCopyButton) {
  magicCopyButton.addEventListener("click", () => {
    copyMagicLink().catch((error) => {
      console.error(error);
      setMagicStatus("Copy failed.", true);
    });
  });
}

if (magicUsernameInput) {
  magicUsernameInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      if (magicGenerateButton) {
        magicGenerateButton.click();
      }
    }
  });
}

syncMagicControls();
loadActiveMagicLinks().catch((error) => {
  console.error(error);
  setMagicStatus(error.message || "Failed to load active magic links.", true);
});
