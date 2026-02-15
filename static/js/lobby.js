const STORAGE_KEYS = {
  publicKey: "auth_public_key_spki",
  privateKey: "auth_private_key_jwk",
  fingerprint: "auth_fingerprint",
  username: "auth_username",
  requestId: "auth_request_id",
  code: "auth_lobby_code",
};
const MAGIC_TOKEN_PARAM = "magic_token";

const elements = {
  usernameInput: document.getElementById("username-input"),
  requestButton: document.getElementById("request-access"),
  requestMessage: document.getElementById("request-message"),
  requestPanel: document.getElementById("request-panel"),
  lobbyStatus: document.getElementById("lobby-status"),
  statusText: document.getElementById("status-text"),
  statusCode: document.getElementById("status-code"),
  statusFingerprint: document.getElementById("status-fingerprint"),
  statusMessage: document.getElementById("status-message"),
  approvalPanel: document.getElementById("approval-panel"),
  approvalList: document.getElementById("approval-list"),
  usernameUpdate: document.getElementById("username-update"),
  usernameSave: document.getElementById("username-save"),
  usernameMessage: document.getElementById("username-message"),
};

const textEncoder = new TextEncoder();
let statusPoller = null;
let currentUsername = "";
const WEB_CRYPTO_ERROR =
  "Secure cryptography is unavailable. Use HTTPS (not HTTP) and a modern browser.";

function resolveSubtleCrypto() {
  if (window.crypto && window.crypto.subtle) {
    return window.crypto.subtle;
  }
  if (window.crypto && window.crypto.webkitSubtle) {
    return window.crypto.webkitSubtle;
  }
  if (window.msCrypto && window.msCrypto.subtle) {
    return window.msCrypto.subtle;
  }
  return null;
}

function requireSubtleCrypto() {
  const subtleCrypto = resolveSubtleCrypto();
  if (!subtleCrypto) {
    throw new Error(WEB_CRYPTO_ERROR);
  }
  return subtleCrypto;
}

function bufferToBase64(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = "";
  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return btoa(binary);
}

async function sha256Hex(buffer) {
  const subtleCrypto = requireSubtleCrypto();
  const digest = await subtleCrypto.digest("SHA-256", buffer);
  const bytes = new Uint8Array(digest);
  return Array.from(bytes)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("")
    .toUpperCase();
}

function showMessage(element, text, isError = false) {
  if (!element) {
    return;
  }
  element.textContent = text;
  element.hidden = !text;
  element.classList.toggle("helper-error", isError);
}

function normalizeUsername(value) {
  return (value || "").trim().toLowerCase();
}

function updateLobbyStatus(status, code, fingerprint, message) {
  if (!elements.lobbyStatus) {
    return;
  }
  elements.lobbyStatus.hidden = false;
  if (elements.statusText) {
    elements.statusText.textContent = status;
  }
  if (elements.statusCode) {
    elements.statusCode.textContent = code || "------";
  }
  if (elements.statusFingerprint) {
    elements.statusFingerprint.textContent = fingerprint || "";
  }
  showMessage(elements.statusMessage, message || "");
}

async function generateKeypair() {
  const subtleCrypto = requireSubtleCrypto();
  const keyPair = await subtleCrypto.generateKey(
    {
      name: "ECDSA",
      namedCurve: "P-256",
    },
    true,
    ["sign", "verify"]
  );

  const publicKeySpki = await subtleCrypto.exportKey("spki", keyPair.publicKey);
  const privateKeyJwk = await subtleCrypto.exportKey("jwk", keyPair.privateKey);
  const fingerprint = await sha256Hex(publicKeySpki);

  localStorage.setItem(STORAGE_KEYS.publicKey, bufferToBase64(publicKeySpki));
  localStorage.setItem(STORAGE_KEYS.privateKey, JSON.stringify(privateKeyJwk));
  localStorage.setItem(STORAGE_KEYS.fingerprint, fingerprint);

  return {
    publicKey: localStorage.getItem(STORAGE_KEYS.publicKey),
    privateKey: privateKeyJwk,
    fingerprint,
  };
}

async function importPrivateKey() {
  const subtleCrypto = requireSubtleCrypto();
  const stored = localStorage.getItem(STORAGE_KEYS.privateKey);
  if (!stored) {
    return null;
  }
  const jwk = JSON.parse(stored);
  return subtleCrypto.importKey(
    "jwk",
    jwk,
    { name: "ECDSA", namedCurve: "P-256" },
    false,
    ["sign"]
  );
}

async function signChallenge(challenge) {
  const subtleCrypto = requireSubtleCrypto();
  const privateKey = await importPrivateKey();
  if (!privateKey) {
    throw new Error("Private key missing");
  }
  const signature = await subtleCrypto.sign(
    { name: "ECDSA", hash: "SHA-256" },
    privateKey,
    textEncoder.encode(challenge)
  );
  return bufferToBase64(signature);
}

async function registerAccess(username, magicToken = null) {
  showMessage(elements.requestMessage, "Generating keypair...", false);

  let publicKey = localStorage.getItem(STORAGE_KEYS.publicKey);
  let fingerprint = localStorage.getItem(STORAGE_KEYS.fingerprint);
  if (!publicKey || !fingerprint) {
    const keyInfo = await generateKeypair();
    publicKey = keyInfo.publicKey;
    fingerprint = keyInfo.fingerprint;
  }

  localStorage.setItem(STORAGE_KEYS.username, username);

  const response = await fetch("/api/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username,
      public_key: publicKey,
      public_key_format: "spki",
      magic_token: magicToken,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to request access");
  }

  const data = await response.json();
  localStorage.setItem(STORAGE_KEYS.requestId, data.request_id);
  localStorage.setItem(STORAGE_KEYS.code, data.code);

  updateLobbyStatus(data.status, data.code, data.fingerprint, "Signing verification challenge...");

  const signature = await signChallenge(data.challenge);
  const verifyResponse = await fetch("/api/auth/verify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      request_id: data.request_id,
      signature,
    }),
  });

  if (!verifyResponse.ok) {
    const error = await verifyResponse.json().catch(() => ({}));
    throw new Error(error.detail || "Verification failed");
  }

  const verified = await verifyResponse.json();
  updateLobbyStatus(
    verified.status,
    verified.code,
    verified.fingerprint,
    "Waiting for approval..."
  );
  startStatusPolling();
}

function clearMagicTokenFromUrl() {
  const url = new URL(window.location.href);
  if (!url.searchParams.has(MAGIC_TOKEN_PARAM)) {
    return;
  }
  url.searchParams.delete(MAGIC_TOKEN_PARAM);
  const nextSearch = url.searchParams.toString();
  const nextUrl = `${url.pathname}${nextSearch ? `?${nextSearch}` : ""}${url.hash || ""}`;
  window.history.replaceState({}, document.title, nextUrl);
}

function magicTokenFailureMessage(status) {
  if (status === "expired") {
    return "This magic link has expired. Ask an admin to issue a new one.";
  }
  if (status === "revoked") {
    return "This magic link was revoked. Ask an admin for a replacement link.";
  }
  if (status === "used") {
    return "This magic link was already used. Ask an admin for a new link.";
  }
  return "This magic link is invalid. Ask an admin to resend it.";
}

async function bootstrapMagicLink(token) {
  const response = await fetch(
    `/api/auth/magic-links/bootstrap?token=${encodeURIComponent(token)}`
  );
  if (!response.ok) {
    throw new Error("Failed to validate magic link.");
  }
  return response.json();
}

async function startMagicLinkFlow(token) {
  if (!elements.usernameInput || !elements.requestButton) {
    return;
  }
  showMessage(elements.requestMessage, "Validating magic link...");
  const data = await bootstrapMagicLink(token);
  if (data.status !== "usable") {
    showMessage(elements.requestMessage, magicTokenFailureMessage(data.status), true);
    return;
  }

  const username = (data.configured_username || "").trim();
  if (!username) {
    showMessage(elements.requestMessage, "Magic link is missing a configured username.", true);
    return;
  }

  elements.usernameInput.value = username;
  elements.usernameInput.readOnly = true;
  elements.requestButton.disabled = true;
  try {
    await registerAccess(username, token);
    showMessage(elements.requestMessage, "Magic link request submitted.");
  } catch (error) {
    showMessage(elements.requestMessage, error.message || "Magic link request failed.", true);
  } finally {
    elements.requestButton.disabled = false;
  }
}

async function fetchStatus() {
  const requestId = localStorage.getItem(STORAGE_KEYS.requestId);
  if (!requestId) {
    return;
  }
  const response = await fetch(`/api/auth/status/${requestId}`);
  if (!response.ok) {
    return;
  }
  const data = await response.json();
  let message = "";
  if (data.status === "verifying") {
    message = "Verifying key ownership...";
  } else if (data.status === "pending") {
    message = "Waiting for approval...";
  } else if (data.status === "approved") {
    message = "Approved. Restoring session...";
  } else if (data.status === "rejected") {
    message = "Access was rejected.";
  }
  updateLobbyStatus(data.status, data.code, data.fingerprint, message);

  if (data.status === "approved") {
    const meResponse = await fetch("/api/auth/me");
    if (meResponse.ok) {
      clearPendingRequest();
      stopStatusPolling();
      if (elements.requestPanel) {
        elements.requestPanel.hidden = true;
      }
      updateLobbyStatus(
        "approved",
        null,
        data.fingerprint,
        "You are approved and signed in."
      );
      return;
    }
    await restoreSession();
    return;
  }
  if (data.status === "rejected") {
    showMessage(elements.statusMessage, "Access was rejected. You can request again.", true);
  }
}

function startStatusPolling() {
  if (statusPoller) {
    clearInterval(statusPoller);
  }
  statusPoller = setInterval(fetchStatus, 5000);
  fetchStatus();
}

function stopStatusPolling() {
  if (statusPoller) {
    clearInterval(statusPoller);
    statusPoller = null;
  }
}

function clearPendingRequest() {
  localStorage.removeItem(STORAGE_KEYS.requestId);
  localStorage.removeItem(STORAGE_KEYS.code);
}

async function restoreSession() {
  try {
    const publicKey = localStorage.getItem(STORAGE_KEYS.publicKey);
    if (!publicKey) {
      return;
    }
    const challengeResponse = await fetch("/api/auth/session/challenge");
    if (!challengeResponse.ok) {
      return;
    }
    const { challenge } = await challengeResponse.json();
    const signature = await signChallenge(challenge);

    const response = await fetch("/api/auth/session/restore", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        public_key: publicKey,
        public_key_format: "spki",
        signature,
        challenge,
      }),
    });

    if (response.ok) {
      window.location.href = "/";
    } else {
      showMessage(elements.statusMessage, "Approved, but failed to restore session.", true);
    }
  } catch (error) {
    showMessage(elements.statusMessage, error.message || "Failed to restore session.", true);
  }
}

async function loadApprovals() {
  const response = await fetch("/api/auth/lobby");
  if (!response.ok) {
    return;
  }
  const data = await response.json();
  elements.approvalPanel.hidden = false;
  await loadCurrentUser();
  renderApprovalEntries(data.entries || []);
}

async function loadCurrentUser() {
  const response = await fetch("/api/auth/me");
  if (!response.ok) {
    return;
  }
  const data = await response.json();
  if (data.account && elements.usernameUpdate) {
    currentUsername = data.account.username || "";
    elements.usernameUpdate.value = currentUsername;
  }
  if (elements.requestPanel) {
    elements.requestPanel.hidden = true;
  }
}

function renderApprovalEntries(entries) {
  if (!elements.approvalList) {
    return;
  }
  elements.approvalList.innerHTML = "";
  if (!entries.length) {
    const empty = document.createElement("p");
    empty.className = "helper-text";
    empty.textContent = "No pending requests.";
    elements.approvalList.appendChild(empty);
    return;
  }
  entries.forEach((entry) => {
    const card = document.createElement("div");
    card.className = "approval-card";

    const header = document.createElement("div");
    header.className = "approval-header";
    header.innerHTML = `
      <div>
        <p class="field-label">${entry.requested_username}</p>
        <p class="mono">${entry.fingerprint}</p>
      </div>
      <div class="code">${entry.code}</div>
    `;

    const actions = document.createElement("div");
    actions.className = "link-button-group";

    const approveButton = document.createElement("button");
    approveButton.className = "link-button";
    approveButton.type = "button";
    approveButton.textContent = "Approve";
    approveButton.addEventListener("click", () => handleDecision(entry.request_id, false));

    const rejectButton = document.createElement("button");
    rejectButton.className = "link-button danger";
    rejectButton.type = "button";
    rejectButton.textContent = "Reject";
    rejectButton.addEventListener("click", () => handleReject(entry.request_id));

    actions.appendChild(approveButton);
    if (
      normalizeUsername(currentUsername) &&
      normalizeUsername(currentUsername) === normalizeUsername(entry.requested_username)
    ) {
      const linkButton = document.createElement("button");
      linkButton.className = "link-button";
      linkButton.type = "button";
      linkButton.textContent = "Approve + link to me";
      linkButton.addEventListener("click", () => handleDecision(entry.request_id, true));
      actions.appendChild(linkButton);
    }
    actions.appendChild(rejectButton);

    card.appendChild(header);
    card.appendChild(actions);
    elements.approvalList.appendChild(card);
  });
}

async function handleDecision(requestId, linkToSelf) {
  await fetch(`/api/auth/lobby/${requestId}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ link_to_self: linkToSelf }),
  });
  loadApprovals();
}

async function handleReject(requestId) {
  await fetch(`/api/auth/lobby/${requestId}/reject`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  loadApprovals();
}

async function handleUsernameUpdate() {
  const username = elements.usernameUpdate.value.trim();
  if (!username) {
    showMessage(elements.usernameMessage, "Enter a display name.", true);
    return;
  }
  const response = await fetch("/api/auth/username", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username }),
  });
  if (!response.ok) {
    showMessage(elements.usernameMessage, "Failed to update name.", true);
    return;
  }
  const data = await response.json();
  localStorage.setItem(STORAGE_KEYS.username, data.username);
  showMessage(elements.usernameMessage, "Display name updated.");
}

function init() {
  const wireEnterToButton = (inputEl, buttonEl) => {
    if (!inputEl || !buttonEl) {
      return;
    }
    inputEl.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        buttonEl.click();
      }
    });
  };

  if (elements.requestButton) {
    if (!resolveSubtleCrypto()) {
      elements.requestButton.disabled = true;
      showMessage(elements.requestMessage, WEB_CRYPTO_ERROR, true);
    }
    elements.requestButton.addEventListener("click", async () => {
      try {
        const username = elements.usernameInput.value.trim();
        if (!username) {
          showMessage(elements.requestMessage, "Please enter a display name.", true);
          return;
        }
        elements.requestButton.disabled = true;
        await registerAccess(username);
        showMessage(elements.requestMessage, "Request submitted.");
      } catch (error) {
        showMessage(elements.requestMessage, error.message || "Request failed.", true);
      } finally {
        elements.requestButton.disabled = false;
      }
    });
  }

  if (elements.usernameSave) {
    elements.usernameSave.addEventListener("click", handleUsernameUpdate);
  }
  wireEnterToButton(elements.usernameInput, elements.requestButton);
  wireEnterToButton(elements.usernameUpdate, elements.usernameSave);

  const storedUsername = localStorage.getItem(STORAGE_KEYS.username);
  if (storedUsername && elements.usernameInput) {
    elements.usernameInput.value = storedUsername;
  }

  if (localStorage.getItem(STORAGE_KEYS.requestId)) {
    elements.lobbyStatus.hidden = false;
    startStatusPolling();
  }

  const params = new URLSearchParams(window.location.search);
  const magicToken = (params.get(MAGIC_TOKEN_PARAM) || "").trim();
  if (magicToken) {
    clearPendingRequest();
    stopStatusPolling();
    clearMagicTokenFromUrl();
    if (!resolveSubtleCrypto()) {
      showMessage(elements.requestMessage, WEB_CRYPTO_ERROR, true);
    } else {
      startMagicLinkFlow(magicToken).catch((error) => {
        showMessage(elements.requestMessage, error.message || "Magic link request failed.", true);
      });
    }
  }

  loadApprovals();
}

init();
