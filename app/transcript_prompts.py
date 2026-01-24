from __future__ import annotations

from pathlib import Path

from app.db_constants import SECTIONS

PROMPT_DIR = Path(__file__).resolve().parent / "prompts"


def _load_prompt(name: str) -> str:
    return (PROMPT_DIR / name).read_text(encoding="utf-8").strip()


def _format_section_items(sections: dict) -> str:
    lines: list[str] = []
    for section in SECTIONS:
        title = section.title()
        lines.append(f"{title}:")
        items = sections.get(section) or []
        if items:
            for item in items:
                text = str(item.get("text", "")).strip()
                if text:
                    lines.append(f"- {text}")
        else:
            lines.append("- (none)")
        lines.append("")
    return "\n".join(lines).strip()


def _format_project_context(project: dict) -> str:
    summary = str(project.get("summary", "")).strip()
    questions = str(project.get("questions", "")).strip()
    objective = str(project.get("objective", "")).strip()
    goal = project.get("goal")
    progress = project.get("progress")

    try:
        goal_value = int(goal) if goal is not None else 0
    except (TypeError, ValueError):
        goal_value = 0
    try:
        progress_value = int(progress) if progress is not None else 0
    except (TypeError, ValueError):
        progress_value = 0

    progress_units = 0
    if goal_value > 0:
        progress_units = round((progress_value / 100) * goal_value)

    sections = project.get("sections") or {}

    lines = [
        f"Summary: {summary or '(empty)'}",
        f"Questions: {questions or '(empty)'}",
        f"Objective: {objective or '(empty)'}",
        f"Goal: {goal_value}",
        f"Progress percent: {progress_value}",
        f"Progress units: {progress_units} / {goal_value}",
        "",
        "Section items:",
        _format_section_items(sections),
    ]
    return "\n".join(lines).strip()


def build_transcript_messages(project: dict, transcript: str) -> list[dict]:
    system_prompt = _load_prompt("transcript_system.txt")
    output_prompt = _load_prompt("transcript_output_format.txt")
    user_prompt = _load_prompt("transcript_user.txt").format(
        resident_name=str(project.get("name", "Resident")).strip() or "Resident",
        project_context=_format_project_context(project),
        transcript=transcript.strip(),
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": output_prompt},
        {"role": "user", "content": user_prompt},
    ]
