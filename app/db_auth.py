from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from app.db_connection import connect


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row_to_dict(row) -> dict:
    return dict(row) if row else {}


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
                code,
                status,
                requested_at,
                expires_at,
                challenge
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request_id,
                public_key_id,
                requested_username,
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

        target_account_id = public_key_row["account_id"]
        if link_to_account_id:
            target_account_id = link_to_account_id
        if not target_account_id:
            now = _utc_now()
            cursor = conn.execute(
                """
                INSERT INTO accounts (username, created_at, updated_at)
                VALUES (?, ?, ?)
                """,
                (request_row["requested_username"], now, now),
            )
            target_account_id = cursor.lastrowid

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
