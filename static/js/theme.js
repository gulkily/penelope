const root = document.documentElement;
const themeSelect = document.getElementById("theme-select");
const THEME_STORAGE_KEY = "theme-preference";
const themeState = {
  preference: "system",
};
const themeOptions = new Set(["light", "dark", "system"]);

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

function applyTheme(preference, persist = false) {
  const normalized = normalizePreference(preference);
  themeState.preference = normalized;
  root.dataset.theme = resolveTheme(normalized);
  if (themeSelect && themeSelect.value !== normalized) {
    themeSelect.value = normalized;
  }
  if (persist) {
    storePreference(normalized);
  }
}

applyTheme(readStoredPreference());

if (themeSelect) {
  themeSelect.addEventListener("change", (event) => {
    applyTheme(event.target.value, true);
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
