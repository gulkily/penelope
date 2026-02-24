from __future__ import annotations

import os

import httpx
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.schemas import (
    TranscriptionResponse,
    UploadChunkResponse,
    UploadSessionCreateRequest,
    UploadSessionResponse,
)
from app.transcription_constants import ALLOWED_MIME_TYPES, MAX_UPLOAD_BYTES
from app.transcription_uploads import (
    UploadSessionError,
    assemble_upload,
    cleanup_upload,
    create_upload_session,
    store_chunk,
)

router = APIRouter()

DEDALUS_TRANSCRIBE_URL = "https://api.dedaluslabs.ai/v1/audio/transcriptions"


def _normalize_content_type(content_type: str | None) -> str:
    normalized = (content_type or "").lower()
    if ";" in normalized:
        normalized = normalized.split(";", 1)[0].strip()
    if normalized == "application/octet-stream":
        return ""
    return normalized


def _validate_payload(content_type: str, payload: bytes) -> None:
    if content_type and content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported audio type")
    if len(payload) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="Audio file exceeds 35MB limit")


def _build_files(upload: UploadFile, payload: bytes) -> dict[str, tuple[str, bytes, str]]:
    filename = upload.filename or "recording"
    content_type = upload.content_type or "application/octet-stream"
    return {"file": (filename, payload, content_type)}


def _build_files_from_payload(
    payload: bytes,
    filename: str | None,
    content_type: str | None,
) -> dict[str, tuple[str, bytes, str]]:
    safe_name = filename or "recording"
    safe_type = content_type or "application/octet-stream"
    return {"file": (safe_name, payload, safe_type)}


def _build_form(model: str, response_format: str) -> dict[str, str]:
    return {
        "model": model,
        "response_format": response_format,
    }


@router.post("/transcriptions", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
) -> TranscriptionResponse:
    api_key = os.getenv("DEDALUS_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(status_code=500, detail="DEDALUS_API_KEY is not configured")

    payload = await file.read()
    return await transcribe_audio_bytes(payload, file.filename, file.content_type)


async def transcribe_audio_bytes(
    payload: bytes,
    filename: str | None,
    content_type: str | None,
) -> TranscriptionResponse:
    safe_content_type = _normalize_content_type(content_type)
    _validate_payload(safe_content_type, payload)

    api_key = os.getenv("DEDALUS_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(status_code=500, detail="DEDALUS_API_KEY is not configured")

    headers = {"Authorization": f"Bearer {api_key}"}
    files = _build_files_from_payload(payload, filename, safe_content_type or None)
    data = _build_form(model="openai/whisper-1", response_format="json")

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                DEDALUS_TRANSCRIBE_URL,
                headers=headers,
                data=data,
                files=files,
            )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail="Transcription request failed") from exc

    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail="Transcription failed")

    body = response.json()
    text = body.get("text") if isinstance(body, dict) else ""
    if not isinstance(text, str):
        text = ""

    return TranscriptionResponse(text=text, status="complete", progress=100)


@router.post("/transcriptions/uploads", response_model=UploadSessionResponse)
async def create_transcription_upload_session(
    payload: UploadSessionCreateRequest | None = None,
) -> UploadSessionResponse:
    request = payload or UploadSessionCreateRequest()
    try:
        session = create_upload_session(
            filename=request.filename,
            content_type=request.content_type,
            total_size=request.total_size,
        )
    except UploadSessionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    return UploadSessionResponse(
        upload_id=session.upload_id,
        chunk_size=session.chunk_size,
        expires_at=session.expires_at,
    )


@router.put("/transcriptions/uploads/{upload_id}/chunks", response_model=UploadChunkResponse)
async def upload_transcription_chunk(
    upload_id: str,
    chunk: UploadFile = File(...),
    index: int = Form(...),
    total_chunks: int = Form(...),
    filename: str | None = Form(None),
    content_type: str | None = Form(None),
    total_size: int | None = Form(None),
) -> UploadChunkResponse:
    payload = await chunk.read()
    normalized_content_type = content_type or chunk.content_type
    if normalized_content_type == "application/octet-stream":
        normalized_content_type = None
    try:
        received_chunks, expected_chunks, status = store_chunk(
            upload_id,
            index=index,
            total_chunks=total_chunks,
            payload=payload,
            filename=filename,
            content_type=normalized_content_type,
            total_size=total_size,
        )
    except UploadSessionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    return UploadChunkResponse(
        upload_id=upload_id,
        status=status,
        received_chunks=received_chunks,
        total_chunks=expected_chunks,
    )


@router.post("/transcriptions/uploads/{upload_id}/complete", response_model=TranscriptionResponse)
async def complete_transcription_upload(upload_id: str) -> TranscriptionResponse:
    try:
        payload, filename, content_type = assemble_upload(upload_id)
        response = await transcribe_audio_bytes(payload, filename, content_type)
    except UploadSessionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    cleanup_upload(upload_id)
    return response
