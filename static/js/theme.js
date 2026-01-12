const root = document.documentElement;
const themeSelect = document.getElementById("theme-select");
const themeState = {
  preference: "system",
};

function getSystemTheme() {
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function resolveTheme(preference) {
  if (preference === "system") {
    return getSystemTheme();
  }
  return preference;
}

function applyTheme(preference) {
  themeState.preference = preference;
  root.dataset.theme = resolveTheme(preference);
  if (themeSelect && themeSelect.value !== preference) {
    themeSelect.value = preference;
  }
}

applyTheme(themeState.preference);

if (themeSelect) {
  themeSelect.addEventListener("change", (event) => {
    const { value } = event.target;
    if (value === "light" || value === "dark" || value === "system") {
      applyTheme(value);
    }
  });
}
