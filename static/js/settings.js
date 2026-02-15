const backupButton = document.getElementById("backup-download");
const backupStatus = document.getElementById("backup-status");

function setStatus(message, isError = false) {
  if (!backupStatus) {
    return;
  }
  backupStatus.textContent = message;
  backupStatus.classList.toggle("status-error", isError);
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
  setStatus("Preparing backup...");
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
    setStatus("Backup downloaded.");
  } catch (error) {
    console.error(error);
    setStatus("Backup failed. Please try again.", true);
  } finally {
    backupButton.disabled = false;
  }
}

if (backupButton) {
  backupButton.addEventListener("click", () => {
    downloadBackup().catch((error) => {
      console.error(error);
    });
  });
}
