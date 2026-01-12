const state = {
  projectId: null,
  questionTimer: null,
};

const projectSelect = document.getElementById("project-select");
const progressFill = document.getElementById("progress-fill");
const progressPercent = document.getElementById("progress-percent");
const emptyState = document.getElementById("empty-state");
const questionsInput = document.getElementById("questions-input");
const addButtons = document.querySelectorAll(".add-button");

const sectionLabels = {
  summary: "summary item",
  challenges: "challenge",
  opportunities: "opportunity",
  milestones: "milestone",
};

function setInteractivity(enabled) {
  addButtons.forEach((button) => {
    button.disabled = !enabled;
  });
  questionsInput.disabled = !enabled;
}

async function requestJSON(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

async function loadProjects() {
  const data = await requestJSON("/api/projects");
  data.projects.forEach((project) => {
    const option = document.createElement("option");
    option.value = project.id;
    option.textContent = project.name;
    projectSelect.append(option);
  });
}

function renderSections(sections) {
  document.querySelectorAll(".section-list").forEach((list) => {
    const section = list.dataset.section;
    list.innerHTML = "";
    const items = sections[section] || [];
    items.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item.text;
      list.append(li);
    });
  });
}

function renderProject(project) {
  progressFill.style.width = `${project.progress}%`;
  progressPercent.textContent = `${project.progress}%`;
  questionsInput.value = project.questions || "";
  renderSections(project.sections || {});
}

async function loadProject(projectId) {
  const data = await requestJSON(`/api/projects/${projectId}`);
  renderProject(data);
}

async function handleAddItem(section) {
  if (!state.projectId) {
    return;
  }
  const label = sectionLabels[section] || "item";
  const text = window.prompt(`Add ${label}`);
  if (!text) {
    return;
  }
  await requestJSON(`/api/projects/${state.projectId}/items`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ section, text }),
  });
  await loadProject(state.projectId);
}

function scheduleQuestionsSave() {
  if (!state.projectId) {
    return;
  }
  if (state.questionTimer) {
    window.clearTimeout(state.questionTimer);
  }
  state.questionTimer = window.setTimeout(async () => {
    await requestJSON(`/api/projects/${state.projectId}/questions`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ questions: questionsInput.value }),
    });
  }, 500);
}

projectSelect.addEventListener("change", async (event) => {
  const selected = event.target.value;
  if (!selected) {
    state.projectId = null;
    emptyState.hidden = false;
    setInteractivity(false);
    progressFill.style.width = "0%";
    progressPercent.textContent = "0%";
    renderSections({});
    questionsInput.value = "";
    return;
  }

  state.projectId = Number(selected);
  emptyState.hidden = true;
  setInteractivity(true);
  await loadProject(state.projectId);
});

addButtons.forEach((button) => {
  button.addEventListener("click", () => handleAddItem(button.dataset.section));
});

questionsInput.addEventListener("input", scheduleQuestionsSave);

setInteractivity(false);
loadProjects().catch((error) => {
  console.error(error);
});
