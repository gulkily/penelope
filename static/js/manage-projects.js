const form = document.getElementById("add-project-form");
const nameInput = document.getElementById("project-name");
const tableBody = document.getElementById("project-table-body");

async function requestJSON(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

function renderProjects(projects) {
  tableBody.innerHTML = "";
  projects.forEach((project) => {
    const row = document.createElement("tr");
    row.className = project.archived ? "is-archived" : "";

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

    row.append(nameCell, archiveCell);
    tableBody.append(row);
  });
}

async function loadProjects() {
  const data = await requestJSON("/api/projects?include_archived=1");
  renderProjects(data.projects);
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

loadProjects().catch((error) => {
  console.error(error);
});
