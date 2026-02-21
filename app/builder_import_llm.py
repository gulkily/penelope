from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import Literal

from pydantic import BaseModel, Field

from app.builder_import_source import SourceCheckinRecord
from app.builder_import_transform import SectionPayloads

DEFAULT_IMPORT_LLM_MODEL = "openai/gpt-5.2"
BASE_DIR = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency guard
    load_dotenv = None


class ImportLLMError(RuntimeError):
    pass


class CheckinEnrichment(BaseModel):
    summary: str = ""
    challenges: str = ""
    milestones: str = ""
    opportunities: str = ""
    confidence: float = Field(..., ge=0, le=1)


def _maybe_load_dotenv() -> bool:
    if load_dotenv is None:
        return False
    return bool(load_dotenv(dotenv_path=BASE_DIR / ".env"))


def _format_section_text(week_of: str, text: str) -> str:
    _ = week_of
    candidate = (text or "").strip()
    if not candidate:
        return ""
    return candidate


def _get_dedalus_client():
    _maybe_load_dotenv()
    try:
        from dedalus_labs import Dedalus  # type: ignore
    except ImportError as exc:  # pragma: no cover - import guard
        raise ImportLLMError(
            "Dedalus SDK not installed. Add 'dedalus-labs' to requirements."
        ) from exc

    api_key = os.getenv("DEDALUS_API_KEY", "").strip()
    if api_key:
        return Dedalus(api_key=api_key)
    return Dedalus()


def get_llm_debug_info() -> dict[str, str]:
    dotenv_loaded = _maybe_load_dotenv()
    dedalus_sdk_available = True
    try:
        import dedalus_labs  # noqa: F401
    except ImportError:
        dedalus_sdk_available = False

    api_key = os.getenv("DEDALUS_API_KEY", "").strip()
    return {
        "python_executable": sys.executable,
        "dotenv_available": "yes" if load_dotenv is not None else "no",
        "dotenv_file_exists": "yes" if (BASE_DIR / ".env").exists() else "no",
        "dotenv_loaded": "yes" if dotenv_loaded else "no",
        "dedalus_sdk_available": "yes" if dedalus_sdk_available else "no",
        "dedalus_api_key_present": "yes" if bool(api_key) else "no",
    }


def get_llm_preflight_issues() -> tuple[dict[str, str], list[str]]:
    debug = get_llm_debug_info()
    issues: list[str] = []
    if debug["dedalus_sdk_available"] != "yes":
        issues.append(
            "Dedalus SDK missing in current interpreter "
            f"({debug['python_executable']}). Install deps in this env with: "
            f"{debug['python_executable']} -m pip install -r requirements.txt"
        )
    if debug["dedalus_api_key_present"] != "yes":
        issues.append(
            "DEDALUS_API_KEY not found in process environment or .env."
        )
    return debug, issues


def _run_enrichment(
    checkin: SourceCheckinRecord,
    model: str,
    timeout_seconds: float,
) -> CheckinEnrichment:
    client = _get_dedalus_client()
    messages = [
        {
            "role": "system",
            "content": (
                "You are cleaning and restructuring weekly founder update text. "
                "Return concise plain text for summary, challenges, milestones, and opportunities. "
                "Do not fabricate facts. Use empty string when a section has no supported content."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Week of: {checkin.week_of}\n"
                f"positive_summary:\n{checkin.positive_summary}\n\n"
                f"blockers_text:\n{checkin.blockers_text}\n\n"
                f"traction_text:\n{checkin.traction_text}\n\n"
                f"llm_summary:\n{checkin.llm_summary}\n\n"
                f"textual_data:\n{checkin.textual_data}\n"
            ),
        },
    ]
    try:
        completion = client.chat.completions.parse(
            model=model,
            messages=messages,
            response_format=CheckinEnrichment,
            temperature=0,
            timeout=max(0.1, timeout_seconds),
        )
    finally:
        client.close()
    try:
        parsed = completion.choices[0].message.parsed
    except (AttributeError, IndexError) as exc:
        raise ImportLLMError("Dedalus returned an empty response.") from exc
    if parsed is None:
        raise ImportLLMError("Dedalus returned no parsed output.")
    return parsed


def enrich_payload_with_llm(
    payload: SectionPayloads,
    checkin: SourceCheckinRecord,
    model: str = DEFAULT_IMPORT_LLM_MODEL,
    confidence_threshold: float = 0.7,
    timeout_seconds: float = 20.0,
) -> tuple[SectionPayloads, Literal["enriched", "low_confidence", "error"], str]:
    selected_model = model.strip() or DEFAULT_IMPORT_LLM_MODEL
    try:
        parsed = _run_enrichment(
            checkin=checkin,
            model=selected_model,
            timeout_seconds=timeout_seconds,
        )
    except Exception as exc:
        return payload, "error", f"{type(exc).__name__}: {exc}"

    if parsed.confidence < confidence_threshold:
        notes = list(payload.question_notes)
        notes.append(
            f"[Import] LLM enrichment confidence {parsed.confidence:.2f} below threshold "
            f"{confidence_threshold:.2f}; kept deterministic text."
        )
        return (
            SectionPayloads(
                summary=payload.summary,
                challenges=payload.challenges,
                milestones=payload.milestones,
                opportunities=payload.opportunities,
                question_notes=notes,
                created_at=payload.created_at,
            ),
            "low_confidence",
            "",
        )

    enriched = SectionPayloads(
        summary=_format_section_text(checkin.week_of, parsed.summary) or payload.summary,
        challenges=_format_section_text(checkin.week_of, parsed.challenges)
        or payload.challenges,
        milestones=_format_section_text(checkin.week_of, parsed.milestones)
        or payload.milestones,
        opportunities=_format_section_text(checkin.week_of, parsed.opportunities)
        or payload.opportunities,
        question_notes=list(payload.question_notes),
        created_at=payload.created_at,
    )
    return enriched, "enriched", ""
