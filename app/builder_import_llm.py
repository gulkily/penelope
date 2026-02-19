from __future__ import annotations

import asyncio
import os
from typing import Literal

from pydantic import BaseModel, Field

from app.builder_import_source import SourceCheckinRecord
from app.builder_import_transform import IMPORT_SNAPSHOT_PREFIX, SectionPayloads

DEFAULT_IMPORT_LLM_MODEL = "openai/gpt-5.2"


class ImportLLMError(RuntimeError):
    pass


class CheckinEnrichment(BaseModel):
    summary: str = ""
    challenges: str = ""
    milestones: str = ""
    opportunities: str = ""
    confidence: float = Field(..., ge=0, le=1)


def _format_section_text(week_of: str, text: str) -> str:
    candidate = (text or "").strip()
    if not candidate:
        return ""
    return f"{IMPORT_SNAPSHOT_PREFIX} {week_of}: {candidate}"


def _get_dedalus_client():
    try:
        from dedalus_labs import AsyncDedalus  # type: ignore
    except ImportError as exc:  # pragma: no cover - import guard
        raise ImportLLMError(
            "Dedalus SDK not installed. Add 'dedalus-labs' to requirements."
        ) from exc

    api_key = os.getenv("DEDALUS_API_KEY", "").strip()
    if api_key:
        return AsyncDedalus(api_key=api_key)
    return AsyncDedalus()


async def _run_enrichment(
    checkin: SourceCheckinRecord,
    model: str,
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
    completion = await client.chat.completions.parse(
        model=model,
        messages=messages,
        response_format=CheckinEnrichment,
        temperature=0,
    )
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
) -> tuple[SectionPayloads, Literal["enriched", "low_confidence", "error"]]:
    selected_model = model.strip() or DEFAULT_IMPORT_LLM_MODEL
    try:
        parsed = asyncio.run(_run_enrichment(checkin, selected_model))
    except Exception:
        return payload, "error"

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
    return enriched, "enriched"
