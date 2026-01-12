const state = {
  projectId: null,
  questionTimer: null,
  progressTimer: null,
};

const projectSelect = document.getElementById("project-select");
const progressSlider = document.getElementById("progress-slider");
const progressPercent = document.getElementById("progress-percent");
const emptyState = document.getElementById("empty-state");
const objectiveInput = document.getElementById("objective-input");
const objectiveSave = document.getElementById("objective-save");
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
  progressSlider.disabled = !enabled;
  objectiveInput.disabled = !enabled;
  objectiveSave.disabled = !enabled;
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

  if (projectSelect.value) {
    state.projectId = Number(projectSelect.value);
    emptyState.hidden = true;
    setInteractivity(true);
    await loadProject(state.projectId);
    return;
  }

  resetEmptyState();
}

function renderSections(sections) {
  document.querySelectorAll(".section-list").forEach((list) => {
    const section = list.dataset.section;
    list.innerHTML = "";
    const items = sections[section] || [];
    items.forEach((item) => {
      const li = document.createElement("li");
      li.className = "section-item";
      li.dataset.itemId = item.id;
      li.dataset.section = section;

      const actions = document.createElement("span");
      actions.className = "item-actions";

      const editButton = document.createElement("button");
      editButton.type = "button";
      editButton.className = "item-action item-action-edit";
      editButton.textContent = "Edit";
      editButton.dataset.action = "edit";

      const saveButton = document.createElement("button");
      saveButton.type = "button";
      saveButton.className = "item-action item-action-save";
      saveButton.textContent = "Save";
      saveButton.dataset.action = "save";

      const cancelButton = document.createElement("button");
      cancelButton.type = "button";
      cancelButton.className = "item-action item-action-cancel";
      cancelButton.textContent = "Cancel";
      cancelButton.dataset.action = "cancel";

      const deleteButton = document.createElement("button");
      deleteButton.type = "button";
      deleteButton.className = "item-action item-delete";
      deleteButton.textContent = "Delete";
      deleteButton.dataset.action = "delete";

      const text = document.createElement("span");
      text.className = "item-text";
      text.textContent = item.text;

      actions.append(editButton, saveButton, cancelButton, deleteButton);
      li.append(text, actions);
      list.append(li);
    });
  });
}

function resetEmptyState() {
  state.projectId = null;
  emptyState.hidden = false;
  setInteractivity(false);
  updateProgressDisplay(0);
  renderSections({});
  objectiveInput.value = "";
  questionsInput.value = "";
}

function updateProgressDisplay(value) {
  const normalized = Number(value) || 0;
  progressSlider.value = normalized;
  progressPercent.textContent = `${normalized}%`;
  progressSlider.style.setProperty("--progress", `${normalized}%`);
}

function renderProject(project) {
  updateProgressDisplay(project.progress);
  objectiveInput.value = project.objective || "";
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

function scheduleProgressSave(value) {
  if (!state.projectId) {
    return;
  }
  if (state.progressTimer) {
    window.clearTimeout(state.progressTimer);
  }
  const normalized = Number(value) || 0;
  state.progressTimer = window.setTimeout(async () => {
    await requestJSON(`/api/projects/${state.projectId}/progress`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ progress: normalized }),
    });
  }, 250);
}

async function handleObjectiveSave() {
  if (!state.projectId) {
    return;
  }
  const objective = objectiveInput.value.trim();
  await requestJSON(`/api/projects/${state.projectId}/objective`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ objective }),
  });
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
    resetEmptyState();
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

document.addEventListener("click", async (event) => {
  const button = event.target.closest(".item-action");
  if (!button) {
    return;
  }
  const listItem = button.closest(".section-item");
  if (!listItem) {
    return;
  }
  const itemId = listItem.dataset.itemId;
  if (!itemId) {
    return;
  }

  if (button.dataset.action === "delete") {
    await requestJSON(`/api/items/${itemId}`, { method: "DELETE" });
    if (state.projectId) {
      await loadProject(state.projectId);
    }
    return;
  }

  if (button.dataset.action === "edit") {
    if (listItem.classList.contains("is-editing")) {
      return;
    }
    const textNode = listItem.querySelector(".item-text");
    if (!textNode) {
      return;
    }
    const currentText = textNode.textContent || "";
    listItem.dataset.originalText = currentText;

    const input = document.createElement("input");
    input.type = "text";
    input.className = "item-input";
    input.value = currentText;
    textNode.replaceWith(input);
    listItem.classList.add("is-editing");
    input.focus();
    input.select();
    return;
  }

  if (button.dataset.action === "cancel") {
    const original = listItem.dataset.originalText || "";
    const input = listItem.querySelector(".item-input");
    if (input) {
      const text = document.createElement("span");
      text.className = "item-text";
      text.textContent = original;
      input.replaceWith(text);
    }
    listItem.classList.remove("is-editing");
    return;
  }

  if (button.dataset.action === "save") {
    const input = listItem.querySelector(".item-input");
    if (!input) {
      return;
    }
    const updated = input.value.trim();
    const original = listItem.dataset.originalText || "";
    if (!updated || updated === original.trim()) {
      listItem.classList.remove("is-editing");
      const text = document.createElement("span");
      text.className = "item-text";
      text.textContent = original;
      input.replaceWith(text);
      return;
    }
    await requestJSON(`/api/items/${itemId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: updated }),
    });
    if (state.projectId) {
      await loadProject(state.projectId);
    }
    return;
  }
});

document.addEventListener("keydown", async (event) => {
  const input = event.target.closest(".item-input");
  if (!input) {
    return;
  }
  const listItem = input.closest(".section-item");
  if (!listItem) {
    return;
  }
  if (event.key === "Enter") {
    event.preventDefault();
    const saveButton = listItem.querySelector(".item-action-save");
    if (saveButton) {
      saveButton.click();
    }
  } else if (event.key === "Escape") {
    event.preventDefault();
    const cancelButton = listItem.querySelector(".item-action-cancel");
    if (cancelButton) {
      cancelButton.click();
    }
  }
});

progressSlider.addEventListener("input", (event) => {
  const value = event.target.value;
  updateProgressDisplay(value);
  scheduleProgressSave(value);
});

objectiveSave.addEventListener("click", handleObjectiveSave);
questionsInput.addEventListener("input", scheduleQuestionsSave);

setInteractivity(false);
resetEmptyState();
loadProjects().catch((error) => {
  console.error(error);
});

window.addEventListener("pageshow", () => {
  if (!projectSelect.value) {
    resetEmptyState();
  }
});
