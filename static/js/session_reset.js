const STORAGE_KEYS = {
  publicKey: "auth_public_key_spki",
  privateKey: "auth_private_key_jwk",
};

const messageEl = document.getElementById("reset-message");
const guidanceEl = document.getElementById("reset-guidance");
const retryButton = document.getElementById("reset-retry");
const encoder = new TextEncoder();
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

function showMessage(text, isError = false) {
  if (!messageEl) {
    return;
  }
  messageEl.textContent = text;
  messageEl.classList.toggle("helper-error", isError);
}

function showLoggedOutGuidance() {
  if (!guidanceEl) {
    return;
  }
  guidanceEl.hidden = false;
}

function hideLoggedOutGuidance() {
  if (!guidanceEl) {
    return;
  }
  guidanceEl.hidden = true;
}

function showNotLoggedInState(details = "") {
  const message = details
    ? `You are not logged in. ${details}`
    : "You are not logged in.";
  showMessage(message, true);
  showLoggedOutGuidance();
}

function resolveNextPath() {
  const nextSource = document.querySelector("[data-reset-next]");
  const candidate = (nextSource?.dataset?.resetNext || "").trim();
  if (!candidate || !candidate.startsWith("/") || candidate.startsWith("//")) {
    return "/";
  }
  if (candidate === "/lobby" || candidate.startsWith("/lobby?")) {
    return "/";
  }
  return candidate;
}

function bufferToBase64(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = "";
  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return btoa(binary);
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
    throw new Error("Missing keypair");
  }
  const signature = await subtleCrypto.sign(
    { name: "ECDSA", hash: "SHA-256" },
    privateKey,
    encoder.encode(challenge)
  );
  return bufferToBase64(signature);
}

async function restoreSession() {
  hideLoggedOutGuidance();
  try {
    const nextPath = resolveNextPath();
    const publicKey = localStorage.getItem(STORAGE_KEYS.publicKey);
    if (!publicKey) {
      showNotLoggedInState("Use your magic link to log in.");
      return;
    }

    showMessage("Restoring session...");
    const challengeResponse = await fetch("/api/auth/session/challenge");
    if (!challengeResponse.ok) {
      showNotLoggedInState("Use your magic link to log in.");
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
      window.location.href = nextPath;
    } else {
      showNotLoggedInState("Use your magic link to log in.");
    }
  } catch (error) {
    showNotLoggedInState(error.message || "Use your magic link to log in.");
  }
}

if (retryButton) {
  if (!resolveSubtleCrypto()) {
    retryButton.disabled = true;
  }
  retryButton.addEventListener("click", restoreSession);
}

restoreSession();
