const logoutButtons = document.querySelectorAll("[data-logout]");

async function handleLogout(event) {
  event.preventDefault();
  try {
    await fetch("/api/auth/logout", { method: "POST" });
  } catch (error) {
    // ignore
  }
  window.location.href = "/lobby";
}

logoutButtons.forEach((button) => {
  button.addEventListener("click", handleLogout);
});
