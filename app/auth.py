from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from dataclasses import dataclass
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
from fastapi import Request, Response

from app import db

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_PATH = BASE_DIR / "data" / "auth_secret.txt"
COOKIE_NAME = "penelope_session"
SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 365 * 10


def _session_cookie_secure() -> bool:
    return os.getenv("SESSION_COOKIE_SECURE", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _session_cookie_domain() -> str | None:
    return os.getenv("SESSION_COOKIE_DOMAIN", "").strip() or None


def _parse_csv_env(name: str) -> list[str]:
    raw_value = os.getenv(name, "")
    return [entry.strip().lower() for entry in raw_value.split(",") if entry.strip()]


@dataclass
class SessionInfo:
    account_id: int
    username: str


def _load_secret() -> bytes:
    env_secret = os.getenv("AUTH_SECRET")
    if env_secret:
        return env_secret.encode("utf-8")
    if SECRET_PATH.exists():
        return SECRET_PATH.read_text().strip().encode("utf-8")
    SECRET_PATH.parent.mkdir(parents=True, exist_ok=True)
    secret = secrets.token_urlsafe(32)
    SECRET_PATH.write_text(secret)
    return secret.encode("utf-8")


def _sign_value(value: str) -> str:
    secret = _load_secret()
    signature = hmac.new(secret, value.encode("utf-8"), hashlib.sha256).hexdigest()
    return signature


def _encode_cookie(account_id: int) -> str:
    value = str(account_id)
    signature = _sign_value(value)
    return f"{value}.{signature}"


def _decode_cookie(cookie_value: str) -> int | None:
    if not cookie_value or "." not in cookie_value:
        return None
    value, signature = cookie_value.split(".", 1)
    expected = _sign_value(value)
    if not hmac.compare_digest(signature, expected):
        return None
    if not value.isdigit():
        return None
    return int(value)


def set_session_cookie(response: Response, account_id: int) -> None:
    cookie_domain = _session_cookie_domain()
    response.set_cookie(
        COOKIE_NAME,
        _encode_cookie(account_id),
        httponly=True,
        samesite="Lax",
        max_age=SESSION_MAX_AGE_SECONDS,
        secure=_session_cookie_secure(),
        domain=cookie_domain,
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME, domain=_session_cookie_domain(), path="/")


def get_session_account(request: Request) -> SessionInfo | None:
    cookie_value = request.cookies.get(COOKIE_NAME)
    account_id = _decode_cookie(cookie_value) if cookie_value else None
    if not account_id:
        return None
    account = db.get_account(account_id)
    if not account:
        return None
    return SessionInfo(account_id=account["id"], username=account["username"])


def issue_stateless_challenge(ttl_seconds: int = 600) -> str:
    issued_at = int(time.time())
    expires_at = issued_at + ttl_seconds
    nonce = secrets.token_urlsafe(16)
    payload = f"{issued_at}.{expires_at}.{nonce}"
    signature = _sign_value(payload)
    return f"{payload}.{signature}"


def verify_stateless_challenge(token: str) -> bool:
    parts = token.split(".")
    if len(parts) < 4:
        return False
    payload = ".".join(parts[:-1])
    signature = parts[-1]
    expected = _sign_value(payload)
    if not hmac.compare_digest(signature, expected):
        return False
    try:
        issued_at = int(parts[0])
        expires_at = int(parts[1])
    except ValueError:
        return False
    now = int(time.time())
    if now < issued_at or now > expires_at:
        return False
    return True


def load_public_key(public_key: str, public_key_format: str):
    if public_key_format.lower() != "spki":
        raise ValueError("Unsupported public key format")
    key_bytes = base64.b64decode(public_key.encode("utf-8"))
    return serialization.load_der_public_key(key_bytes)


def fingerprint_public_key(public_key: str, public_key_format: str) -> str:
    if public_key_format.lower() != "spki":
        raise ValueError("Unsupported public key format")
    key_bytes = base64.b64decode(public_key.encode("utf-8"))
    return hashlib.sha256(key_bytes).hexdigest().upper()


def _decode_signature(signature_b64: str) -> bytes:
    return base64.b64decode(signature_b64.encode("utf-8"))


def _raw_ecdsa_signature_to_der(raw_signature: bytes) -> bytes:
    if len(raw_signature) % 2 != 0:
        raise ValueError("Invalid ECDSA signature length")
    half = len(raw_signature) // 2
    r = int.from_bytes(raw_signature[:half], byteorder="big")
    s = int.from_bytes(raw_signature[half:], byteorder="big")
    return encode_dss_signature(r, s)


def verify_signature(
    public_key: str,
    public_key_format: str,
    signature_b64: str,
    challenge: str,
) -> bool:
    public_key_obj = load_public_key(public_key, public_key_format)
    signature = _decode_signature(signature_b64)
    challenge_bytes = challenge.encode("utf-8")
    if isinstance(public_key_obj, ec.EllipticCurvePublicKey):
        try:
            if len(signature) == 64:
                signature = _raw_ecdsa_signature_to_der(signature)
            public_key_obj.verify(signature, challenge_bytes, ec.ECDSA(hashes.SHA256()))
            return True
        except Exception:
            return False
    raise ValueError("Unsupported public key type")


def parse_public_key_payload(payload: str) -> tuple[str, str]:
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError:
        return payload, "spki"
    if isinstance(parsed, dict) and "value" in parsed and "format" in parsed:
        return parsed["value"], parsed["format"]
    return payload, "spki"


def hash_magic_login_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def is_admin_account(account_id: int) -> bool:
    account = db.get_account(account_id)
    if not account:
        return False
    admin_usernames = _parse_csv_env("MAGIC_LINK_ADMIN_USERNAMES")
    if not admin_usernames:
        return True
    return (account.get("username") or "").strip().lower() in admin_usernames
