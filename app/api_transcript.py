from fastapi import APIRouter, HTTPException

from app import db
from app.llm_provider import LLMProviderError, run_transcript_llm
from app.schemas import TranscriptUpdateRequest, TranscriptUpdateResponse
from app.transcript_prompts import build_transcript_messages

router = APIRouter()


@router.post(
    "/projects/{project_id}/transcript",
    response_model=TranscriptUpdateResponse,
)
async def analyze_transcript(
    project_id: int,
    payload: TranscriptUpdateRequest,
) -> TranscriptUpdateResponse:
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Resident not found")

    transcript = payload.transcript.strip()
    if not transcript:
        raise HTTPException(status_code=400, detail="Transcript cannot be empty")

    messages = build_transcript_messages(project, transcript)
    try:
        proposal = await run_transcript_llm(messages)
    except LLMProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - guardrail
        raise HTTPException(status_code=502, detail="LLM request failed") from exc

    return TranscriptUpdateResponse(proposal=proposal)
