const usersTableBody = document.getElementById("users-table-body");
const usersEmpty = document.getElementById("users-empty");
const usersStatus = document.getElementById("users-status");

const DEFAULT_HOUSE = "Unassigned";
let houseOptions = [DEFAULT_HOUSE];

const usersById = new Map();

function setStatus(message, isError = false) {
  if (!usersStatus) {
    return;
  }
  usersStatus.textContent = message;
  usersStatus.classList.toggle("status-error", isError);
}

function formatTimestamp(value) {
  if (!value) {
    return "";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString();
}

function parseError(payload, fallback) {
  if (payload && payload.detail) {
    return payload.detail;
  }
  return fallback;
}

function normalizeHouse(value) {
  const candidate = String(value || "").trim().toLowerCase();
  const match = houseOptions.find((option) => option.toLowerCase() === candidate);
  return match || houseOptions[0] || DEFAULT_HOUSE;
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

async function loadHouseOptions() {
  const response = await fetch("/api/houses");
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(parseError(payload, "Failed to load house options."));
  }
  setHouseOptions(payload.houses);
}

function createHouseSelect(entry) {
  const select = document.createElement("select");
  select.className = "field-input";
  houseOptions.forEach((option) => {
    const optionNode = document.createElement("option");
    optionNode.value = option;
    optionNode.textContent = option;
    select.append(optionNode);
  });
  select.value = normalizeHouse(entry.house);
  select.addEventListener("change", () => {
    updateUserHouse(entry.id, select).catch((error) => {
      console.error(error);
      setStatus("Failed to update user house.", true);
    });
  });
  return select;
}

async function updateUserHouse(accountId, select) {
  const entry = usersById.get(accountId);
  if (!entry) {
    return;
  }
  const previousHouse = normalizeHouse(entry.house);
  const nextHouse = normalizeHouse(select.value);
  if (nextHouse === previousHouse) {
    return;
  }

  select.disabled = true;
  setStatus(`Updating house for ${entry.username || `#${entry.id}`}...`);
  try {
    const response = await fetch(`/api/auth/users/${encodeURIComponent(accountId)}/house`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ house: nextHouse }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(parseError(payload, "Failed to update user house."));
    }
    entry.house = normalizeHouse(payload.house);
    usersById.set(accountId, entry);
    select.value = entry.house;
    setStatus(`Updated house for ${entry.username || `#${entry.id}`} to ${entry.house}.`);
  } catch (error) {
    select.value = previousHouse;
    setStatus(error.message || "Failed to update user house.", true);
  } finally {
    select.disabled = false;
  }
}

function renderUsers(entries) {
  if (!usersTableBody) {
    return;
  }
  usersById.clear();
  usersTableBody.innerHTML = "";
  if (!entries.length) {
    if (usersEmpty) {
      usersEmpty.hidden = false;
    }
    return;
  }
  if (usersEmpty) {
    usersEmpty.hidden = true;
  }

  entries.forEach((entry) => {
    usersById.set(entry.id, entry);

    const row = document.createElement("tr");
    const usernameCell = document.createElement("td");
    usernameCell.textContent = entry.username || `#${entry.id}`;

    const roleCell = document.createElement("td");
    roleCell.textContent = entry.is_admin ? "Admin" : "Standard";

    const houseCell = document.createElement("td");
    houseCell.append(createHouseSelect(entry));

    const createdAtCell = document.createElement("td");
    createdAtCell.textContent = formatTimestamp(entry.created_at);

    row.append(usernameCell, roleCell, houseCell, createdAtCell);
    usersTableBody.append(row);
  });
}

async function loadUsers() {
  setStatus("Loading users...");
  const response = await fetch("/api/auth/users?limit=500");
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    renderUsers([]);
    throw new Error(parseError(payload, "Failed to load users."));
  }
  const entries = payload.entries || [];
  renderUsers(entries);
  setStatus(`Showing ${entries.length} of ${payload.total ?? entries.length} users.`);
}

(async () => {
  try {
    await loadHouseOptions();
    await loadUsers();
  } catch (error) {
    console.error(error);
    setStatus(error.message || "Failed to load users.", true);
  }
})();
