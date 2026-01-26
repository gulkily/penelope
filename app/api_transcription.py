from __future__ import annotations

import os

import httpx
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas import TranscriptionResponse

router = APIRouter()

ALLOWED_MIME_TYPES = {
    "audio/mpeg",
    "audio/mp3",
    "audio/mp4",
    "audio/wav",
    "audio/x-wav",
    "audio/webm",
    "audio/ogg",
    "audio/aac",
    "audio/flac",
}
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
DEDALUS_TRANSCRIBE_URL = "https://api.dedaluslabs.ai/v1/audio/transcriptions"


def _validate_file(upload: UploadFile, payload: bytes) -> None:
    content_type = (upload.content_type or "").lower()
    if content_type and content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported audio type")
    if len(payload) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="Audio file exceeds 25MB limit")


def _build_files(upload: UploadFile, payload: bytes) -> dict[str, tuple[str, bytes, str]]:
    filename = upload.filename or "recording"
    content_type = upload.content_type or "application/octet-stream"
    return {"file": (filename, payload, content_type)}


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
    _validate_file(file, payload)

    headers = {"Authorization": f"Bearer {api_key}"}
    files = _build_files(file, payload)
    data = _build_form(model="openai/whisper-1", response_format="json")

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                DEDAULS_TRANSCRIBE_URL,
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
