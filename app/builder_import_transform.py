from __future__ import annotations

from dataclasses import dataclass

from app.builder_import_source import SourceBuilderRecord, SourceCheckinRecord


@dataclass(frozen=True)
class SectionPayloads:
    summary: str
    challenges: str
    milestones: str
    opportunities: str
    question_notes: list[str]
    created_at: str


def build_section_payloads(
    builder: SourceBuilderRecord,
    latest_checkin: SourceCheckinRecord | None,
) -> SectionPayloads:
    if latest_checkin is None:
        return SectionPayloads(
            summary="",
            challenges="",
            milestones="",
            opportunities="",
            question_notes=["[Import] No weekly check-ins available in source dataset."],
            created_at="",
        )

    summary = _format_import_text(latest_checkin.week_of, latest_checkin.positive_summary)
    challenges = _format_import_text(latest_checkin.week_of, latest_checkin.blockers_text)
    milestones = _format_import_text(latest_checkin.week_of, latest_checkin.traction_text)
    opportunities = _format_import_text(latest_checkin.week_of, latest_checkin.llm_summary)
    notes: list[str] = []
    if latest_checkin.north_star_value is None:
        notes.append(
            f"[Import TODO] Missing north_star_value for latest check-in week: {latest_checkin.week_of}."
        )
    if not any((summary, challenges, milestones, opportunities)):
        textual_fallback = latest_checkin.textual_data.strip()
        if textual_fallback:
            notes.append(
                f"[Import Snapshot] {latest_checkin.week_of} source textual_data: {textual_fallback}"
            )
    if builder.email.strip():
        notes.append(f"[Import] Source email: {builder.email.strip()}")
    if builder.ca_name.strip():
        notes.append(f"[Import] Source community architect: {builder.ca_name.strip()}")
    return SectionPayloads(
        summary=summary,
        challenges=challenges,
        milestones=milestones,
        opportunities=opportunities,
        question_notes=notes,
        created_at=_resolve_checkin_timestamp(latest_checkin),
    )


def _format_import_text(week_of: str, text: str) -> str:
    _ = week_of
    candidate = (text or "").strip()
    if not candidate:
        return ""
    return candidate


def _resolve_checkin_timestamp(checkin: SourceCheckinRecord) -> str:
    for value in (checkin.updated_at, checkin.created_at):
        candidate = (value or "").strip()
        if candidate:
            return candidate
    return f"{checkin.week_of}T00:00:00+00:00"
