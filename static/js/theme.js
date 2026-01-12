const root = document.documentElement;
const themeToggle = document.getElementById("theme-toggle");
const THEME_STORAGE_KEY = "theme-preference";
const themeState = {
  preference: "system",
};
const themeOptions = new Set(["light", "dark", "system"]);
const themeCycle = ["system", "dark", "light"];
const themeLabels = {
  system: "System",
  light: "Light",
  dark: "Dark",
};

function getSystemTheme() {
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function normalizePreference(value) {
  if (themeOptions.has(value)) {
    return value;
  }
  return "system";
}

function readStoredPreference() {
  try {
    return normalizePreference(window.localStorage.getItem(THEME_STORAGE_KEY));
  } catch (error) {
    return "system";
  }
}

function storePreference(value) {
  try {
    window.localStorage.setItem(THEME_STORAGE_KEY, value);
  } catch (error) {
  }
}

function resolveTheme(preference) {
  if (preference === "system") {
    return getSystemTheme();
  }
  return preference;
}

function updateToggle(preference) {
  if (!themeToggle) {
    return;
  }
  const label = themeLabels[preference] || "System";
  const resolved = resolveTheme(preference);
  const status = preference === "system" ? `${label} (${resolved})` : label;
  themeToggle.textContent = label;
  themeToggle.dataset.preference = preference;
  themeToggle.setAttribute("aria-label", `Theme: ${status}`);
  themeToggle.setAttribute("title", `Theme: ${status}`);
}

function nextPreference(preference) {
  const index = themeCycle.indexOf(preference);
  if (index === -1) {
    return "system";
  }
  return themeCycle[(index + 1) % themeCycle.length];
}

function applyTheme(preference, persist = false) {
  const normalized = normalizePreference(preference);
  themeState.preference = normalized;
  root.dataset.theme = resolveTheme(normalized);
  updateToggle(normalized);
  if (persist) {
    storePreference(normalized);
  }
}

applyTheme(readStoredPreference());

if (themeToggle) {
  themeToggle.addEventListener("click", () => {
    applyTheme(nextPreference(themeState.preference), true);
  });
}

window
  .matchMedia("(prefers-color-scheme: dark)")
  .addEventListener("change", () => {
    if (themeState.preference === "system") {
      applyTheme("system");
    }
  });

window.addEventListener("storage", (event) => {
  if (event.key === THEME_STORAGE_KEY) {
    applyTheme(event.newValue || "system");
  }
});
