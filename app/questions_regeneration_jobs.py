from __future__ import annotations

from datetime import datetime, timedelta, timezone
from threading import Lock
from uuid import uuid4

from app import db
from app.questions_ai import QuestionsGenerationError, generate_ai_questions

_ACTIVE_STATUSES = {"queued", "running"}
_JOB_RETENTION = timedelta(minutes=30)

_jobs: dict[str, dict] = {}
_active_project_jobs: dict[int, str] = {}
_lock = Lock()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _prune_jobs() -> None:
    cutoff = datetime.now(timezone.utc) - _JOB_RETENTION
    to_delete: list[str] = []
    for job_id, job in _jobs.items():
        if job["status"] in _ACTIVE_STATUSES:
            continue
        completed_at = job.get("completed_at")
        created_at = job.get("created_at")
        timestamp = completed_at or created_at
        if not timestamp:
            continue
        if _parse_iso(str(timestamp)) < cutoff:
            to_delete.append(job_id)

    for job_id in to_delete:
        job = _jobs.pop(job_id, None)
        if not job:
            continue
        project_id = job.get("project_id")
        active_job_id = _active_project_jobs.get(project_id)
        if active_job_id == job_id:
            _active_project_jobs.pop(project_id, None)


def _snapshot(job: dict) -> dict:
    return {
        "job_id": job["job_id"],
        "status": job["status"],
        "questions": job.get("questions"),
        "error": job.get("error"),
        "project_id": job["project_id"],
    }


def start_questions_regeneration_job(project_id: int) -> dict:
    with _lock:
        _prune_jobs()
        active_job_id = _active_project_jobs.get(project_id)
        if active_job_id:
            active_job = _jobs.get(active_job_id)
            if active_job and active_job["status"] in _ACTIVE_STATUSES:
                return _snapshot(active_job)

        job_id = str(uuid4())
        job = {
            "job_id": job_id,
            "project_id": project_id,
            "status": "queued",
            "questions": None,
            "error": None,
            "created_at": _now_iso(),
            "started_at": None,
            "completed_at": None,
        }
        _jobs[job_id] = job
        _active_project_jobs[project_id] = job_id
        return _snapshot(job)


def get_questions_regeneration_job(project_id: int, job_id: str) -> dict | None:
    with _lock:
        _prune_jobs()
        job = _jobs.get(job_id)
        if not job or job.get("project_id") != project_id:
            return None
        return _snapshot(job)


def _set_job_failed(job_id: str, message: str) -> None:
    with _lock:
        job = _jobs.get(job_id)
        if not job:
            return
        job["status"] = "failed"
        job["error"] = message
        job["completed_at"] = _now_iso()


async def run_questions_regeneration_job(job_id: str) -> None:
    with _lock:
        job = _jobs.get(job_id)
        if not job or job["status"] != "queued":
            return
        job["status"] = "running"
        job["started_at"] = _now_iso()
        project_id = int(job["project_id"])

    project = db.get_project(project_id)
    if not project:
        _set_job_failed(job_id, "Resident not found")
        return

    try:
        questions = await generate_ai_questions(project_id)
    except QuestionsGenerationError as exc:
        _set_job_failed(job_id, str(exc))
        return
    except Exception:  # pragma: no cover - guardrail
        _set_job_failed(job_id, "Questions generation failed")
        return

    db.update_questions(project_id, questions)

    with _lock:
        job = _jobs.get(job_id)
        if not job:
            return
        job["status"] = "completed"
        job["questions"] = questions
        job["error"] = None
        job["completed_at"] = _now_iso()
