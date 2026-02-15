const backupButton = document.getElementById("backup-download");
const backupStatus = document.getElementById("backup-status");

const magicUsernameInput = document.getElementById("magic-link-username");
const magicGenerateButton = document.getElementById("magic-link-generate");
const magicCopyButton = document.getElementById("magic-link-copy");
const magicRevokeButton = document.getElementById("magic-link-revoke");
const magicLinkOutput = document.getElementById("magic-link-output");
const magicStatus = document.getElementById("magic-link-status");

let latestMagicTokenId = "";

function setBackupStatus(message, isError = false) {
  if (!backupStatus) {
    return;
  }
  backupStatus.textContent = message;
  backupStatus.classList.toggle("status-error", isError);
}

function setMagicStatus(message, isError = false) {
  if (!magicStatus) {
    return;
  }
  magicStatus.textContent = message;
  magicStatus.classList.toggle("status-error", isError);
}

function filenameFromHeaders(headers) {
  const disposition = headers.get("Content-Disposition") || "";
  const match = disposition.match(/filename=\"?([^\"]+)\"?/i);
  return match ? match[1] : null;
}

async function downloadBackup() {
  if (!backupButton) {
    return;
  }
  backupButton.disabled = true;
  setBackupStatus("Preparing backup...");
  try {
    const response = await fetch("/api/backup");
    if (!response.ok) {
      throw new Error(`Backup failed: ${response.status}`);
    }
    const blob = await response.blob();
    const filename =
      filenameFromHeaders(response.headers) || "north_star_backup.sqlite";
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    window.URL.revokeObjectURL(url);
    setBackupStatus("Backup downloaded.");
  } catch (error) {
    console.error(error);
    setBackupStatus("Backup failed. Please try again.", true);
  } finally {
    backupButton.disabled = false;
  }
}

function syncMagicControls() {
  const hasLink = Boolean(magicLinkOutput && magicLinkOutput.value);
  if (magicCopyButton) {
    magicCopyButton.disabled = !hasLink;
  }
  if (magicRevokeButton) {
    magicRevokeButton.disabled = !latestMagicTokenId;
  }
}

async function generateMagicLink() {
  if (!magicUsernameInput || !magicGenerateButton) {
    return;
  }
  const configuredUsername = magicUsernameInput.value.trim();
  if (!configuredUsername) {
    setMagicStatus("Enter a configured username.", true);
    return;
  }
  magicGenerateButton.disabled = true;
  setMagicStatus("Generating magic link...");
  try {
    const response = await fetch("/api/auth/magic-links", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        configured_username: configuredUsername,
      }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(payload.detail || "Failed to generate magic link.");
    }

    latestMagicTokenId = payload.token_id || "";
    if (magicLinkOutput) {
      magicLinkOutput.value = payload.magic_link || "";
    }
    syncMagicControls();
    setMagicStatus(`Link created for ${payload.configured_username}.`);
  } catch (error) {
    setMagicStatus(error.message || "Failed to generate magic link.", true);
  } finally {
    magicGenerateButton.disabled = false;
  }
}

async function copyMagicLink() {
  if (!magicLinkOutput || !magicLinkOutput.value) {
    return;
  }
  try {
    await navigator.clipboard.writeText(magicLinkOutput.value);
    setMagicStatus("Magic link copied.");
  } catch (error) {
    console.error(error);
    magicLinkOutput.focus();
    magicLinkOutput.select();
    setMagicStatus("Copy failed. Copy the link manually.", true);
  }
}

async function revokeMagicLink() {
  if (!latestMagicTokenId || !magicRevokeButton) {
    return;
  }
  magicRevokeButton.disabled = true;
  setMagicStatus("Revoking latest link...");
  try {
    const response = await fetch(
      `/api/auth/magic-links/${encodeURIComponent(latestMagicTokenId)}/revoke`,
      {
        method: "POST",
      }
    );
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(payload.detail || "Failed to revoke magic link.");
    }

    latestMagicTokenId = "";
    syncMagicControls();
    setMagicStatus("Latest magic link revoked.");
  } catch (error) {
    setMagicStatus(error.message || "Failed to revoke magic link.", true);
    syncMagicControls();
  }
}

if (backupButton) {
  backupButton.addEventListener("click", () => {
    downloadBackup().catch((error) => {
      console.error(error);
    });
  });
}

if (magicGenerateButton) {
  magicGenerateButton.addEventListener("click", () => {
    generateMagicLink().catch((error) => {
      console.error(error);
      setMagicStatus("Failed to generate magic link.", true);
    });
  });
}

if (magicCopyButton) {
  magicCopyButton.addEventListener("click", () => {
    copyMagicLink().catch((error) => {
      console.error(error);
      setMagicStatus("Copy failed. Copy the link manually.", true);
    });
  });
}

if (magicRevokeButton) {
  magicRevokeButton.addEventListener("click", () => {
    revokeMagicLink().catch((error) => {
      console.error(error);
      setMagicStatus("Failed to revoke magic link.", true);
    });
  });
}

if (magicUsernameInput) {
  magicUsernameInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      if (magicGenerateButton) {
        magicGenerateButton.click();
      }
    }
  });
}

syncMagicControls();
