const root = document.documentElement;
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
}

applyTheme(themeState.preference);
