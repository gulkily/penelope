from __future__ import annotations

from pathlib import Path

from app.db_constants import SECTIONS

PROMPT_DIR = Path(__file__).resolve().parent / "prompts"


def _load_prompt(name: str) -> str:
    return (PROMPT_DIR / name).read_text(encoding="utf-8").strip()


def _format_section_items(sections: dict) -> str:
    lines: list[str] = []
    for section in SECTIONS:
        lines.append(f"{section.title()}:")
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
    try:
        goal = int(project.get("goal") or 0)
    except (TypeError, ValueError):
        goal = 0
    try:
        progress = int(project.get("progress") or 0)
    except (TypeError, ValueError):
        progress = 0

    progress_units = 0
    if goal > 0:
        progress_units = round((progress / 100) * goal)

    sections = project.get("sections") or {}
    lines = [
        f"Summary: {summary or '(empty)'}",
        f"Questions: {questions or '(empty)'}",
        f"Objective: {objective or '(empty)'}",
        f"Goal: {goal}",
        f"Progress percent: {progress}",
        f"Progress units: {progress_units} / {goal}",
        "",
        "Section items:",
        _format_section_items(sections),
    ]
    return "\n".join(lines).strip()


def _format_progress_history(history: list[dict]) -> str:
    if not history:
        return "- (none)"

    lines: list[str] = []
    for entry in history:
        recorded_at = str(entry.get("recorded_at", "")).strip() or "(unknown)"
        try:
            progress = int(entry.get("progress") or 0)
        except (TypeError, ValueError):
            progress = 0
        lines.append(f"- {recorded_at}: {progress}%")
    return "\n".join(lines)


def build_questions_regeneration_messages(
    project: dict,
    history: list[dict],
) -> list[dict]:
    system_prompt = _load_prompt("questions_regeneration_system.txt")
    output_prompt = _load_prompt("questions_regeneration_output_format.txt")
    user_prompt = _load_prompt("questions_regeneration_user.txt").format(
        resident_name=str(project.get("name", "Resident")).strip() or "Resident",
        project_context=_format_project_context(project),
        progress_history=_format_progress_history(history),
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": output_prompt},
        {"role": "user", "content": user_prompt},
    ]
