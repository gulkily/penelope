const DEFAULT_GOAL = 100;
const DEFAULT_RESIDENCY_YEAR = new Date().getUTCFullYear();
const DEFAULT_RESIDENCY_START = `${DEFAULT_RESIDENCY_YEAR}-01-01`;
const DEFAULT_RESIDENCY_END = `${DEFAULT_RESIDENCY_YEAR}-01-31`;

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
  residencyStartDate: DEFAULT_RESIDENCY_START,
  residencyEndDate: DEFAULT_RESIDENCY_END,
  graphExpanded: false,
  projectData: null,
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
const progressGraphToggle = document.getElementById("progress-graph-toggle");
const progressGraphIndicator = document.getElementById("progress-graph-indicator");
const progressGraphPanel = document.getElementById("progress-graph-panel");
const progressGraphRange = document.getElementById("progress-graph-range");
const progressGraphAxis = document.getElementById("progress-graph-axis");
const progressGraphLabels = document.getElementById("progress-graph-labels");
const progressGraphSvg = document.getElementById("progress-graph-svg");
const progressGraphPath = document.getElementById("progress-graph-path");
const progressGraphPoints = document.getElementById("progress-graph-points");
const progressGraphEmpty = document.getElementById("progress-graph-empty");
const reorderLive = document.getElementById("reorder-live");
const transcriptOpen = document.getElementById("transcript-open");
const transcriptDialog = document.getElementById("transcript-dialog");
const transcriptClose = document.getElementById("transcript-close");
const transcriptInput = document.getElementById("transcript-input");
const transcriptAnalyze = document.getElementById("transcript-analyze");
const transcriptClear = document.getElementById("transcript-clear");
const transcriptStatus = document.getElementById("transcript-status");
const transcriptSuggestions = document.getElementById("transcript-suggestions");
const transcriptSuggestionsEmpty = document.getElementById(
  "transcript-suggestions-empty",
);
const transcriptSuggestionList = document.getElementById(
  "transcript-suggestion-list",
);
const transcriptApply = document.getElementById("transcript-apply");
const transcriptCancel = document.getElementById("transcript-cancel");

const undoState = {
  projectId: null,
  section: null,
  text: "",
  timer: null,
};

const reorderState = {
  active: false,
  item: null,
  list: null,
  pointerId: null,
  originalOrder: [],
};

const transcriptState = {
  proposal: null,
  busy: false,
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

function toggleReorderControls(enabled) {
  document.querySelectorAll(".item-drag-handle, .item-action-move").forEach(
    (button) => {
      button.disabled = !enabled;
    },
  );
}

function setInteractivity(enabled) {
  toggleInlineAdds(enabled);
  progressSlider.disabled = !enabled;
  summaryInput.disabled = !enabled;
  objectiveInput.disabled = !enabled;
  goalInput.disabled = !enabled;
  questionsInput.disabled = !enabled;
  progressGraphToggle.disabled = !enabled;
  toggleReorderControls(enabled);
  if (transcriptOpen) {
    transcriptOpen.disabled = !enabled;
  }
}

async function requestJSON(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

function getOrderedIds(list) {
  return Array.from(list.querySelectorAll(".section-item")).map(
    (item) => Number(item.dataset.itemId),
  );
}

function arraysEqual(left, right) {
  if (left.length !== right.length) {
    return false;
  }
  return left.every((value, index) => value === right[index]);
}

function formatSectionLabel(section) {
  if (!section) {
    return "section";
  }
  return section.charAt(0).toUpperCase() + section.slice(1);
}

function setTranscriptStatus(message, isError = false) {
  if (!transcriptStatus) {
    return;
  }
  transcriptStatus.textContent = message || "";
  if (message && isError) {
    transcriptStatus.dataset.status = "error";
  } else {
    delete transcriptStatus.dataset.status;
  }
}

function resetTranscriptSuggestions() {
  transcriptState.proposal = null;
  if (transcriptSuggestionList) {
    transcriptSuggestionList.replaceChildren();
  }
  if (transcriptSuggestionsEmpty) {
    transcriptSuggestionsEmpty.hidden = true;
  }
  if (transcriptSuggestions) {
    transcriptSuggestions.hidden = true;
  }
  if (transcriptApply) {
    transcriptApply.disabled = true;
  }
}

function resetTranscriptDialog() {
  if (transcriptInput) {
    transcriptInput.value = "";
  }
  setTranscriptStatus("");
  resetTranscriptSuggestions();
}

function setTranscriptBusy(isBusy) {
  transcriptState.busy = isBusy;
  if (transcriptAnalyze) {
    transcriptAnalyze.disabled = isBusy;
  }
  if (transcriptApply) {
    transcriptApply.disabled = isBusy || !transcriptState.proposal;
  }
  if (transcriptClear) {
    transcriptClear.disabled = isBusy;
  }
}

function openTranscriptDialog() {
  if (!transcriptDialog || !state.projectId) {
    return;
  }
  resetTranscriptSuggestions();
  setTranscriptStatus("");
  if (typeof transcriptDialog.showModal === "function") {
    transcriptDialog.showModal();
  }
  if (transcriptInput) {
    transcriptInput.focus();
  }
}

function closeTranscriptDialog() {
  if (!transcriptDialog || !transcriptDialog.open) {
    return;
  }
  transcriptDialog.close();
  resetTranscriptDialog();
}

function formatCurrentValue(value) {
  const text = String(value ?? "").trim();
  return text || "(empty)";
}

function normalizeComparableText(value) {
  return String(value ?? "")
    .trim()
    .replace(/\s+/g, " ")
    .toLowerCase();
}

function hasMeaningfulText(value) {
  return normalizeComparableText(value) !== "";
}

function buildSuggestionField({ field, label, value, currentValue, inputType }) {
  const wrapper = document.createElement("div");
  wrapper.className = "transcript-suggestion";
  wrapper.dataset.field = field;

  const toggle = document.createElement("label");
  toggle.className = "transcript-suggestion-toggle";
  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = true;
  const title = document.createElement("span");
  title.textContent = label;
  toggle.append(checkbox, title);

  const body = document.createElement("div");
  body.className = "transcript-suggestion-body";

  const current = document.createElement("p");
  current.className = "transcript-suggestion-current";
  current.textContent = `Current: ${formatCurrentValue(currentValue)}`;

  let input = null;
  if (inputType === "textarea") {
    input = document.createElement("textarea");
    input.rows = 3;
    input.className = "field-input field-textarea transcript-suggestion-input";
  } else {
    input = document.createElement("input");
    input.type = inputType;
    input.className = "field-input transcript-suggestion-input";
  }
  input.value = value ?? "";

  body.append(current, input);
  wrapper.append(toggle, body);

  return wrapper;
}

function buildItemSuggestion(section, text) {
  const wrapper = document.createElement("div");
  wrapper.className = "transcript-suggestion";
  wrapper.dataset.field = "item";
  wrapper.dataset.section = section;

  const toggle = document.createElement("label");
  toggle.className = "transcript-suggestion-toggle";
  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = true;
  const title = document.createElement("span");
  title.textContent = `Add to ${formatSectionLabel(section)}`;
  toggle.append(checkbox, title);

  const body = document.createElement("div");
  body.className = "transcript-suggestion-body";

  const input = document.createElement("textarea");
  input.rows = 2;
  input.className = "field-input field-textarea transcript-suggestion-input";
  input.value = text ?? "";

  body.append(input);
  wrapper.append(toggle, body);

  return wrapper;
}

function renderTranscriptSuggestions(proposal) {
  if (!transcriptSuggestionList || !transcriptSuggestions) {
    return;
  }

  const project = state.projectData || {};
  const suggestions = [];
  const existingItems = project.sections || {};
  const existingItemText = {};

  Object.entries(existingItems).forEach(([section, items]) => {
    existingItemText[section] = new Set(
      (items || [])
        .map((item) => normalizeComparableText(item.text))
        .filter((text) => text),
    );
  });

  if (
    proposal.summary !== null &&
    proposal.summary !== undefined &&
    hasMeaningfulText(proposal.summary) &&
    normalizeComparableText(proposal.summary) !==
      normalizeComparableText(project.summary)
  ) {
    suggestions.push(
      buildSuggestionField({
        field: "summary",
        label: "Summary",
        value: proposal.summary,
        currentValue: project.summary,
        inputType: "textarea",
      }),
    );
  }

  if (
    proposal.questions !== null &&
    proposal.questions !== undefined &&
    hasMeaningfulText(proposal.questions) &&
    normalizeComparableText(proposal.questions) !==
      normalizeComparableText(project.questions)
  ) {
    suggestions.push(
      buildSuggestionField({
        field: "questions",
        label: "Questions",
        value: proposal.questions,
        currentValue: project.questions,
        inputType: "textarea",
      }),
    );
  }

  if (
    proposal.objective !== null &&
    proposal.objective !== undefined &&
    hasMeaningfulText(proposal.objective) &&
    normalizeComparableText(proposal.objective) !==
      normalizeComparableText(project.objective)
  ) {
    suggestions.push(
      buildSuggestionField({
        field: "objective",
        label: "Objective",
        value: proposal.objective,
        currentValue: project.objective,
        inputType: "text",
      }),
    );
  }

  if (proposal.goal !== null && proposal.goal !== undefined) {
    const proposedGoal = normalizeGoal(proposal.goal);
    const currentGoal = normalizeGoal(project.goal);
    if (proposedGoal !== currentGoal) {
      suggestions.push(
        buildSuggestionField({
          field: "goal",
          label: "Goal",
          value: String(proposedGoal),
          currentValue: project.goal,
          inputType: "number",
        }),
      );
    }
  }

  if (proposal.progress !== null && proposal.progress !== undefined) {
    const proposedProgress = clampPercent(proposal.progress);
    const currentProgress = clampPercent(project.progress);
    if (proposedProgress !== currentProgress) {
      suggestions.push(
        buildSuggestionField({
          field: "progress",
          label: "Progress percent",
          value: String(proposedProgress),
          currentValue: project.progress,
          inputType: "number",
        }),
      );
    }
  }

  const items = proposal.items_to_add || [];
  items.forEach((item) => {
    if (!item || !item.section) {
      return;
    }
    const normalizedText = normalizeComparableText(item.text);
    if (!normalizedText) {
      return;
    }
    const existing = existingItemText[item.section];
    if (existing && existing.has(normalizedText)) {
      return;
    }
    suggestions.push(buildItemSuggestion(item.section, item.text));
  });

  transcriptSuggestionList.replaceChildren(...suggestions);
  transcriptSuggestions.hidden = false;
  transcriptState.proposal = proposal;

  const hasSuggestions = suggestions.length > 0;
  if (transcriptSuggestionsEmpty) {
    transcriptSuggestionsEmpty.hidden = hasSuggestions;
  }
  if (transcriptApply) {
    transcriptApply.disabled = !hasSuggestions;
  }
}

function collectTranscriptUpdates() {
  if (!transcriptSuggestionList) {
    return null;
  }

  const updates = {
    summary: null,
    questions: null,
    objective: null,
    goal: null,
    progress: null,
    items_to_add: [],
  };
  let hasUpdates = false;

  transcriptSuggestionList
    .querySelectorAll(".transcript-suggestion")
    .forEach((card) => {
      const checkbox = card.querySelector("input[type='checkbox']");
      if (!checkbox || !checkbox.checked) {
        return;
      }

      const field = card.dataset.field;
      const input = card.querySelector(".transcript-suggestion-input");
      const rawValue = input ? input.value.trim() : "";

      if (field === "item") {
        const section = card.dataset.section;
        if (!section || !rawValue) {
          throw new Error("Every selected item needs text.");
        }
        updates.items_to_add.push({ section, text: rawValue });
        hasUpdates = true;
        return;
      }

      if (field === "goal") {
        if (!rawValue) {
          throw new Error("Goal cannot be empty.");
        }
        const parsed = Number(rawValue);
        if (!Number.isFinite(parsed)) {
          throw new Error("Goal must be a number.");
        }
        updates.goal = normalizeGoal(parsed);
        hasUpdates = true;
        return;
      }

      if (field === "progress") {
        if (!rawValue) {
          throw new Error("Progress cannot be empty.");
        }
        const parsed = Number(rawValue);
        if (!Number.isFinite(parsed)) {
          throw new Error("Progress must be a number.");
        }
        updates.progress = clampPercent(parsed);
        hasUpdates = true;
        return;
      }

      updates[field] = rawValue;
      hasUpdates = true;
    });

  if (!hasUpdates) {
    return null;
  }
  return updates;
}

async function analyzeTranscript() {
  if (!state.projectId || !transcriptInput) {
    return;
  }
  const transcript = transcriptInput.value.trim();
  if (!transcript) {
    setTranscriptStatus("Paste a transcript to analyze.", true);
    return;
  }

  setTranscriptStatus("Analyzing transcript...");
  setTranscriptBusy(true);
  resetTranscriptSuggestions();

  try {
    const data = await requestJSON(`/api/projects/${state.projectId}/transcript`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ transcript }),
    });
    renderTranscriptSuggestions(data.proposal || {});
    if (data.proposal) {
      setTranscriptStatus("Review the suggested updates below.");
    } else {
      setTranscriptStatus("No suggestions returned.", true);
    }
  } catch (error) {
    console.warn("Transcript analysis failed", error);
    setTranscriptStatus("Transcript analysis failed. Try again.", true);
  } finally {
    setTranscriptBusy(false);
  }
}

async function applyTranscriptUpdates() {
  if (!state.projectId) {
    return;
  }

  let updates = null;
  try {
    updates = collectTranscriptUpdates();
  } catch (error) {
    setTranscriptStatus(error.message || "Fix the highlighted updates.", true);
    return;
  }

  if (!updates) {
    setTranscriptStatus("Select at least one update to apply.", true);
    return;
  }

  setTranscriptStatus("Applying updates...");
  setTranscriptBusy(true);

  try {
    if (updates.summary !== null) {
      await requestJSON(`/api/projects/${state.projectId}/summary`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ summary: updates.summary }),
      });
    }

    if (updates.questions !== null) {
      await requestJSON(`/api/projects/${state.projectId}/questions`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ questions: updates.questions }),
      });
    }

    if (updates.objective !== null) {
      await requestJSON(`/api/projects/${state.projectId}/objective`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ objective: updates.objective }),
      });
    }

    if (updates.goal !== null) {
      await requestJSON(`/api/projects/${state.projectId}/goal`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ goal: updates.goal }),
      });
    }

    if (updates.progress !== null) {
      await requestJSON(`/api/projects/${state.projectId}/progress`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ progress: updates.progress }),
      });
      await refreshProgressGraph();
    }

    for (const item of updates.items_to_add) {
      await requestJSON(`/api/projects/${state.projectId}/items`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ section: item.section, text: item.text }),
      });
    }

    await loadProject(state.projectId);
    setTranscriptStatus("Updates applied.");
    closeTranscriptDialog();
  } catch (error) {
    console.warn("Failed to apply transcript updates", error);
    setTranscriptStatus("Failed to apply updates. Try again.", true);
  } finally {
    setTranscriptBusy(false);
  }
}

function announceReorder(list, item) {
  if (!reorderLive) {
    return;
  }
  const items = Array.from(list.querySelectorAll(".section-item"));
  const position = items.indexOf(item) + 1;
  const total = items.length;
  const section = formatSectionLabel(list.dataset.section);
  reorderLive.textContent = "";
  reorderLive.textContent = `Moved item to position ${position} of ${total} in ${section}.`;
}

async function persistSectionOrder(list) {
  if (!state.projectId) {
    return;
  }
  const section = list.dataset.section;
  if (!section) {
    return;
  }
  const orderedIds = getOrderedIds(list);
  try {
    await requestJSON(`/api/projects/${state.projectId}/items/order`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ section, ordered_ids: orderedIds }),
    });
  } catch (error) {
    console.warn("Failed to reorder items", error);
    if (state.projectId) {
      await loadProject(state.projectId);
    }
  }
}

function listHasEditing(list) {
  return Boolean(list.querySelector(".section-item.is-editing"));
}

function canReorder(listItem) {
  if (!state.projectId) {
    return false;
  }
  if (!listItem || listItem.classList.contains("is-editing")) {
    return false;
  }
  const list = listItem.closest(".section-list");
  if (!list || listHasEditing(list)) {
    return false;
  }
  return true;
}

async function moveItem(listItem, direction) {
  const list = listItem.closest(".section-list");
  if (!list || listHasEditing(list)) {
    return;
  }
  const items = Array.from(list.querySelectorAll(".section-item"));
  const index = items.indexOf(listItem);
  const targetIndex = index + direction;
  if (targetIndex < 0 || targetIndex >= items.length) {
    return;
  }
  const target = items[targetIndex];
  if (direction < 0) {
    list.insertBefore(listItem, target);
  } else {
    list.insertBefore(listItem, target.nextSibling);
  }
  await persistSectionOrder(list);
  announceReorder(list, listItem);
}

function startDrag(pointerId, listItem, list) {
  reorderState.active = true;
  reorderState.item = listItem;
  reorderState.list = list;
  reorderState.pointerId = pointerId;
  reorderState.originalOrder = getOrderedIds(list);
  listItem.classList.add("is-dragging");
  list.classList.add("is-reordering");
}

async function finishDrag() {
  const { item, list, originalOrder } = reorderState;
  if (item) {
    item.classList.remove("is-dragging");
  }
  if (list) {
    list.classList.remove("is-reordering");
  }
  reorderState.active = false;
  reorderState.item = null;
  reorderState.list = null;
  reorderState.pointerId = null;
  reorderState.originalOrder = [];

  if (!list || !item) {
    return;
  }
  const newOrder = getOrderedIds(list);
  if (!arraysEqual(originalOrder, newOrder)) {
    await persistSectionOrder(list);
    announceReorder(list, item);
  }
}

function handleDragMove(event) {
  if (!reorderState.active || event.pointerId !== reorderState.pointerId) {
    return;
  }
  const list = reorderState.list;
  const item = reorderState.item;
  if (!list || !item) {
    return;
  }
  const target = document
    .elementFromPoint(event.clientX, event.clientY)
    ?.closest(".section-item");
  if (!target || target === item) {
    return;
  }
  if (target.closest(".section-list") !== list) {
    return;
  }
  const rect = target.getBoundingClientRect();
  const before = event.clientY < rect.top + rect.height / 2;
  if (before) {
    list.insertBefore(item, target);
  } else {
    list.insertBefore(item, target.nextSibling);
  }
  event.preventDefault();
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

      const dragHandle = document.createElement("button");
      dragHandle.type = "button";
      dragHandle.className = "item-drag-handle";
      dragHandle.setAttribute("aria-label", "Reorder item");
      dragHandle.setAttribute("title", "Drag to reorder");

      const actions = document.createElement("span");
      actions.className = "item-actions";

      const moveUpButton = document.createElement("button");
      moveUpButton.type = "button";
      moveUpButton.className = "item-action item-action-move";
      moveUpButton.textContent = "Up";
      moveUpButton.dataset.action = "move-up";
      moveUpButton.setAttribute("aria-label", "Move item up");

      const moveDownButton = document.createElement("button");
      moveDownButton.type = "button";
      moveDownButton.className = "item-action item-action-move";
      moveDownButton.textContent = "Down";
      moveDownButton.dataset.action = "move-down";
      moveDownButton.setAttribute("aria-label", "Move item down");

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

      actions.append(
        moveUpButton,
        moveDownButton,
        editButton,
        saveButton,
        cancelButton,
        deleteButton,
      );
      li.append(dragHandle, body, actions);
      list.append(li);
    });
  });
}

function resetEmptyState() {
  state.projectId = null;
  state.projectData = null;
  emptyState.hidden = false;
  setInteractivity(false);
  goalInput.value = String(DEFAULT_GOAL);
  updateProgressDisplay(0, DEFAULT_GOAL);
  updateGraphBounds({
    residency_start_date: DEFAULT_RESIDENCY_START,
    residency_end_date: DEFAULT_RESIDENCY_END,
  });
  clearProgressGraph();
  setGraphExpanded(false);
  renderSections({});
  summaryInput.value = "";
  objectiveInput.value = "";
  questionsInput.value = "";
  hideUndoToast();
  closeTranscriptDialog();
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

function parseDateOnly(value, endOfDay = false) {
  if (!value) {
    return null;
  }
  const suffix = endOfDay ? "T23:59:59Z" : "T00:00:00Z";
  const parsed = new Date(`${value}${suffix}`);
  if (Number.isNaN(parsed.getTime())) {
    return null;
  }
  return parsed;
}

function parseHistoryTimestamp(value) {
  if (!value) {
    return null;
  }
  const direct = new Date(value);
  if (!Number.isNaN(direct.getTime())) {
    return direct;
  }
  let normalized = value.trim().replace(" ", "T");
  normalized = normalized.replace(/\.(\d{3})\d+/, ".$1");
  if (!/[zZ]|[+-]\d{2}:?\d{2}$/.test(normalized)) {
    normalized = `${normalized}Z`;
  }
  normalized = normalized.replace(/\+00:00$/, "Z");
  normalized = normalized.replace(/([+-]\d{2}):(\d{2})$/, "$1$2");
  const retry = new Date(normalized);
  if (Number.isNaN(retry.getTime())) {
    return null;
  }
  return retry;
}

function formatGraphDate(date) {
  return date.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
    timeZone: "UTC",
  });
}

function formatGraphTickDate(date, includeYear) {
  return date.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: includeYear ? "numeric" : undefined,
    timeZone: "UTC",
  });
}

function updateGraphRangeLabel() {
  const start = parseDateOnly(state.residencyStartDate) ||
    parseDateOnly(DEFAULT_RESIDENCY_START);
  const end = parseDateOnly(state.residencyEndDate, true) ||
    parseDateOnly(DEFAULT_RESIDENCY_END, true);
  if (!start || !end) {
    progressGraphRange.textContent = "Date range unavailable";
    return;
  }
  progressGraphRange.textContent = `${formatGraphDate(start)} – ${formatGraphDate(end)}`;
}

function setGraphExpanded(expanded) {
  state.graphExpanded = expanded;
  progressGraphPanel.hidden = !expanded;
  progressGraphToggle.setAttribute("aria-expanded", expanded ? "true" : "false");
  progressGraphIndicator.textContent = expanded ? "Hide" : "Show";
  if (!expanded) {
    clearProgressGraph();
    clearGraphAxis();
  }
}

function updateGraphBounds(project) {
  state.residencyStartDate = project.residency_start_date || DEFAULT_RESIDENCY_START;
  state.residencyEndDate = project.residency_end_date || DEFAULT_RESIDENCY_END;
  updateGraphRangeLabel();
  if (state.graphExpanded) {
    refreshProgressGraph();
  }
}

function clearProgressGraph() {
  progressGraphPath.setAttribute("d", "");
  progressGraphPoints.replaceChildren();
  progressGraphSvg.hidden = false;
  progressGraphEmpty.hidden = false;
}

function clearGraphAxis() {
  progressGraphAxis.replaceChildren();
  progressGraphLabels.replaceChildren();
}

function getGraphDimensions() {
  const width = Math.max(1, progressGraphSvg.clientWidth);
  const height = Math.max(1, progressGraphSvg.clientHeight);
  const paddingX = Math.max(6, Math.round(width * 0.04));
  const paddingY = Math.max(6, Math.round(height * 0.08));
  const labelSpace = 18;
  const innerWidth = Math.max(1, width - paddingX * 2);
  const innerHeight = Math.max(1, height - paddingY * 2 - labelSpace);
  return {
    width,
    height,
    paddingX,
    paddingY,
    labelSpace,
    innerWidth,
    innerHeight,
  };
}

function renderGraphAxis(start, end, dimensions) {
  const ticks = 5;
  const rangeMs = end.getTime() - start.getTime() || 1;
  const includeYear = start.getUTCFullYear() !== end.getUTCFullYear();
  const lines = document.createDocumentFragment();
  const labels = document.createDocumentFragment();
  for (let index = 0; index < ticks; index += 1) {
    const ratio = ticks === 1 ? 0 : index / (ticks - 1);
    const x = dimensions.paddingX + ratio * dimensions.innerWidth;
    const tickDate = new Date(start.getTime() + rangeMs * ratio);
    const line = document.createElement("div");
    line.className = "graph-axis-line";
    line.style.left = `${Math.round(x)}px`;
    line.style.top = `${dimensions.paddingY}px`;
    line.style.height = `${Math.max(1, dimensions.innerHeight)}px`;
    lines.append(line);

    const label = document.createElement("span");
    label.className = "graph-axis-label";
    label.style.left = `${Math.round(x)}px`;
    label.textContent = formatGraphTickDate(tickDate, includeYear);
    labels.append(label);
  }
  progressGraphAxis.replaceChildren(lines);
  progressGraphLabels.replaceChildren(labels);
}

function renderProgressGraph(history) {
  const start = parseDateOnly(state.residencyStartDate) ||
    parseDateOnly(DEFAULT_RESIDENCY_START);
  const end = parseDateOnly(state.residencyEndDate, true) ||
    parseDateOnly(DEFAULT_RESIDENCY_END, true);
  if (!start || !end || end < start) {
    clearGraphAxis();
    clearProgressGraph();
    return;
  }

  const dimensions = getGraphDimensions();
  progressGraphSvg.setAttribute(
    "viewBox",
    `0 0 ${dimensions.width} ${dimensions.height}`,
  );
  renderGraphAxis(start, end, dimensions);

  const filtered = history
    .map((entry) => ({ ...entry, time: parseHistoryTimestamp(entry.recorded_at) }))
    .filter((entry) => entry.time && !Number.isNaN(entry.time.getTime()))
    .filter((entry) => entry.time >= start && entry.time <= end)
    .sort((a, b) => a.time - b.time);

  if (!filtered.length) {
    clearProgressGraph();
    return;
  }

  const rangeMs = end.getTime() - start.getTime() || 1;
  const points = filtered.map((entry) => {
    const ratio = (entry.time.getTime() - start.getTime()) / rangeMs;
    const x = dimensions.paddingX + ratio * dimensions.innerWidth;
    const y =
      dimensions.paddingY +
      (1 - clampPercent(entry.progress) / 100) * dimensions.innerHeight;
    return { x: Math.min(dimensions.width, Math.max(0, x)), y };
  });

  const path = points
    .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`)
    .join(" ");
  progressGraphPath.setAttribute("d", path);

  const markers = document.createDocumentFragment();
  const radius = Math.max(3, Math.round(dimensions.height * 0.025));
  points.forEach((point) => {
    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", point.x.toString());
    circle.setAttribute("cy", point.y.toString());
    circle.setAttribute("r", radius.toString());
    markers.append(circle);
  });
  progressGraphPoints.replaceChildren(markers);
  progressGraphSvg.hidden = false;
  progressGraphEmpty.hidden = true;
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
  updateGraphBounds(project);
  renderSections(project.sections || {});
}

async function loadProject(projectId) {
  try {
    const data = await requestJSON(`/api/projects/${projectId}`);
    renderProject(data);
    state.projectData = data;
    if (state.graphExpanded) {
      await refreshProgressGraph();
    }
    return data;
  } catch (error) {
    console.warn("Failed to load resident", error);
    state.projectData = null;
    return null;
  }
}

async function refreshProgressGraph() {
  if (!state.projectId || !state.graphExpanded) {
    return;
  }
  try {
    const data = await requestJSON(
      `/api/projects/${state.projectId}/progress/history`,
    );
    renderProgressGraph(data.history || []);
  } catch (error) {
    console.warn("Failed to load progress history", error);
    clearProgressGraph();
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
    await refreshProgressGraph();
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
  resetTranscriptDialog();
  const projectData = await loadProject(state.projectId);
  if (projectData) {
    setInteractivity(true);
  }
});

if (transcriptOpen) {
  transcriptOpen.addEventListener("click", openTranscriptDialog);
}

if (transcriptClose) {
  transcriptClose.addEventListener("click", closeTranscriptDialog);
}

if (transcriptCancel) {
  transcriptCancel.addEventListener("click", closeTranscriptDialog);
}

if (transcriptDialog) {
  transcriptDialog.addEventListener("cancel", (event) => {
    event.preventDefault();
    closeTranscriptDialog();
  });
}

if (transcriptAnalyze) {
  transcriptAnalyze.addEventListener("click", analyzeTranscript);
}

if (transcriptApply) {
  transcriptApply.addEventListener("click", applyTranscriptUpdates);
}

if (transcriptClear) {
  transcriptClear.addEventListener("click", () => {
    if (transcriptInput) {
      transcriptInput.value = "";
      transcriptInput.focus();
    }
    resetTranscriptSuggestions();
    setTranscriptStatus("");
  });
}

progressGraphToggle.addEventListener("click", async () => {
  const expanded = progressGraphPanel.hidden;
  setGraphExpanded(expanded);
  if (expanded) {
    await refreshProgressGraph();
  }
});

inlineAddButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const wrapper = button.closest(".inline-add");
    const input = wrapper ? wrapper.querySelector(".inline-add-input") : null;
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
      const section = wrapper ? wrapper.dataset.section : null;
      if (section) {
        handleInlineAdd(section, input);
      }
    }
  });
  input.addEventListener("input", () => autoGrow(input));
  autoGrow(input);
});

document.addEventListener("pointerdown", (event) => {
  const handle = event.target.closest(".item-drag-handle");
  if (!handle || handle.disabled || reorderState.active) {
    return;
  }
  const listItem = handle.closest(".section-item");
  if (!canReorder(listItem)) {
    return;
  }
  const list = listItem.closest(".section-list");
  if (!list) {
    return;
  }
  handle.setPointerCapture(event.pointerId);
  startDrag(event.pointerId, listItem, list);
  event.preventDefault();
});

document.addEventListener("pointermove", handleDragMove);

document.addEventListener("pointerup", (event) => {
  if (!reorderState.active || event.pointerId !== reorderState.pointerId) {
    return;
  }
  if (event.target.releasePointerCapture) {
    event.target.releasePointerCapture(event.pointerId);
  }
  finishDrag();
});

document.addEventListener("pointercancel", (event) => {
  if (!reorderState.active || event.pointerId !== reorderState.pointerId) {
    return;
  }
  if (event.target.releasePointerCapture) {
    event.target.releasePointerCapture(event.pointerId);
  }
  finishDrag();
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

  if (button.dataset.action === "move-up") {
    if (canReorder(listItem)) {
      await moveItem(listItem, -1);
    }
    return;
  }

  if (button.dataset.action === "move-down") {
    if (canReorder(listItem)) {
      await moveItem(listItem, 1);
    }
    return;
  }

  if (button.dataset.action === "delete") {
    const textNode = listItem.querySelector(".item-text");
    const inputNode = listItem.querySelector(".item-input");
    const textValue = (
      inputNode ? inputNode.value : (textNode ? textNode.textContent : "") || ""
    ).trim();
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

document.addEventListener("keydown", async (event) => {
  const handle = event.target.closest(".item-drag-handle");
  if (!handle) {
    return;
  }
  if (event.key !== "ArrowUp" && event.key !== "ArrowDown") {
    return;
  }
  const listItem = handle.closest(".section-item");
  if (!canReorder(listItem)) {
    return;
  }
  event.preventDefault();
  await moveItem(listItem, event.key === "ArrowUp" ? -1 : 1);
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
    const confetti = window.NorthStarConfetti;
    if (confetti && typeof confetti.triggerConfetti === "function") {
      confetti.triggerConfetti();
    }
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
