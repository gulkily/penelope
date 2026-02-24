from __future__ import annotations

from app import db
from app.llm_provider import LLMProviderError, run_questions_llm
from app.questions_prompts import build_questions_regeneration_messages


class QuestionsGenerationError(RuntimeError):
    pass


async def generate_ai_questions(project_id: int) -> str:
    project = db.get_project(project_id)
    if not project:
        raise QuestionsGenerationError("Resident not found")

    history = db.list_progress_history(project_id, limit=20)
    messages = build_questions_regeneration_messages(project, history)

    try:
        questions = await run_questions_llm(messages)
    except LLMProviderError as exc:
        raise QuestionsGenerationError(str(exc)) from exc

    text = questions.strip()
    if not text:
        raise QuestionsGenerationError("No questions generated")
    return text
