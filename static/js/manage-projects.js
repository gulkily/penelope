const form = document.getElementById("add-project-form");
const nameInput = document.getElementById("project-name");
const tableBody = document.getElementById("project-table-body");
const sortButtons = document.querySelectorAll(".table-sort");

const state = {
  projects: [],
  sortKey: "id",
  sortDirection: "asc",
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
  const sorted = [...projects].sort(compareProjects);
  sorted.forEach((project) => {
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

async function loadProjects() {
  const data = await requestJSON("/api/projects?include_archived=1");
  state.projects = data.projects;
  renderProjects(state.projects);
  updateSortIndicators();
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
    renderProjects(state.projects);
    updateSortIndicators();
  });
});

loadProjects().catch((error) => {
  console.error(error);
});
