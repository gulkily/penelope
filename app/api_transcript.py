import re

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app import db
from app.llm_provider import LLMProviderError, run_transcript_llm
from app.questions_regeneration_jobs import (
    get_questions_regeneration_job,
    run_questions_regeneration_job,
    start_questions_regeneration_job,
)
from app.schemas import (
    QuestionsRegenerationStartResponse,
    QuestionsRegenerationStatusResponse,
    TranscriptUpdateRequest,
    TranscriptUpdateResponse,
)
from app.transcript_prompts import build_transcript_messages

router = APIRouter()

_NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
}


def _extract_goal_from_objective(objective: str) -> int | None:
    if not objective:
        return None
    text = objective.lower()

    for match in re.finditer(r"\b(\d+)(?!\s*%)\b", text):
        value = int(match.group(1))
        if 1 <= value <= 1000:
            return value

    for token in re.split(r"[\s,.;:()]+", text.replace("-", " ")):
        value = _NUMBER_WORDS.get(token)
        if value:
            return value
    return None


def _apply_objective_goal_hint(proposal, project: dict) -> None:
    if proposal.goal is not None:
        return
    objective = proposal.objective or ""
    candidate = _extract_goal_from_objective(objective)
    if candidate is None:
        return
    current_goal = project.get("goal")
    try:
        if current_goal is not None and int(current_goal) == candidate:
            return
    except (TypeError, ValueError):
        pass
    proposal.goal = candidate


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

    _apply_objective_goal_hint(proposal, project)

    return TranscriptUpdateResponse(proposal=proposal)


@router.post(
    "/projects/{project_id}/questions/regenerate",
    response_model=QuestionsRegenerationStartResponse,
)
def start_questions_regeneration(
    project_id: int,
    background_tasks: BackgroundTasks,
) -> QuestionsRegenerationStartResponse:
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Resident not found")

    job = start_questions_regeneration_job(project_id)
    if job["status"] == "queued":
        background_tasks.add_task(run_questions_regeneration_job, job["job_id"])

    return QuestionsRegenerationStartResponse(
        job_id=str(job["job_id"]),
        status=job["status"],
    )


@router.get(
    "/projects/{project_id}/questions/regeneration/{job_id}",
    response_model=QuestionsRegenerationStatusResponse,
)
def get_questions_regeneration_status(
    project_id: int,
    job_id: str,
) -> QuestionsRegenerationStatusResponse:
    job = get_questions_regeneration_job(project_id, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Questions regeneration job not found")

    return QuestionsRegenerationStatusResponse(
        job_id=str(job["job_id"]),
        status=job["status"],
        questions=job.get("questions"),
        error=job.get("error"),
    )
