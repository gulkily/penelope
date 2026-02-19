import json
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Request, Response

from app import db
from app import auth
from app.feature_flags import get_feature_flags
from app.schemas import (
    AuthRegisterRequest,
    AuthRegisterResponse,
    AuthStatusResponse,
    AuthVerifyRequest,
    LobbyDecisionRequest,
    LobbyDecisionResponse,
    LobbyListResponse,
    MagicLinkBootstrapResponse,
    MagicLinkCreateRequest,
    MagicLinkCreateResponse,
    MagicLinkListResponse,
    MagicLinkRevokeResponse,
    SessionRestoreInitResponse,
    SessionRestoreRequest,
    UsernameUpdateRequest,
)

router = APIRouter()

CODE_TTL_DAYS = 14
CHALLENGE_TTL_SECONDS = 60 * 60 * 24


def _require_session(request: Request) -> auth.SessionInfo:
    session = auth.get_session_account(request)
    if not session:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return session


def _require_admin(request: Request) -> auth.SessionInfo:
    session = _require_session(request)
    if not auth.is_admin_account(session.account_id):
        raise HTTPException(status_code=403, detail="Admin access required")
    return session


def _require_lobby_auth_enabled() -> None:
    if not get_feature_flags().lobby_auth_enabled:
        raise HTTPException(status_code=503, detail="Lobby authentication is disabled")


def _is_magic_link_request(request_row: dict | None) -> bool:
    return bool(request_row and request_row.get("magic_token_id"))


def _require_lobby_auth_for_request(request_row: dict | None) -> None:
    if get_feature_flags().lobby_auth_enabled or _is_magic_link_request(request_row):
        return
    raise HTTPException(status_code=503, detail="Lobby authentication is disabled")


def _build_magic_link(request: Request, token: str) -> str:
    base = str(request.base_url).rstrip("/")
    return f"{base}/lobby?token={quote(token)}"


def _classify_magic_token(token_row: dict) -> str:
    if not token_row:
        return "invalid"
    if token_row.get("revoked_at"):
        return "revoked"
    return "usable"


@router.post("/auth/magic-links", response_model=MagicLinkCreateResponse)
def issue_magic_link(payload: MagicLinkCreateRequest, request: Request) -> dict:
    session = _require_admin(request)
    configured_username = payload.configured_username.strip()
    if not configured_username:
        raise HTTPException(status_code=400, detail="Configured username required")

    token = secrets.token_urlsafe(32)
    token_hash = auth.hash_magic_login_token(token)

    token_row = db.create_magic_login_token(
        configured_username=configured_username,
        created_by_account_id=session.account_id,
        expires_at="",
        token_hash=token_hash,
    )
    db.append_ledger_event(
        "magic_link_issued",
        actor_account_id=session.account_id,
        subject_account_id=None,
        metadata={
            "token_id": token_row["id"],
            "configured_username": configured_username,
        },
    )
    return {
        "token_id": token_row["id"],
        "configured_username": configured_username,
        "magic_link": _build_magic_link(request, token),
        "expires_at": None,
    }


@router.get("/auth/magic-links", response_model=MagicLinkListResponse)
def list_magic_links(request: Request, limit: int = 200) -> dict:
    _require_admin(request)
    entries = db.list_active_magic_login_tokens(limit=limit)
    return {
        "entries": [
            {
                "token_id": entry["id"],
                "configured_username": entry["configured_username"],
                "created_at": entry["created_at"],
                "created_by_account_id": entry["created_by_account_id"],
                "created_by_username": entry.get("created_by_username"),
            }
            for entry in entries
        ]
    }


@router.post("/auth/magic-links/{token_id}/revoke", response_model=MagicLinkRevokeResponse)
def revoke_magic_link(token_id: str, request: Request) -> dict:
    session = _require_admin(request)
    try:
        token_row = db.mark_magic_login_token_revoked(token_id, session.account_id)
    except ValueError as exc:
        message = str(exc)
        if "not found" in message:
            raise HTTPException(status_code=404, detail=message) from exc
        raise HTTPException(status_code=400, detail=message) from exc

    db.append_ledger_event(
        "magic_link_revoked",
        actor_account_id=session.account_id,
        subject_account_id=None,
        metadata={"token_id": token_row["id"]},
    )
    return {"token_id": token_row["id"], "status": "revoked"}


@router.get("/auth/magic-links/bootstrap", response_model=MagicLinkBootstrapResponse)
def bootstrap_magic_link(token: str = "") -> dict:
    candidate = token.strip()
    if not candidate:
        return {"status": "invalid", "configured_username": None}

    token_hash = auth.hash_magic_login_token(candidate)
    token_row = db.get_magic_login_token_by_hash(token_hash)
    status = _classify_magic_token(token_row)
    if status != "usable":
        db.append_ledger_event(
            "magic_link_bootstrap_blocked",
            actor_account_id=None,
            subject_account_id=None,
            metadata={
                "status": status,
                "token_id": token_row.get("id") if token_row else None,
            },
        )
        return {"status": status, "configured_username": None}

    return {"status": "usable", "configured_username": token_row["configured_username"]}


@router.post("/auth/register", response_model=AuthRegisterResponse)
def register(payload: AuthRegisterRequest) -> dict:
    public_key = payload.public_key.strip()
    if not public_key:
        raise HTTPException(status_code=400, detail="Public key required")
    username = payload.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username required")
    token = (payload.token or "").strip()
    if not token and not get_feature_flags().lobby_auth_enabled:
        raise HTTPException(status_code=503, detail="Lobby authentication is disabled")
    magic_token_id = None
    if token:
        token_hash = auth.hash_magic_login_token(token)
        token_row = db.get_magic_login_token_by_hash(token_hash)
        token_status = _classify_magic_token(token_row)
        if token_status != "usable":
            raise HTTPException(status_code=400, detail=f"Magic link {token_status}")
        magic_token_id = token_row["id"]
        username = token_row["configured_username"]

    public_key_format = payload.public_key_format or "spki"
    try:
        fingerprint = auth.fingerprint_public_key(public_key, public_key_format)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    key_row = db.add_public_key(None, public_key, public_key_format, fingerprint)

    code = f"{secrets.randbelow(1_000_000):06d}"
    expires_at = (datetime.now(timezone.utc) + timedelta(days=CODE_TTL_DAYS)).isoformat()
    challenge = auth.issue_stateless_challenge(CHALLENGE_TTL_SECONDS)

    request_row = db.create_lobby_request(
        public_key_id=key_row["id"],
        requested_username=username,
        code=code,
        expires_at=expires_at,
        challenge=challenge,
        magic_token_id=magic_token_id,
    )
    db.append_ledger_event(
        "lobby_requested",
        actor_account_id=None,
        subject_account_id=None,
        metadata={
            "request_id": request_row["request_id"],
            "fingerprint": fingerprint,
            "username": username,
            "magic_token_id": magic_token_id,
        },
    )
    return {
        "request_id": request_row["request_id"],
        "fingerprint": fingerprint,
        "code": code,
        "challenge": challenge,
        "expires_at": expires_at,
        "status": request_row["status"],
    }


@router.post("/auth/verify")
def verify_request(payload: AuthVerifyRequest) -> AuthStatusResponse:
    request_row = db.get_lobby_request(payload.request_id)
    if not request_row:
        raise HTTPException(status_code=404, detail="Request not found")
    _require_lobby_auth_for_request(request_row)
    if request_row["status"] != "verifying":
        raise HTTPException(status_code=400, detail="Request not in verifying state")
    if not auth.verify_stateless_challenge(request_row["challenge"]):
        raise HTTPException(status_code=400, detail="Challenge expired")

    public_key_row = db.get_public_key(request_row["public_key_id"])
    if not public_key_row:
        raise HTTPException(status_code=404, detail="Public key not found")

    try:
        is_valid = auth.verify_signature(
            public_key_row["public_key"],
            public_key_row["public_key_format"],
            payload.signature,
            request_row["challenge"],
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid signature")

    request_row = db.mark_lobby_request_verified(request_row["request_id"])
    db.append_ledger_event(
        "lobby_verified",
        actor_account_id=None,
        subject_account_id=None,
        metadata={"request_id": request_row["request_id"]},
    )
    if request_row.get("magic_token_id"):
        try:
            approved = db.approve_lobby_request_with_magic_token(request_row["request_id"])
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        db.append_ledger_event(
            "magic_link_auto_approved",
            actor_account_id=None,
            subject_account_id=approved.get("account_id"),
            metadata={
                "request_id": request_row["request_id"],
                "magic_token_id": request_row["magic_token_id"],
            },
        )
        return AuthStatusResponse(
            request_id=request_row["request_id"],
            status="approved",
            code=None,
            fingerprint=public_key_row["fingerprint"],
        )
    if db.count_accounts() == 0:
        approved = db.approve_lobby_request(
            request_id=request_row["request_id"],
            approved_by_account_id=None,
            link_to_account_id=None,
        )
        db.append_ledger_event(
            "lobby_bootstrap_approved",
            actor_account_id=None,
            subject_account_id=approved.get("account_id"),
            metadata={"request_id": request_row["request_id"]},
        )
        return AuthStatusResponse(
            request_id=request_row["request_id"],
            status="approved",
            code=None,
            fingerprint=public_key_row["fingerprint"],
        )
    return AuthStatusResponse(
        request_id=request_row["request_id"],
        status=request_row["status"],
        code=request_row["code"],
        fingerprint=public_key_row["fingerprint"],
    )


@router.get("/auth/status/{request_id}", response_model=AuthStatusResponse)
def get_status(request_id: str) -> dict:
    request_row = db.get_lobby_request(request_id)
    if not request_row:
        raise HTTPException(status_code=404, detail="Request not found")
    _require_lobby_auth_for_request(request_row)
    public_key_row = db.get_public_key(request_row["public_key_id"])
    fingerprint = public_key_row.get("fingerprint") if public_key_row else ""
    code = request_row["code"] if request_row["status"] in ("pending", "verifying") else None
    return {
        "request_id": request_row["request_id"],
        "status": request_row["status"],
        "code": code,
        "fingerprint": fingerprint,
    }


@router.get("/auth/lobby", response_model=LobbyListResponse)
def list_lobby(request: Request) -> dict:
    _require_lobby_auth_enabled()
    _require_session(request)
    entries = db.list_pending_lobby_requests()
    return {"entries": entries}


@router.get("/auth/me")
def auth_me(request: Request) -> dict:
    session = _require_session(request)
    account = db.get_account(session.account_id)
    return {"account": {"id": account["id"], "username": account["username"]}}


@router.post("/auth/lobby/{request_id}/approve", response_model=LobbyDecisionResponse)
def approve_lobby(
    request_id: str,
    payload: LobbyDecisionRequest,
    request: Request,
) -> dict:
    _require_lobby_auth_enabled()
    session = _require_session(request)
    link_account_id = session.account_id if payload.link_to_self else None
    approved = db.approve_lobby_request(
        request_id=request_id,
        approved_by_account_id=session.account_id,
        link_to_account_id=link_account_id,
    )
    db.append_ledger_event(
        "lobby_approved",
        actor_account_id=session.account_id,
        subject_account_id=approved.get("account_id"),
        metadata={"request_id": request_id},
    )
    return {
        "request_id": request_id,
        "status": "approved",
        "account_id": approved.get("account_id"),
    }


@router.post("/auth/lobby/{request_id}/reject", response_model=LobbyDecisionResponse)
def reject_lobby(request_id: str, request: Request) -> dict:
    _require_lobby_auth_enabled()
    session = _require_session(request)
    db.reject_lobby_request(request_id, session.account_id)
    db.append_ledger_event(
        "lobby_rejected",
        actor_account_id=session.account_id,
        subject_account_id=None,
        metadata={"request_id": request_id},
    )
    return {"request_id": request_id, "status": "rejected", "account_id": None}


@router.post("/auth/username")
def update_username(payload: UsernameUpdateRequest, request: Request) -> dict:
    session = _require_session(request)
    updated = db.update_username(session.account_id, payload.username.strip())
    db.append_ledger_event(
        "username_updated",
        actor_account_id=session.account_id,
        subject_account_id=session.account_id,
        metadata={"username": updated["username"]},
    )
    return {"username": updated["username"]}


@router.post("/auth/logout")
def logout(response: Response) -> dict:
    auth.clear_session_cookie(response)
    return {"status": "ok"}


@router.get("/auth/ledger")
def ledger(request: Request, limit: int = 200, offset: int = 0) -> dict:
    _require_session(request)
    limit = max(1, min(limit, 500))
    offset = max(0, offset)
    entries = db.list_ledger_events(limit=limit, offset=offset)
    total = db.count_ledger_events()
    for entry in entries:
        raw_metadata = entry.get("metadata") or "{}"
        try:
            entry["metadata"] = json.loads(raw_metadata)
        except json.JSONDecodeError:
            entry["metadata"] = {"raw": raw_metadata}
    return {"entries": entries, "total": total, "limit": limit, "offset": offset}


@router.get("/auth/session/challenge", response_model=SessionRestoreInitResponse)
def session_challenge() -> dict:
    return {"challenge": auth.issue_stateless_challenge()}


@router.post("/auth/session/restore")
def session_restore(payload: SessionRestoreRequest, response: Response) -> dict:
    if not auth.verify_stateless_challenge(payload.challenge):
        raise HTTPException(status_code=400, detail="Challenge expired")

    public_key = payload.public_key.strip()
    public_key_format = payload.public_key_format or "spki"
    try:
        fingerprint = auth.fingerprint_public_key(public_key, public_key_format)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    public_key_row = db.get_public_key_by_fingerprint(fingerprint)
    if not public_key_row or not public_key_row.get("account_id"):
        raise HTTPException(status_code=403, detail="Key not approved")

    try:
        is_valid = auth.verify_signature(
            public_key,
            public_key_format,
            payload.signature,
            payload.challenge,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid signature")

    auth.set_session_cookie(response, public_key_row["account_id"])
    return {"status": "ok"}
