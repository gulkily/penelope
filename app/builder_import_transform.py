from __future__ import annotations

from dataclasses import dataclass

from app.builder_import_source import SourceBuilderRecord, SourceCheckinRecord


@dataclass(frozen=True)
class SectionPayloads:
    source_checkin_id: str
    week_of: str
    summary: str
    challenges: str
    milestones: str
    opportunities: str
    created_at: str


def build_section_payloads(
    builder: SourceBuilderRecord,
    checkin: SourceCheckinRecord,
) -> SectionPayloads:
    summary = _format_import_text(checkin.week_of, checkin.positive_summary)
    challenges = _format_import_text(checkin.week_of, checkin.blockers_text)
    milestones = _format_import_text(checkin.week_of, checkin.traction_text)
    opportunities = _format_import_text(checkin.week_of, checkin.llm_summary)
    if not any((summary, challenges, milestones, opportunities)):
        textual_fallback = checkin.textual_data.strip()
        if textual_fallback:
            opportunities = f"[Import Snapshot] {checkin.week_of} source textual_data: {textual_fallback}"

    return SectionPayloads(
        source_checkin_id=checkin.source_checkin_id,
        week_of=checkin.week_of,
        summary=summary,
        challenges=challenges,
        milestones=milestones,
        opportunities=opportunities,
        created_at=_resolve_checkin_timestamp(checkin),
    )


def build_builder_import_notes(
    builder: SourceBuilderRecord,
    checkins: list[SourceCheckinRecord],
) -> list[str]:
    notes: list[str] = []
    if not checkins:
        notes.append("[Import] No weekly check-ins available in source dataset.")
    for checkin in checkins:
        if checkin.north_star_value is None:
            notes.append(
                f"[Import TODO] Missing north_star_value for check-in week: {checkin.week_of}."
            )
    if builder.email.strip():
        notes.append(f"[Import] Source email: {builder.email.strip()}")
    if builder.ca_name.strip():
        notes.append(f"[Import] Source community architect: {builder.ca_name.strip()}")
    return notes


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
