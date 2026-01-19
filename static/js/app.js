const DEFAULT_GOAL = 100;

const state = {
  projectId: null,
  questionTimer: null,
  summaryTimer: null,
  progressTimer: null,
  objectiveTimer: null,
  goalTimer: null,
  projectsLoaded: false,
  progressPercent: 0,
  goalValue: DEFAULT_GOAL,
};

const projectSelect = document.getElementById("project-select");
const progressSlider = document.getElementById("progress-slider");
const progressPercent = document.getElementById("progress-percent");
const emptyState = document.getElementById("empty-state");
const summaryInput = document.getElementById("summary-input");
const objectiveInput = document.getElementById("objective-input");
const goalInput = document.getElementById("goal-input");
const questionsInput = document.getElementById("questions-input");
const inlineAddButtons = document.querySelectorAll(".inline-add-button");
const inlineAddInputs = document.querySelectorAll(".inline-add-input");
const undoToast = document.getElementById("undo-toast");
const undoDelete = document.getElementById("undo-delete");
const undoMessage = document.getElementById("undo-message");

const undoState = {
  projectId: null,
  section: null,
  text: "",
  timer: null,
};

function toggleInlineAdds(enabled) {
  inlineAddButtons.forEach((button) => {
    button.disabled = !enabled;
  });
  inlineAddInputs.forEach((input) => {
    input.disabled = !enabled;
    if (!enabled) {
      input.value = "";
      autoGrow(input);
    }
  });
}

function setInteractivity(enabled) {
  toggleInlineAdds(enabled);
  progressSlider.disabled = !enabled;
  summaryInput.disabled = !enabled;
  objectiveInput.disabled = !enabled;
  goalInput.disabled = !enabled;
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
  const urlProjectId = readProjectFromUrl();
  const includeArchived = urlProjectId !== null;
  const listUrl = includeArchived
    ? "/api/projects?include_archived=1"
    : "/api/projects";
  const data = await requestJSON(listUrl);
  data.projects.forEach((project) => {
    const option = document.createElement("option");
    option.value = project.id;
    option.textContent = project.name;
    projectSelect.append(option);
  });
  state.projectsLoaded = true;

  if (includeArchived) {
    projectSelect.value = String(urlProjectId);
  }

  if (includeArchived && !projectSelect.value) {
    resetEmptyState();
    clearProjectInUrl();
    return;
  }

  if (projectSelect.value) {
    state.projectId = Number(projectSelect.value);
    emptyState.hidden = true;
    setInteractivity(false);
    const projectData = await loadProject(state.projectId);
    if (!projectData && includeArchived) {
      projectSelect.value = "";
      resetEmptyState();
      clearProjectInUrl();
      return;
    }
    if (projectData) {
      setInteractivity(true);
    }
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

      const body = document.createElement("div");
      body.className = "item-body";

      const text = document.createElement("span");
      text.className = "item-text";
      text.textContent = item.text;

      const dateLabel = formatItemDate(item.created_at);
      if (dateLabel) {
        const date = document.createElement("span");
        date.className = "item-date";
        date.textContent = dateLabel;
        body.append(text, date);
      } else {
        body.append(text);
      }

      actions.append(editButton, saveButton, cancelButton, deleteButton);
      li.append(body, actions);
      list.append(li);
    });
  });
}

function resetEmptyState() {
  state.projectId = null;
  emptyState.hidden = false;
  setInteractivity(false);
  goalInput.value = String(DEFAULT_GOAL);
  updateProgressDisplay(0, DEFAULT_GOAL);
  renderSections({});
  summaryInput.value = "";
  objectiveInput.value = "";
  questionsInput.value = "";
  hideUndoToast();
}

function clampPercent(value) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    return 0;
  }
  return Math.min(100, Math.max(0, Math.round(parsed)));
}

function normalizeGoal(value) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    return DEFAULT_GOAL;
  }
  return Math.max(1, Math.round(parsed));
}

function percentToUnits(percent, goal) {
  return Math.round((percent / 100) * goal);
}

function unitsToPercent(units, goal) {
  if (goal <= 0) {
    return 0;
  }
  return Math.round((units / goal) * 100);
}

function updateProgressDisplay(progressValue, goalValue) {
  const safeGoal = normalizeGoal(goalValue);
  const safePercent = clampPercent(progressValue);
  const unitValue = percentToUnits(safePercent, safeGoal);
  state.progressPercent = safePercent;
  state.goalValue = safeGoal;
  progressSlider.max = String(safeGoal);
  progressSlider.value = String(unitValue);
  progressPercent.textContent = `${unitValue} / ${safeGoal}`;
  progressSlider.style.setProperty("--progress", `${safePercent}%`);
}

function readProjectFromUrl() {
  const params = new URLSearchParams(window.location.search);
  const raw = params.get("project");
  if (!raw) {
    return null;
  }
  const parsed = Number(raw);
  if (!Number.isInteger(parsed) || parsed <= 0) {
    return null;
  }
  return parsed;
}

function setProjectInUrl(projectId) {
  const params = new URLSearchParams(window.location.search);
  params.set("project", String(projectId));
  const url = `${window.location.pathname}?${params.toString()}`;
  window.history.replaceState({}, "", url);
}

function clearProjectInUrl() {
  const params = new URLSearchParams(window.location.search);
  params.delete("project");
  const query = params.toString();
  const url = query ? `${window.location.pathname}?${query}` : window.location.pathname;
  window.history.replaceState({}, "", url);
}

function autoGrow(input) {
  input.style.height = "auto";
  input.style.height = `${input.scrollHeight}px`;
}

function formatItemDate(isoString) {
  if (!isoString) {
    return "";
  }
  const parsed = new Date(isoString);
  if (Number.isNaN(parsed.getTime())) {
    return "";
  }
  const now = new Date();
  const options = { month: "short", day: "numeric" };
  if (parsed.getFullYear() !== now.getFullYear()) {
    options.year = "numeric";
  }
  return parsed.toLocaleDateString(undefined, options);
}

function showUndoToast(text, anchor) {
  if (undoState.timer) {
    window.clearTimeout(undoState.timer);
  }
  undoMessage.textContent = text || "Item deleted.";
  undoToast.hidden = false;
  if (anchor) {
    positionUndoToast(anchor);
  }
  undoState.timer = window.setTimeout(() => {
    hideUndoToast();
  }, 5000);
}

function hideUndoToast() {
  if (undoState.timer) {
    window.clearTimeout(undoState.timer);
  }
  undoToast.hidden = true;
  undoToast.style.left = "";
  undoToast.style.top = "";
  undoState.projectId = null;
  undoState.section = null;
  undoState.text = "";
  undoState.timer = null;
}

function positionUndoToast(anchor) {
  const rect = anchor.getBoundingClientRect();
  const toastRect = undoToast.getBoundingClientRect();
  const margin = 8;
  let top = rect.top - toastRect.height - margin;
  if (top < margin) {
    top = rect.bottom + margin;
  }
  let left = rect.left + rect.width / 2;
  const minLeft = toastRect.width / 2 + margin;
  const maxLeft = window.innerWidth - toastRect.width / 2 - margin;
  left = Math.min(Math.max(left, minLeft), maxLeft);
  undoToast.style.top = `${Math.round(top)}px`;
  undoToast.style.left = `${Math.round(left)}px`;
}

function renderProject(project) {
  const goalValue = normalizeGoal(project.goal);
  goalInput.value = String(goalValue);
  updateProgressDisplay(project.progress, goalValue);
  objectiveInput.value = project.objective || "";
  summaryInput.value = project.summary || "";
  questionsInput.value = project.questions || "";
  renderSections(project.sections || {});
}

async function loadProject(projectId) {
  try {
    const data = await requestJSON(`/api/projects/${projectId}`);
    renderProject(data);
    return data;
  } catch (error) {
    console.warn("Failed to load resident", error);
    return null;
  }
}

async function handleInlineAdd(section, input) {
  if (!state.projectId) {
    return;
  }
  const text = input.value.trim();
  if (!text) {
    return;
  }
  await requestJSON(`/api/projects/${state.projectId}/items`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ section, text }),
  });
  input.value = "";
  autoGrow(input);
  await loadProject(state.projectId);
}

function scheduleProgressSave(value) {
  if (!state.projectId) {
    return;
  }
  if (state.progressTimer) {
    window.clearTimeout(state.progressTimer);
  }
  const normalized = clampPercent(value);
  state.progressTimer = window.setTimeout(async () => {
    await requestJSON(`/api/projects/${state.projectId}/progress`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ progress: normalized }),
    });
  }, 250);
}

function scheduleObjectiveSave() {
  if (!state.projectId) {
    return;
  }
  if (state.objectiveTimer) {
    window.clearTimeout(state.objectiveTimer);
  }
  state.objectiveTimer = window.setTimeout(async () => {
    const objective = objectiveInput.value.trim();
    await requestJSON(`/api/projects/${state.projectId}/objective`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ objective }),
    });
  }, 500);
}

function scheduleGoalSave(goalValue) {
  if (!state.projectId) {
    return;
  }
  if (state.goalTimer) {
    window.clearTimeout(state.goalTimer);
  }
  const normalized = normalizeGoal(goalValue);
  state.goalTimer = window.setTimeout(async () => {
    await requestJSON(`/api/projects/${state.projectId}/goal`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ goal: normalized }),
    });
    goalInput.value = String(normalized);
  }, 500);
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

function scheduleSummarySave() {
  if (!state.projectId) {
    return;
  }
  if (state.summaryTimer) {
    window.clearTimeout(state.summaryTimer);
  }
  state.summaryTimer = window.setTimeout(async () => {
    await requestJSON(`/api/projects/${state.projectId}/summary`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ summary: summaryInput.value }),
    });
  }, 500);
}

function handleGoalInput() {
  if (!state.projectId) {
    return;
  }
  const raw = goalInput.value.trim();
  if (!raw) {
    return;
  }
  const parsed = Number(raw);
  if (!Number.isFinite(parsed)) {
    return;
  }
  const normalized = normalizeGoal(parsed);
  updateProgressDisplay(state.progressPercent, normalized);
  scheduleGoalSave(normalized);
}

projectSelect.addEventListener("change", async (event) => {
  const selected = event.target.value;
  if (!selected) {
    resetEmptyState();
    clearProjectInUrl();
    return;
  }

  state.projectId = Number(selected);
  emptyState.hidden = true;
  setInteractivity(false);
  setProjectInUrl(state.projectId);
  const projectData = await loadProject(state.projectId);
  if (projectData) {
    setInteractivity(true);
  }
});

inlineAddButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const wrapper = button.closest(".inline-add");
    const input = wrapper?.querySelector(".inline-add-input");
    const section = button.dataset.section;
    if (input && section) {
      handleInlineAdd(section, input);
    }
  });
});

inlineAddInputs.forEach((input) => {
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      const wrapper = input.closest(".inline-add");
      const section = wrapper?.dataset.section;
      if (section) {
        handleInlineAdd(section, input);
      }
    }
  });
  input.addEventListener("input", () => autoGrow(input));
  autoGrow(input);
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
    const textNode = listItem.querySelector(".item-text");
    const inputNode = listItem.querySelector(".item-input");
    const textValue = (inputNode ? inputNode.value : textNode?.textContent || "")
      .trim();
    undoState.projectId = state.projectId;
    undoState.section = listItem.dataset.section || "";
    undoState.text = textValue;
    await requestJSON(`/api/items/${itemId}`, { method: "DELETE" });
    if (state.projectId) {
      await loadProject(state.projectId);
    }
    showUndoToast("Item deleted.", listItem);
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

    const input = document.createElement("textarea");
    input.className = "item-input";
    input.rows = 1;
    input.value = currentText;
    textNode.replaceWith(input);
    listItem.classList.add("is-editing");
    autoGrow(input);
    input.focus();
    input.select();
    input.addEventListener("input", () => autoGrow(input));
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
  if (event.key === "Enter" && !event.shiftKey) {
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

undoDelete.addEventListener("click", async () => {
  if (!undoState.projectId || !undoState.section) {
    hideUndoToast();
    return;
  }
  await requestJSON(`/api/projects/${undoState.projectId}/items`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ section: undoState.section, text: undoState.text }),
  });
  if (state.projectId === undoState.projectId) {
    await loadProject(state.projectId);
  }
  hideUndoToast();
});

progressSlider.addEventListener("input", (event) => {
  const units = Number(event.target.value) || 0;
  const percent = unitsToPercent(units, state.goalValue);
  const previous = state.progressPercent;
  updateProgressDisplay(percent, state.goalValue);
  if (state.projectId && percent > previous) {
    window.NorthStarConfetti?.triggerConfetti?.();
  }
  scheduleProgressSave(percent);
});

objectiveInput.addEventListener("input", scheduleObjectiveSave);
goalInput.addEventListener("input", handleGoalInput);
questionsInput.addEventListener("input", scheduleQuestionsSave);
summaryInput.addEventListener("input", scheduleSummarySave);

setInteractivity(false);
resetEmptyState();
loadProjects().catch((error) => {
  console.error(error);
});

window.addEventListener("pageshow", () => {
  if (!state.projectsLoaded) {
    return;
  }
  if (!projectSelect.value) {
    resetEmptyState();
    const urlProjectId = readProjectFromUrl();
    if (urlProjectId) {
      projectSelect.value = String(urlProjectId);
      projectSelect.dispatchEvent(new Event("change"));
    }
  }
});
