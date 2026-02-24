const magicUsernameInput = document.getElementById("magic-link-username");
const magicHouseSelect = document.getElementById("magic-link-house");
const magicGenerateButton = document.getElementById("magic-link-generate");
const magicCopyButton = document.getElementById("magic-link-copy");
const magicLinkTableBody = document.getElementById("magic-link-table-body");
const magicStatus = document.getElementById("magic-link-status");

const DEFAULT_HOUSE = "Unassigned";
let houseOptions = [DEFAULT_HOUSE];

let latestMagicLink = "";
let usersByUsername = new Map();

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

function normalizeUsername(value) {
  return String(value || "").trim().toLowerCase();
}

function setHouseOptions(options) {
  const unique = [];
  const seen = new Set();
  (options || []).forEach((option) => {
    const candidate = String(option || "").trim();
    if (!candidate) {
      return;
    }
    const key = candidate.toLowerCase();
    if (seen.has(key)) {
      return;
    }
    seen.add(key);
    unique.push(candidate);
  });
  houseOptions = unique.length ? unique : [DEFAULT_HOUSE];
}

function normalizeHouse(value) {
  const candidate = String(value || "").trim().toLowerCase();
  const match = houseOptions.find((option) => option.toLowerCase() === candidate);
  return match || houseOptions[0] || DEFAULT_HOUSE;
}

function renderHouseSelectOptions(selectedValue) {
  if (!magicHouseSelect) {
    return;
  }
  const normalizedSelection = normalizeHouse(selectedValue);
  magicHouseSelect.innerHTML = "";
  houseOptions.forEach((option) => {
    const optionNode = document.createElement("option");
    optionNode.value = option;
    optionNode.textContent = option;
    magicHouseSelect.append(optionNode);
  });
  magicHouseSelect.value = normalizedSelection;
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

async function loadHouseOptions() {
  const response = await fetch("/api/houses");
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(parseError(payload, "Failed to load house options."));
  }
  setHouseOptions(payload.houses);
  renderHouseSelectOptions(magicHouseSelect ? magicHouseSelect.value : undefined);
}

async function loadUserHouses() {
  usersByUsername = new Map();
  const response = await fetch("/api/auth/users?limit=500");
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(parseError(payload, "Failed to load users for house prefill."));
  }
  (payload.entries || []).forEach((entry) => {
    const key = normalizeUsername(entry.username);
    if (!key || usersByUsername.has(key)) {
      return;
    }
    usersByUsername.set(key, normalizeHouse(entry.house));
  });
}

function prefillHouseForExistingUser() {
  if (!magicUsernameInput || !magicHouseSelect) {
    return;
  }
  const key = normalizeUsername(magicUsernameInput.value);
  if (!key) {
    return;
  }
  const existingHouse = usersByUsername.get(key);
  if (existingHouse) {
    magicHouseSelect.value = normalizeHouse(existingHouse);
  }
}

async function generateMagicLink() {
  if (!magicUsernameInput || !magicGenerateButton || !magicHouseSelect) {
    return;
  }
  const configuredUsername = magicUsernameInput.value.trim();
  if (!configuredUsername) {
    setMagicStatus("Enter a configured username.", true);
    return;
  }

  const assignedHouse = normalizeHouse(magicHouseSelect.value);

  magicGenerateButton.disabled = true;
  setMagicStatus("Generating magic link...");
  try {
    const response = await fetch("/api/auth/magic-links", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        configured_username: configuredUsername,
        house: assignedHouse,
      }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(parseError(payload, "Failed to generate magic link."));
    }

    latestMagicLink = payload.magic_link || "";
    syncMagicControls();
    await Promise.all([loadActiveMagicLinks(), loadUserHouses()]);

    if (payload.account_created) {
      setMagicStatus(
        `Created account for ${payload.configured_username} in ${payload.assigned_house} and issued link.`,
      );
    } else {
      setMagicStatus(
        `Issued link for ${payload.configured_username} and set house to ${payload.assigned_house}.`,
      );
    }
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
    },
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
  magicUsernameInput.addEventListener("change", () => {
    prefillHouseForExistingUser();
  });
  magicUsernameInput.addEventListener("blur", () => {
    prefillHouseForExistingUser();
  });
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
(async () => {
  try {
    await loadHouseOptions();
    await Promise.all([loadActiveMagicLinks(), loadUserHouses()]);
  } catch (error) {
    console.error(error);
    setMagicStatus(error.message || "Failed to initialize magic links page.", true);
  }
})();
