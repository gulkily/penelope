from datetime import datetime, timezone
import re

from app.builder_import_transform import SectionPayloads
from app.db_connection import connect
from app.db_import_map import (
    list_import_item_ids_for_project,
    replace_import_item_ids_for_project,
)

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")
BULLET_PREFIX_RE = re.compile(r"^(?:[-*•]+|\d+[.)])\s+")
LEGACY_IMPORT_PREFIX = "[Import Snapshot]"


def replace_import_snapshot_items(project_id: int, payload: SectionPayloads) -> None:
    timestamp = payload.created_at or datetime.now(timezone.utc).isoformat()
    rows = [
        ("summary", payload.summary),
        ("challenges", payload.challenges),
        ("milestones", payload.milestones),
        ("opportunities", payload.opportunities),
    ]
    mapped_item_ids = list_import_item_ids_for_project(project_id)
    inserted_item_ids: list[int] = []
    with connect() as conn:
        if mapped_item_ids:
            placeholders = ", ".join("?" for _ in mapped_item_ids)
            conn.execute(
                f"""
                DELETE FROM items
                WHERE project_id = ? AND id IN ({placeholders})
                """,
                (project_id, *mapped_item_ids),
            )
        conn.execute(
            """
            DELETE FROM items
            WHERE project_id = ? AND content LIKE ?
            """,
            (project_id, f"{LEGACY_IMPORT_PREFIX}%"),
        )
        section_next_order: dict[str, int] = {}
        for section, text in rows:
            for item_text in _expand_import_section_items(text):
                if section not in section_next_order:
                    section_next_order[section] = conn.execute(
                        """
                        SELECT COALESCE(MAX(sort_order), 0)
                        FROM items
                        WHERE project_id = ? AND section = ?
                        """,
                        (project_id, section),
                    ).fetchone()[0]
                section_next_order[section] += 1
                cursor = conn.execute(
                    """
                    INSERT INTO items (project_id, section, content, sort_order, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        project_id,
                        section,
                        item_text,
                        section_next_order[section],
                        timestamp,
                    ),
                )
                inserted_item_ids.append(int(cursor.lastrowid))
        conn.commit()
    replace_import_item_ids_for_project(project_id, inserted_item_ids)


def replace_import_notes(project_id: int, notes: list[str]) -> None:
    with connect() as conn:
        row = conn.execute(
            "SELECT questions FROM projects WHERE id = ?",
            (project_id,),
        ).fetchone()
        if not row:
            return
        existing_questions = (row["questions"] or "").strip()
        kept_lines: list[str] = []
        for line in existing_questions.splitlines():
            if line.strip().startswith("[Import"):
                continue
            kept_lines.append(line)

        merged_notes: list[str] = []
        seen: set[str] = set()
        for note in notes:
            candidate = note.strip()
            if not candidate or candidate in seen:
                continue
            seen.add(candidate)
            merged_notes.append(candidate)

        sections: list[str] = []
        kept_text = "\n".join([line for line in kept_lines if line.strip()]).strip()
        notes_text = "\n".join(merged_notes).strip()
        if kept_text:
            sections.append(kept_text)
        if notes_text:
            sections.append(notes_text)
        next_questions = "\n\n".join(sections)

        conn.execute(
            "UPDATE projects SET questions = ? WHERE id = ?",
            (next_questions, project_id),
        )
        conn.commit()


def seed_resident_summary_if_empty(project_id: int, summary: str) -> None:
    candidate = _normalize_space(summary)
    if not candidate:
        return
    with connect() as conn:
        row = conn.execute(
            "SELECT summary FROM projects WHERE id = ?",
            (project_id,),
        ).fetchone()
        if not row:
            return
        existing_summary = _normalize_space(row["summary"])
        if existing_summary:
            return
        conn.execute(
            "UPDATE projects SET summary = ? WHERE id = ?",
            (candidate, project_id),
        )
        conn.commit()


def _expand_import_section_items(
    text: str,
    max_item_chars: int = 220,
    max_items: int = 8,
) -> list[str]:
    candidate = _normalize_space(text)
    if not candidate:
        return []
    primary_parts = _split_primary_parts(candidate)
    chunks: list[str] = []
    for part in primary_parts:
        chunks.extend(_chunk_text(part, max_item_chars))

    cleaned_chunks: list[str] = []
    seen: set[str] = set()
    for chunk in chunks:
        normalized = _normalize_space(chunk)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        cleaned_chunks.append(normalized)
        if len(cleaned_chunks) >= max_items:
            break

    if not cleaned_chunks:
        return [candidate]
    return cleaned_chunks


def _split_primary_parts(text: str) -> list[str]:
    normalized_text = text.replace("\r\n", "\n").replace("\r", "\n")
    line_parts: list[str] = []
    for line in normalized_text.split("\n"):
        candidate = _normalize_space(BULLET_PREFIX_RE.sub("", line))
        if candidate:
            line_parts.append(candidate)
    if len(line_parts) > 1:
        return line_parts

    single_line = _normalize_space(normalized_text)
    if not single_line:
        return []

    sentence_parts = _split_sentences(single_line)
    if len(sentence_parts) > 1:
        return sentence_parts

    semicolon_parts = [_normalize_space(part) for part in single_line.split(";")]
    semicolon_parts = [part for part in semicolon_parts if part]
    if len(semicolon_parts) > 1:
        return semicolon_parts
    return [single_line]


def _split_sentences(text: str) -> list[str]:
    return [part.strip() for part in SENTENCE_SPLIT_RE.split(text) if part.strip()]


def _chunk_text(text: str, max_item_chars: int) -> list[str]:
    if len(text) <= max_item_chars:
        return [text]

    sentence_parts = _split_sentences(text)
    if len(sentence_parts) > 1:
        chunks: list[str] = []
        current = ""
        for sentence in sentence_parts:
            if len(sentence) > max_item_chars:
                if current:
                    chunks.append(current)
                    current = ""
                chunks.extend(_word_wrap(sentence, max_item_chars))
                continue
            combined = sentence if not current else f"{current} {sentence}"
            if len(combined) <= max_item_chars:
                current = combined
            else:
                chunks.append(current)
                current = sentence
        if current:
            chunks.append(current)
        return chunks

    return _word_wrap(text, max_item_chars)


def _word_wrap(text: str, max_item_chars: int) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if len(candidate) <= max_item_chars:
            current = candidate
        else:
            chunks.append(current)
            current = word
    chunks.append(current)
    return chunks


def _normalize_space(text: str) -> str:
    return " ".join((text or "").strip().split())
