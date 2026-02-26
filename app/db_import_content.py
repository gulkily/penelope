from datetime import datetime, timezone
from difflib import SequenceMatcher
from dataclasses import dataclass
import re
from typing import Callable, Literal

from app.builder_import_transform import SectionPayloads
from app.db_connection import connect
from app.db_import_map import (
    list_import_item_ids_for_project,
    replace_import_item_ids_for_project,
)

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")
BULLET_PREFIX_RE = re.compile(r"^(?:[-*•]+|\d+[.)])\s+")
LEGACY_IMPORT_PREFIX = "[Import Snapshot]"
HIGH_SIMILARITY_DUPLICATE_THRESHOLD = 0.94
BORDERLINE_SIMILARITY_THRESHOLD = 0.86

DuplicateDecision = Literal["keep", "drop"]
DuplicateArbitrationCallback = Callable[[str, str, str], tuple[DuplicateDecision, str]]


@dataclass(frozen=True)
class ImportWriteMetrics:
    items_inserted: int
    exact_duplicates_skipped: int
    near_duplicates_skipped: int
    llm_arbitration_attempted: int
    llm_arbitration_kept: int
    llm_arbitration_dropped: int


def replace_import_snapshot_items(
    project_id: int,
    payloads: list[SectionPayloads],
    duplicate_arbitration_callback: DuplicateArbitrationCallback | None = None,
) -> ImportWriteMetrics:
    if payloads:
        ordered_payloads = sorted(
            payloads,
            key=lambda payload: (
                payload.week_of or "",
                payload.created_at or "",
                payload.source_checkin_id,
            ),
        )
    else:
        ordered_payloads = []

    rows: list[tuple[str, str, str]] = []
    for payload in ordered_payloads:
        timestamp = payload.created_at or datetime.now(timezone.utc).isoformat()
        sections = [
            ("summary", payload.summary),
            ("challenges", payload.challenges),
            ("milestones", payload.milestones),
            ("opportunities", payload.opportunities),
        ]
        for section, text in sections:
            for item_text in _expand_import_section_items(text):
                rows.append((section, item_text, timestamp))

    deduped_rows, metrics = _dedupe_rows(
        rows,
        duplicate_arbitration_callback=duplicate_arbitration_callback,
    )
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
        for section, item_text, timestamp in deduped_rows:
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
    return ImportWriteMetrics(
        items_inserted=len(inserted_item_ids),
        exact_duplicates_skipped=metrics["exact_duplicates_skipped"],
        near_duplicates_skipped=metrics["near_duplicates_skipped"],
        llm_arbitration_attempted=metrics["llm_arbitration_attempted"],
        llm_arbitration_kept=metrics["llm_arbitration_kept"],
        llm_arbitration_dropped=metrics["llm_arbitration_dropped"],
    )


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


def normalize_import_text(text: str) -> str:
    normalized = _normalize_space(text).lower()
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return _normalize_space(normalized)


def _token_set(text: str) -> set[str]:
    return {token for token in text.split(" ") if token}


def _similarity_score(left: str, right: str) -> float:
    left_normalized = normalize_import_text(left)
    right_normalized = normalize_import_text(right)
    if not left_normalized or not right_normalized:
        return 0.0
    if left_normalized == right_normalized:
        return 1.0
    left_tokens = _token_set(left_normalized)
    right_tokens = _token_set(right_normalized)
    if not left_tokens or not right_tokens:
        token_score = 0.0
    else:
        intersection = len(left_tokens & right_tokens)
        union = len(left_tokens | right_tokens)
        token_score = intersection / union if union else 0.0
    sequence_score = SequenceMatcher(None, left_normalized, right_normalized).ratio()
    return max(token_score, sequence_score)


def is_near_duplicate(candidate: str, existing: str) -> bool:
    return _similarity_score(candidate, existing) >= HIGH_SIMILARITY_DUPLICATE_THRESHOLD


def _dedupe_rows(
    rows: list[tuple[str, str, str]],
    duplicate_arbitration_callback: DuplicateArbitrationCallback | None = None,
) -> tuple[list[tuple[str, str, str]], dict[str, int]]:
    kept: list[tuple[str, str, str]] = []
    canonical_seen_by_section: dict[str, set[str]] = {}
    existing_text_by_section: dict[str, list[str]] = {}
    metrics = {
        "exact_duplicates_skipped": 0,
        "near_duplicates_skipped": 0,
        "llm_arbitration_attempted": 0,
        "llm_arbitration_kept": 0,
        "llm_arbitration_dropped": 0,
    }

    for section, item_text, timestamp in rows:
        canonical = normalize_import_text(item_text)
        if not canonical:
            continue

        canonical_seen = canonical_seen_by_section.setdefault(section, set())
        if canonical in canonical_seen:
            metrics["exact_duplicates_skipped"] += 1
            continue

        existing_texts = existing_text_by_section.setdefault(section, [])
        best_existing = ""
        best_similarity = 0.0
        for existing in existing_texts:
            similarity = _similarity_score(item_text, existing)
            if similarity > best_similarity:
                best_similarity = similarity
                best_existing = existing

        if best_similarity >= HIGH_SIMILARITY_DUPLICATE_THRESHOLD:
            metrics["near_duplicates_skipped"] += 1
            continue

        if (
            best_similarity >= BORDERLINE_SIMILARITY_THRESHOLD
            and duplicate_arbitration_callback is not None
            and best_existing
        ):
            metrics["llm_arbitration_attempted"] += 1
            decision, _reason = duplicate_arbitration_callback(item_text, best_existing, section)
            if decision == "drop":
                metrics["near_duplicates_skipped"] += 1
                metrics["llm_arbitration_dropped"] += 1
                continue
            metrics["llm_arbitration_kept"] += 1

        kept.append((section, item_text, timestamp))
        canonical_seen.add(canonical)
        existing_texts.append(item_text)

    return kept, metrics
