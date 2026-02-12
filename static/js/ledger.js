const ledgerBody = document.getElementById("ledger-table-body");
const emptyState = document.getElementById("ledger-empty");

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

function formatActor(entry) {
  return entry.actor_username || entry.actor_account_id || "—";
}

function formatSubject(entry) {
  return entry.subject_username || entry.subject_account_id || "—";
}

function formatDetails(entry) {
  const metadata = entry.metadata || {};
  if (metadata.username) {
    return metadata.username;
  }
  if (metadata.request_id) {
    return `Request ${metadata.request_id}`;
  }
  if (metadata.raw) {
    return metadata.raw;
  }
  const keys = Object.keys(metadata);
  if (!keys.length) {
    return "";
  }
  return keys
    .map((key) => `${key}: ${metadata[key]}`)
    .join(" · ");
}

function renderRows(entries) {
  ledgerBody.innerHTML = "";
  if (!entries.length) {
    emptyState.hidden = false;
    return;
  }
  emptyState.hidden = true;

  entries.forEach((entry) => {
    const row = document.createElement("tr");
    const timeCell = document.createElement("td");
    timeCell.textContent = formatTimestamp(entry.created_at);

    const actionCell = document.createElement("td");
    actionCell.textContent = entry.event_type;

    const actorCell = document.createElement("td");
    actorCell.textContent = formatActor(entry);

    const subjectCell = document.createElement("td");
    subjectCell.textContent = formatSubject(entry);

    const detailCell = document.createElement("td");
    detailCell.textContent = formatDetails(entry);

    row.append(timeCell, actionCell, actorCell, subjectCell, detailCell);
    ledgerBody.append(row);
  });
}

async function loadLedger() {
  const response = await fetch("/api/auth/ledger?limit=200");
  if (!response.ok) {
    emptyState.hidden = false;
    emptyState.textContent = "Unable to load ledger.";
    return;
  }
  const data = await response.json();
  renderRows(data.entries || []);
}

loadLedger();
