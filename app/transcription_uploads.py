from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.transcription_constants import (
    ALLOWED_MIME_TYPES,
    DEFAULT_CHUNK_SIZE,
    MAX_UPLOAD_BYTES,
    UPLOAD_SESSION_TTL_SECONDS,
)

_UPLOAD_ID_PATTERN = re.compile(r"^[a-f0-9-]{36}$")


@dataclass(frozen=True)
class UploadSession:
    upload_id: str
    chunk_size: int
    expires_at: datetime


class UploadSessionError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def _upload_root() -> Path:
    root = os.getenv("TRANSCRIPTION_UPLOAD_DIR", "").strip()
    if root:
        base = Path(root)
    else:
        base = Path(tempfile.gettempdir()) / "penelope_transcription_uploads"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _upload_dir(upload_id: str) -> Path:
    if not _UPLOAD_ID_PATTERN.match(upload_id):
        raise UploadSessionError(status_code=404, detail="Upload session not found")
    return _upload_root() / upload_id


def _meta_path(upload_id: str) -> Path:
    return _upload_dir(upload_id) / "meta.json"


def _chunks_dir(upload_id: str) -> Path:
    return _upload_dir(upload_id) / "chunks"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _load_meta(upload_id: str) -> dict:
    meta_path = _meta_path(upload_id)
    if not meta_path.exists():
        raise UploadSessionError(status_code=404, detail="Upload session not found")
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise UploadSessionError(status_code=500, detail="Upload session corrupted") from exc


def _save_meta(upload_id: str, meta: dict) -> None:
    meta_path = _meta_path(upload_id)
    meta_path.write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")


def _normalize_content_type(content_type: str | None) -> str:
    normalized = (content_type or "").lower()
    if ";" in normalized:
        normalized = normalized.split(";", 1)[0].strip()
    if normalized == "application/octet-stream":
        return ""
    return normalized


def _validate_content_type(content_type: str | None) -> str:
    normalized = _normalize_content_type(content_type)
    if normalized and normalized not in ALLOWED_MIME_TYPES:
        raise UploadSessionError(status_code=400, detail="Unsupported audio type")
    return normalized


def _validate_total_size(total_size: int | None) -> None:
    if total_size is not None and total_size > MAX_UPLOAD_BYTES:
        raise UploadSessionError(status_code=400, detail="Audio file exceeds 35MB limit")


def _is_expired(meta: dict) -> bool:
    expires_at = meta.get("expires_at")
    if not expires_at:
        return False
    try:
        return _parse_timestamp(expires_at) <= _now()
    except ValueError:
        return True


def prune_expired_uploads() -> None:
    root = _upload_root()
    for entry in root.iterdir():
        if not entry.is_dir():
            continue
        meta_file = entry / "meta.json"
        if not meta_file.exists():
            continue
        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            shutil.rmtree(entry, ignore_errors=True)
            continue
        if _is_expired(meta):
            shutil.rmtree(entry, ignore_errors=True)


def create_upload_session(
    filename: str | None = None,
    content_type: str | None = None,
    total_size: int | None = None,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> UploadSession:
    normalized_type = _validate_content_type(content_type)
    _validate_total_size(total_size)
    prune_expired_uploads()

    upload_id = str(uuid.uuid4())
    now = _now()
    expires_at = now + timedelta(seconds=UPLOAD_SESSION_TTL_SECONDS)

    upload_dir = _upload_dir(upload_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    _chunks_dir(upload_id).mkdir(parents=True, exist_ok=True)

    meta = {
        "upload_id": upload_id,
        "created_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "chunk_size": chunk_size,
        "total_chunks": None,
        "received_bytes": 0,
        "filename": filename,
        "content_type": normalized_type or None,
        "total_size": total_size,
    }
    _save_meta(upload_id, meta)
    return UploadSession(upload_id=upload_id, chunk_size=chunk_size, expires_at=expires_at)


def store_chunk(
    upload_id: str,
    index: int,
    total_chunks: int,
    payload: bytes,
    filename: str | None = None,
    content_type: str | None = None,
    total_size: int | None = None,
) -> tuple[int, int, str]:
    meta = _load_meta(upload_id)
    if _is_expired(meta):
        raise UploadSessionError(status_code=410, detail="Upload session expired")

    if total_chunks <= 0:
        raise UploadSessionError(status_code=400, detail="Invalid chunk count")
    if index < 0 or index >= total_chunks:
        raise UploadSessionError(status_code=400, detail="Invalid chunk index")

    meta_total_chunks = meta.get("total_chunks")
    if meta_total_chunks is None:
        meta_total_chunks = total_chunks
        meta["total_chunks"] = total_chunks
    elif meta_total_chunks != total_chunks:
        raise UploadSessionError(status_code=400, detail="Chunk count mismatch")

    if filename and not meta.get("filename"):
        meta["filename"] = filename
    if content_type and not meta.get("content_type"):
        normalized_type = _validate_content_type(content_type)
        meta["content_type"] = normalized_type or None
    if total_size and not meta.get("total_size"):
        _validate_total_size(total_size)
        meta["total_size"] = total_size

    chunk_dir = _chunks_dir(upload_id)
    chunk_path = chunk_dir / f"{index:06d}.part"
    existing_size = chunk_path.stat().st_size if chunk_path.exists() else 0
    new_total_bytes = meta.get("received_bytes", 0) - existing_size + len(payload)
    if new_total_bytes > MAX_UPLOAD_BYTES:
        raise UploadSessionError(status_code=400, detail="Audio file exceeds 35MB limit")

    chunk_path.write_bytes(payload)
    meta["received_bytes"] = new_total_bytes
    _save_meta(upload_id, meta)

    received_chunks = len(list(chunk_dir.glob("*.part")))
    status = "complete" if received_chunks == total_chunks else "partial"
    return received_chunks, total_chunks, status


def assemble_upload(upload_id: str) -> tuple[bytes, str, str]:
    meta = _load_meta(upload_id)
    if _is_expired(meta):
        raise UploadSessionError(status_code=410, detail="Upload session expired")

    total_chunks = meta.get("total_chunks")
    if not total_chunks:
        raise UploadSessionError(status_code=400, detail="Upload not complete")

    chunk_dir = _chunks_dir(upload_id)
    payload = bytearray()
    total_bytes = 0
    for index in range(total_chunks):
        chunk_path = chunk_dir / f"{index:06d}.part"
        if not chunk_path.exists():
            raise UploadSessionError(status_code=400, detail="Upload not complete")
        chunk_bytes = chunk_path.read_bytes()
        total_bytes += len(chunk_bytes)
        if total_bytes > MAX_UPLOAD_BYTES:
            raise UploadSessionError(status_code=400, detail="Audio file exceeds 35MB limit")
        payload.extend(chunk_bytes)

    filename = meta.get("filename") or "recording"
    content_type = meta.get("content_type") or "application/octet-stream"
    _validate_content_type(meta.get("content_type"))
    _validate_total_size(meta.get("total_size"))
    return bytes(payload), filename, content_type


def cleanup_upload(upload_id: str) -> None:
    shutil.rmtree(_upload_dir(upload_id), ignore_errors=True)
