from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from app.db_connection import connect


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row_to_dict(row) -> dict:
    return dict(row) if row else {}


def _resolve_target_account_id(
    conn,
    requested_username: str,
    public_key_account_id: int | None,
    link_to_account_id: int | None = None,
) -> int:
    target_account_id = public_key_account_id
    if link_to_account_id:
        target_account_id = link_to_account_id
    if not target_account_id:
        existing_account = conn.execute(
            """
            SELECT *
            FROM accounts
            WHERE LOWER(TRIM(username)) = LOWER(TRIM(?))
            ORDER BY id ASC
            LIMIT 1
            """,
            (requested_username,),
        ).fetchone()
        if existing_account:
            target_account_id = int(existing_account["id"])
    if target_account_id:
        return target_account_id

    now = _utc_now()
    cursor = conn.execute(
        """
        INSERT INTO accounts (username, created_at, updated_at)
        VALUES (?, ?, ?)
        """,
        (requested_username, now, now),
    )
    return int(cursor.lastrowid)


def create_account(initial_username: str) -> dict:
    now = _utc_now()
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO accounts (username, created_at, updated_at)
            VALUES (?, ?, ?)
            """,
            (initial_username, now, now),
        )
        account_id = cursor.lastrowid
        row = conn.execute(
            "SELECT * FROM accounts WHERE id = ?",
            (account_id,),
        ).fetchone()
        return _row_to_dict(row)


def get_account(account_id: int) -> dict:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM accounts WHERE id = ?",
            (account_id,),
        ).fetchone()
        return _row_to_dict(row)


def get_account_by_username_case_insensitive(username: str) -> dict:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM accounts
            WHERE LOWER(TRIM(username)) = LOWER(TRIM(?))
            ORDER BY id ASC
            LIMIT 1
            """,
            (username,),
        ).fetchone()
        return _row_to_dict(row)


def update_username(account_id: int, new_username: str) -> dict:
    now = _utc_now()
    with connect() as conn:
        conn.execute(
            "UPDATE accounts SET username = ?, updated_at = ? WHERE id = ?",
            (new_username, now, account_id),
        )
        return get_account(account_id)


def count_accounts() -> int:
    with connect() as conn:
        row = conn.execute("SELECT COUNT(*) AS count FROM accounts").fetchone()
        return int(row["count"]) if row else 0


def list_accounts(limit: int = 500, offset: int = 0) -> list[dict]:
    safe_limit = max(1, min(limit, 500))
    safe_offset = max(0, offset)
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT id, username, created_at
            FROM accounts
            ORDER BY LOWER(TRIM(username)) ASC, id ASC
            LIMIT ? OFFSET ?
            """,
            (safe_limit, safe_offset),
        ).fetchall()
        return [dict(row) for row in rows]


def add_public_key(
    account_id: int | None,
    public_key: str,
    public_key_format: str,
    fingerprint: str,
) -> dict:
    now = _utc_now()
    with connect() as conn:
        existing = conn.execute(
            "SELECT * FROM public_keys WHERE fingerprint = ?",
            (fingerprint,),
        ).fetchone()
        if existing:
            if account_id and not existing["account_id"]:
                conn.execute(
                    "UPDATE public_keys SET account_id = ? WHERE id = ?",
                    (account_id, existing["id"]),
                )
            if not existing["public_key_format"]:
                conn.execute(
                    "UPDATE public_keys SET public_key_format = ? WHERE id = ?",
                    (public_key_format, existing["id"]),
                )
            return _row_to_dict(existing)

        cursor = conn.execute(
            """
            INSERT INTO public_keys (account_id, public_key, public_key_format, fingerprint, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (account_id, public_key, public_key_format, fingerprint, now),
        )
        public_key_id = cursor.lastrowid
        row = conn.execute(
            "SELECT * FROM public_keys WHERE id = ?",
            (public_key_id,),
        ).fetchone()
        return _row_to_dict(row)


def get_public_key(public_key_id: int) -> dict:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM public_keys WHERE id = ?",
            (public_key_id,),
        ).fetchone()
        return _row_to_dict(row)


def get_public_key_by_fingerprint(fingerprint: str) -> dict:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM public_keys WHERE fingerprint = ?",
            (fingerprint,),
        ).fetchone()
        return _row_to_dict(row)


def create_lobby_request(
    public_key_id: int,
    requested_username: str,
    code: str,
    expires_at: str,
    challenge: str,
    magic_token_id: str | None = None,
) -> dict:
    now = _utc_now()
    request_id = str(uuid.uuid4())
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO lobby_requests (
                request_id,
                public_key_id,
                requested_username,
                magic_token_id,
                code,
                status,
                requested_at,
                expires_at,
                challenge
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request_id,
                public_key_id,
                requested_username,
                magic_token_id,
                code,
                "verifying",
                now,
                expires_at,
                challenge,
            ),
        )
        row = conn.execute(
            "SELECT * FROM lobby_requests WHERE request_id = ?",
            (request_id,),
        ).fetchone()
        return _row_to_dict(row)


def get_lobby_request(request_id: str) -> dict:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM lobby_requests WHERE request_id = ?",
            (request_id,),
        ).fetchone()
        return _row_to_dict(row)


def create_magic_login_token(
    configured_username: str,
    created_by_account_id: int,
    expires_at: str,
    token_hash: str,
) -> dict:
    now = _utc_now()
    token_id = str(uuid.uuid4())
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO magic_login_tokens (
                id,
                token_hash,
                configured_username,
                created_by_account_id,
                created_at,
                expires_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                token_id,
                token_hash,
                configured_username,
                created_by_account_id,
                now,
                expires_at,
            ),
        )
        row = conn.execute(
            "SELECT * FROM magic_login_tokens WHERE id = ?",
            (token_id,),
        ).fetchone()
        return _row_to_dict(row)


def get_magic_login_token(token_id: str) -> dict:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM magic_login_tokens WHERE id = ?",
            (token_id,),
        ).fetchone()
        return _row_to_dict(row)


def get_magic_login_token_by_hash(token_hash: str) -> dict:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM magic_login_tokens WHERE token_hash = ?",
            (token_hash,),
        ).fetchone()
        return _row_to_dict(row)


def is_magic_login_token_usable(token_id: str) -> bool:
    token_row = get_magic_login_token(token_id)
    if not token_row:
        return False
    return not token_row.get("revoked_at")


def attach_magic_token_to_lobby_request(request_id: str, token_id: str) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE lobby_requests SET magic_token_id = ? WHERE request_id = ?",
            (token_id, request_id),
        )


def consume_magic_login_token(token_id: str, request_id: str, account_id: int) -> dict:
    with connect() as conn:
        token_row = conn.execute(
            "SELECT * FROM magic_login_tokens WHERE id = ?",
            (token_id,),
        ).fetchone()
        if not token_row:
            raise ValueError("Magic token not found")
        if token_row["revoked_at"]:
            raise ValueError("Magic token revoked")
        return _row_to_dict(token_row)


def mark_magic_login_token_revoked(token_id: str, actor_account_id: int) -> dict:
    with connect() as conn:
        token_row = conn.execute(
            "SELECT * FROM magic_login_tokens WHERE id = ?",
            (token_id,),
        ).fetchone()
        if not token_row:
            raise ValueError("Magic token not found")
        if token_row["revoked_at"]:
            return _row_to_dict(token_row)

        now = _utc_now()
        conn.execute(
            """
            UPDATE magic_login_tokens
            SET revoked_at = ?,
                revoked_by_account_id = ?
            WHERE id = ?
            """,
            (now, actor_account_id, token_id),
        )
        row = conn.execute(
            "SELECT * FROM magic_login_tokens WHERE id = ?",
            (token_id,),
        ).fetchone()
        return _row_to_dict(row)


def list_active_magic_login_tokens(limit: int = 200) -> list[dict]:
    safe_limit = max(1, min(limit, 500))
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT
                tokens.id,
                tokens.configured_username,
                tokens.created_at,
                tokens.created_by_account_id,
                creators.username AS created_by_username
            FROM magic_login_tokens AS tokens
            LEFT JOIN accounts AS creators ON creators.id = tokens.created_by_account_id
            WHERE tokens.revoked_at IS NULL
            ORDER BY tokens.created_at DESC, tokens.id DESC
            LIMIT ?
            """,
            (safe_limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def list_pending_lobby_requests() -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT
                lobby_requests.*, public_keys.fingerprint
            FROM lobby_requests
            JOIN public_keys ON public_keys.id = lobby_requests.public_key_id
            WHERE lobby_requests.status = 'pending'
            ORDER BY lobby_requests.requested_at ASC
            """
        ).fetchall()
        return [dict(row) for row in rows]


def link_key_to_account(public_key_id: int, account_id: int) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE public_keys SET account_id = ? WHERE id = ?",
            (account_id, public_key_id),
        )


def approve_lobby_request(
    request_id: str,
    approved_by_account_id: int | None,
    link_to_account_id: int | None,
) -> dict:
    with connect() as conn:
        request_row = conn.execute(
            "SELECT * FROM lobby_requests WHERE request_id = ?",
            (request_id,),
        ).fetchone()
        if not request_row or request_row["status"] != "pending":
            raise ValueError("Lobby request not pending")

        public_key_row = conn.execute(
            "SELECT * FROM public_keys WHERE id = ?",
            (request_row["public_key_id"],),
        ).fetchone()
        if not public_key_row:
            raise ValueError("Public key not found")

        target_account_id = _resolve_target_account_id(
            conn=conn,
            requested_username=request_row["requested_username"],
            public_key_account_id=public_key_row["account_id"],
            link_to_account_id=link_to_account_id,
        )

        conn.execute(
            "UPDATE public_keys SET account_id = ? WHERE id = ?",
            (target_account_id, public_key_row["id"]),
        )
        now = _utc_now()
        conn.execute(
            """
            UPDATE lobby_requests
            SET status = 'approved',
                approved_by = ?,
                approved_at = ?,
                account_id = ?
            WHERE request_id = ?
            """,
            (approved_by_account_id, now, target_account_id, request_id),
        )
        return _row_to_dict(
            conn.execute(
                "SELECT * FROM lobby_requests WHERE request_id = ?",
                (request_id,),
            ).fetchone()
        )


def approve_lobby_request_with_magic_token(request_id: str) -> dict:
    with connect() as conn:
        request_row = conn.execute(
            "SELECT * FROM lobby_requests WHERE request_id = ?",
            (request_id,),
        ).fetchone()
        if not request_row or request_row["status"] != "pending":
            raise ValueError("Lobby request not pending")
        if not request_row["magic_token_id"]:
            raise ValueError("Lobby request missing magic token")

        token_row = conn.execute(
            "SELECT * FROM magic_login_tokens WHERE id = ?",
            (request_row["magic_token_id"],),
        ).fetchone()
        if not token_row:
            raise ValueError("Magic token not found")
        if token_row["revoked_at"]:
            raise ValueError("Magic token revoked")

        public_key_row = conn.execute(
            "SELECT * FROM public_keys WHERE id = ?",
            (request_row["public_key_id"],),
        ).fetchone()
        if not public_key_row:
            raise ValueError("Public key not found")

        target_account_id = _resolve_target_account_id(
            conn=conn,
            requested_username=request_row["requested_username"],
            public_key_account_id=public_key_row["account_id"],
        )
        now = _utc_now()
        conn.execute(
            "UPDATE public_keys SET account_id = ? WHERE id = ?",
            (target_account_id, public_key_row["id"]),
        )
        conn.execute(
            """
            UPDATE lobby_requests
            SET status = 'approved',
                approved_by = NULL,
                approved_at = ?,
                account_id = ?
            WHERE request_id = ?
            """,
            (now, target_account_id, request_id),
        )

        row = conn.execute(
            "SELECT * FROM lobby_requests WHERE request_id = ?",
            (request_id,),
        ).fetchone()
        return _row_to_dict(row)


def reject_lobby_request(request_id: str, rejected_by_account_id: int) -> dict:
    with connect() as conn:
        request_row = conn.execute(
            "SELECT * FROM lobby_requests WHERE request_id = ?",
            (request_id,),
        ).fetchone()
        if not request_row or request_row["status"] != "pending":
            raise ValueError("Lobby request not pending")
        now = _utc_now()
        conn.execute(
            """
            UPDATE lobby_requests
            SET status = 'rejected',
                rejected_by = ?,
                rejected_at = ?
            WHERE request_id = ?
            """,
            (rejected_by_account_id, now, request_id),
        )
        return _row_to_dict(
            conn.execute(
                "SELECT * FROM lobby_requests WHERE request_id = ?",
                (request_id,),
            ).fetchone()
        )


def mark_lobby_request_verified(request_id: str) -> dict:
    with connect() as conn:
        request_row = conn.execute(
            "SELECT * FROM lobby_requests WHERE request_id = ?",
            (request_id,),
        ).fetchone()
        if not request_row or request_row["status"] != "verifying":
            raise ValueError("Lobby request not awaiting verification")
        now = _utc_now()
        conn.execute(
            """
            UPDATE lobby_requests
            SET status = 'pending',
                verified_at = ?
            WHERE request_id = ?
            """,
            (now, request_id),
        )
        return _row_to_dict(
            conn.execute(
                "SELECT * FROM lobby_requests WHERE request_id = ?",
                (request_id,),
            ).fetchone()
        )


def append_ledger_event(
    event_type: str,
    actor_account_id: int | None,
    subject_account_id: int | None,
    metadata: dict,
) -> None:
    now = _utc_now()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO ledger_events (event_type, actor_account_id, subject_account_id, metadata, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                event_type,
                actor_account_id,
                subject_account_id,
                json.dumps(metadata, sort_keys=True),
                now,
            ),
        )


def list_ledger_events(limit: int = 200, offset: int = 0) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT
                ledger_events.id,
                ledger_events.event_type,
                ledger_events.actor_account_id,
                ledger_events.subject_account_id,
                ledger_events.metadata,
                ledger_events.created_at,
                actor.username AS actor_username,
                subject.username AS subject_username
            FROM ledger_events
            LEFT JOIN accounts AS actor ON actor.id = ledger_events.actor_account_id
            LEFT JOIN accounts AS subject ON subject.id = ledger_events.subject_account_id
            ORDER BY ledger_events.created_at DESC, ledger_events.id DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()
        return [dict(row) for row in rows]


def count_ledger_events() -> int:
    with connect() as conn:
        row = conn.execute("SELECT COUNT(*) AS count FROM ledger_events").fetchone()
        return int(row["count"]) if row else 0
