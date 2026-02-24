const usersTableBody = document.getElementById("users-table-body");
const usersEmpty = document.getElementById("users-empty");
const usersStatus = document.getElementById("users-status");

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

function renderUsers(entries) {
  if (!usersTableBody) {
    return;
  }
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
    const row = document.createElement("tr");
    const usernameCell = document.createElement("td");
    usernameCell.textContent = entry.username || `#${entry.id}`;

    const roleCell = document.createElement("td");
    roleCell.textContent = entry.is_admin ? "Admin" : "Standard";

    const createdAtCell = document.createElement("td");
    createdAtCell.textContent = formatTimestamp(entry.created_at);

    row.append(usernameCell, roleCell, createdAtCell);
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

loadUsers().catch((error) => {
  console.error(error);
  setStatus(error.message || "Failed to load users.", true);
});
