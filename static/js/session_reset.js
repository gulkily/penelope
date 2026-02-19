const STORAGE_KEYS = {
  publicKey: "auth_public_key_spki",
  privateKey: "auth_private_key_jwk",
};

const encoder = new TextEncoder();
const RESET_FALLBACK_REDIRECT_MS = 8000;

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
    throw new Error("Secure cryptography unavailable");
  }
  return subtleCrypto;
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

function redirectToWelcome() {
  window.location.replace("/welcome");
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
  let completed = false;
  const fallbackTimer = window.setTimeout(() => {
    if (!completed) {
      redirectToWelcome();
    }
  }, RESET_FALLBACK_REDIRECT_MS);
  const finish = (action) => {
    if (completed) {
      return;
    }
    completed = true;
    window.clearTimeout(fallbackTimer);
    action();
  };

  try {
    const nextPath = resolveNextPath();
    const publicKey = localStorage.getItem(STORAGE_KEYS.publicKey);
    if (!publicKey) {
      finish(redirectToWelcome);
      return;
    }

    const challengeResponse = await fetch("/api/auth/session/challenge");
    if (!challengeResponse.ok) {
      finish(redirectToWelcome);
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
      finish(() => {
        window.location.replace(nextPath);
      });
      return;
    }
    finish(redirectToWelcome);
  } catch (_error) {
    finish(redirectToWelcome);
  }
}

restoreSession();
