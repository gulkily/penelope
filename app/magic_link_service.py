from __future__ import annotations

import secrets
from urllib.parse import quote

from app import auth
from app import db


def build_magic_link(base_url: str, token: str) -> str:
    base = (base_url or "").strip()
    if not base:
        raise ValueError("Base URL is required to build magic links.")
    return f"{base.rstrip('/')}/lobby?token={quote(token)}"


def issue_magic_link(
    configured_username: str,
    issuer_account_id: int,
    base_url: str,
) -> dict:
    username = configured_username.strip()
    if not username:
        raise ValueError("Configured username required")
    if issuer_account_id <= 0:
        raise ValueError("Issuer account id must be a positive integer.")

    token = secrets.token_urlsafe(32)
    token_hash = auth.hash_magic_login_token(token)
    token_row = db.create_magic_login_token(
        configured_username=username,
        created_by_account_id=issuer_account_id,
        expires_at="",
        token_hash=token_hash,
    )
    db.append_ledger_event(
        "magic_link_issued",
        actor_account_id=issuer_account_id,
        subject_account_id=None,
        metadata={
            "token_id": token_row["id"],
            "configured_username": username,
        },
    )
    return {
        "token_id": token_row["id"],
        "configured_username": username,
        "magic_link": build_magic_link(base_url=base_url, token=token),
        "expires_at": None,
    }
