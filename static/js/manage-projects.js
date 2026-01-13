const form = document.getElementById("add-project-form");
const nameInput = document.getElementById("project-name");
const tableBody = document.getElementById("project-table-body");
const sortButtons = document.querySelectorAll(".table-sort");
const paginationPrev = document.getElementById("pagination-prev");
const paginationNext = document.getElementById("pagination-next");
const paginationStatus = document.getElementById("pagination-status");

const PAGE_SIZE = 100;
const DEFAULT_SORT_KEY = "id";
const DEFAULT_SORT_DIRECTION = "asc";
const SORT_KEYS = new Set(["id", "name", "archived"]);
const SORT_DIRECTIONS = new Set(["asc", "desc"]);

const state = {
  projects: [],
  sortKey: DEFAULT_SORT_KEY,
  sortDirection: DEFAULT_SORT_DIRECTION,
  page: 1,
  pageSize: PAGE_SIZE,
  total: 0,
  sortMode: "client",
};

async function requestJSON(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

function renderProjects(projects) {
  tableBody.innerHTML = "";
  const rows =
    state.sortMode === "client" ? [...projects].sort(compareProjects) : projects;
  rows.forEach((project) => {
    const row = document.createElement("tr");
    row.className = project.archived ? "is-archived" : "";

    const idCell = document.createElement("td");
    idCell.textContent = String(project.id);

    const nameCell = document.createElement("td");
    const link = document.createElement("a");
    link.href = `/?project=${project.id}`;
    link.textContent = project.name;
    link.className = "project-link";
    nameCell.append(link);

    const archiveCell = document.createElement("td");
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = project.archived;
    checkbox.dataset.projectId = project.id;
    checkbox.addEventListener("change", handleArchiveToggle);
    archiveCell.append(checkbox);

    row.append(idCell, nameCell, archiveCell);
    tableBody.append(row);
  });
}

function updatePaginationControls(totalPages) {
  const pages = totalPages ?? Math.max(1, Math.ceil(state.total / state.pageSize));
  if (paginationPrev) {
    paginationPrev.disabled = state.page <= 1;
  }
  if (paginationNext) {
    paginationNext.disabled = state.page >= pages;
  }
  if (paginationStatus) {
    paginationStatus.textContent = `Page ${state.page} of ${pages} · ${state.total} total`;
  }
}

function compareProjects(a, b) {
  const key = state.sortKey;
  let left = a[key];
  let right = b[key];
  if (key === "name") {
    left = String(left || "").toLowerCase();
    right = String(right || "").toLowerCase();
  }
  if (key === "archived") {
    left = left ? 1 : 0;
    right = right ? 1 : 0;
  }
  if (left < right) {
    return state.sortDirection === "asc" ? -1 : 1;
  }
  if (left > right) {
    return state.sortDirection === "asc" ? 1 : -1;
  }
  return 0;
}

function updateSortIndicators() {
  sortButtons.forEach((button) => {
    const key = button.dataset.sort;
    if (!key) {
      return;
    }
    const header = button.closest("th");
    const indicator = button.querySelector(".table-sort-indicator");
    if (key === state.sortKey) {
      if (indicator) {
        indicator.textContent = state.sortDirection === "asc" ? "↑" : "↓";
      }
      if (header) {
        header.setAttribute(
          "aria-sort",
          state.sortDirection === "asc" ? "ascending" : "descending"
        );
      }
    } else {
      if (indicator) {
        indicator.textContent = "";
      }
      if (header) {
        header.setAttribute("aria-sort", "none");
      }
    }
  });
}

function readStateFromUrl() {
  const params = new URLSearchParams(window.location.search);
  const pageParam = Number.parseInt(params.get("page"), 10);
  state.page = Number.isInteger(pageParam) && pageParam > 0 ? pageParam : 1;

  const sortKey = params.get("sort_key");
  state.sortKey = SORT_KEYS.has(sortKey) ? sortKey : DEFAULT_SORT_KEY;

  const sortDir = params.get("sort_dir");
  state.sortDirection = SORT_DIRECTIONS.has(sortDir)
    ? sortDir
    : DEFAULT_SORT_DIRECTION;
}

function syncUrl(replace = true) {
  const url = new URL(window.location.href);
  url.searchParams.set("page", String(state.page));
  url.searchParams.set("sort_key", state.sortKey);
  url.searchParams.set("sort_dir", state.sortDirection);
  if (replace) {
    window.history.replaceState({}, "", url);
  } else {
    window.history.pushState({}, "", url);
  }
}

async function loadProjects() {
  const params = new URLSearchParams({ include_archived: "1" });
  params.set("page", String(state.page));
  if (state.sortMode === "server") {
    params.set("sort_key", state.sortKey);
    params.set("sort_dir", state.sortDirection);
  }
  const data = await requestJSON(`/api/projects?${params.toString()}`);
  const total = Number.isFinite(data.total) ? data.total : data.projects.length;
  const pageSize = data.page_size || PAGE_SIZE;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  if (total > pageSize && state.sortMode !== "server") {
    state.sortMode = "server";
    return loadProjects();
  }

  if (total <= pageSize && state.sortMode !== "client") {
    state.sortMode = "client";
  }

  if (state.page > totalPages && totalPages > 0) {
    state.page = totalPages;
    return loadProjects();
  }

  state.projects = data.projects;
  state.total = total;
  state.page = data.page || state.page;
  state.pageSize = pageSize;
  renderProjects(state.projects);
  updateSortIndicators();
  updatePaginationControls(totalPages);
  syncUrl(true);
}

async function handleArchiveToggle(event) {
  const checkbox = event.target;
  const projectId = checkbox.dataset.projectId;
  if (!projectId) {
    return;
  }
  checkbox.disabled = true;
  try {
    await requestJSON(`/api/projects/${projectId}/archive`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ archived: checkbox.checked }),
    });
    await loadProjects();
  } catch (error) {
    console.error(error);
    checkbox.checked = !checkbox.checked;
  } finally {
    checkbox.disabled = false;
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const name = nameInput.value.trim();
  if (!name) {
    return;
  }
  form.querySelector("button").disabled = true;
  try {
    await requestJSON("/api/projects", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });
    nameInput.value = "";
    await loadProjects();
  } catch (error) {
    console.error(error);
  } finally {
    form.querySelector("button").disabled = false;
  }
});

sortButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const key = button.dataset.sort;
    if (!key) {
      return;
    }
    if (state.sortKey === key) {
      state.sortDirection = state.sortDirection === "asc" ? "desc" : "asc";
    } else {
      state.sortKey = key;
      state.sortDirection = "asc";
    }
    updateSortIndicators();
    if (state.sortMode === "server") {
      state.page = 1;
      syncUrl(false);
      loadProjects().catch((error) => {
        console.error(error);
      });
    } else {
      renderProjects(state.projects);
      updatePaginationControls();
      syncUrl(false);
    }
  });
});

if (paginationPrev) {
  paginationPrev.addEventListener("click", () => {
    if (state.page > 1) {
      state.page -= 1;
      syncUrl(false);
      loadProjects().catch((error) => {
        console.error(error);
      });
    }
  });
}

if (paginationNext) {
  paginationNext.addEventListener("click", () => {
    const totalPages = Math.max(1, Math.ceil(state.total / state.pageSize));
    if (state.page < totalPages) {
      state.page += 1;
      syncUrl(false);
      loadProjects().catch((error) => {
        console.error(error);
      });
    }
  });
}

window.addEventListener("popstate", () => {
  readStateFromUrl();
  loadProjects().catch((error) => {
    console.error(error);
  });
});

readStateFromUrl();
loadProjects().catch((error) => {
  console.error(error);
});
