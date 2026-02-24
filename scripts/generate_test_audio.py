#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
import time
import wave
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

TIMESTAMP_RE = re.compile(r"^\[\d{2}:\d{2}\]$")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional helper
    load_dotenv = None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate long-form test audio from a transcript script using Dedalus Labs TTS. "
            "Long scripts are chunked automatically and merged into one WAV file."
        )
    )
    parser.add_argument(
        "--script-path",
        default="tests/fixtures/transcripts/long_conversation_15min_all_fields_script.txt",
        help="Path to transcript script text file.",
    )
    parser.add_argument(
        "--output-path",
        default="tests/fixtures/audio/long_conversation_15min_all_fields.wav",
        help="Final output WAV path.",
    )
    parser.add_argument(
        "--model",
        default="openai/gpt-4o-mini-tts",
        help="Dedalus speech model (for example: openai/gpt-4o-mini-tts).",
    )
    parser.add_argument(
        "--voice",
        default="alloy",
        choices=[
            "alloy",
            "ash",
            "ballad",
            "coral",
            "echo",
            "fable",
            "onyx",
            "nova",
            "sage",
            "shimmer",
            "verse",
        ],
        help="Voice preset.",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=0.9,
        help="Speech speed multiplier for TTS output.",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=3500,
        help="Maximum characters per TTS chunk (must stay below provider limit).",
    )
    parser.add_argument(
        "--speaker-mode",
        choices=["keep", "strip"],
        default="keep",
        help="Keep or strip speaker labels (for example, 'Leah:').",
    )
    parser.add_argument(
        "--keep-parts",
        action="store_true",
        help="Keep intermediate chunk WAV files after merge.",
    )
    return parser


def _clean_script_to_speakable_text(raw_text: str, speaker_mode: str) -> str:
    lines: list[str] = []
    for raw_line in raw_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("15-Minute Conversation Script"):
            continue
        if line == "Participants:":
            continue
        if line.startswith("- "):
            continue
        if TIMESTAMP_RE.match(line):
            continue
        if line.startswith("[") and line.endswith("]"):
            # Skip bracketed metadata headings.
            continue
        if ":" in line:
            speaker, content = line.split(":", 1)
            content = content.strip()
            if not content:
                continue
            if speaker_mode == "strip":
                lines.append(content)
            else:
                lines.append(f"{speaker.strip()}: {content}")
            continue
        lines.append(line)

    return " ".join(lines).strip()


def _chunk_text(text: str, max_chars: int) -> list[str]:
    if not text:
        return []
    if max_chars < 200:
        raise ValueError("--max-chars must be at least 200.")

    chunks: list[str] = []
    current = ""
    for sentence in SENTENCE_SPLIT_RE.split(text):
        sentence = sentence.strip()
        if not sentence:
            continue
        if len(sentence) > max_chars:
            # Hard wrap very long sentences by word.
            words = sentence.split()
            piece = ""
            for word in words:
                candidate = word if not piece else f"{piece} {word}"
                if len(candidate) <= max_chars:
                    piece = candidate
                    continue
                if piece:
                    if current:
                        chunks.append(current)
                        current = ""
                    chunks.append(piece)
                piece = word
            if piece:
                if current:
                    chunks.append(current)
                    current = ""
                chunks.append(piece)
            continue

        candidate = sentence if not current else f"{current} {sentence}"
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = sentence

    if current:
        chunks.append(current)
    return chunks


def _merge_wav_parts(parts: list[Path], output_path: Path) -> None:
    if not parts:
        raise ValueError("No WAV parts to merge.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(parts[0]), "rb") as first:
        params = first.getparams()
        format_signature = (
            params.nchannels,
            params.sampwidth,
            params.framerate,
            params.comptype,
            params.compname,
        )

    with wave.open(str(output_path), "wb") as merged:
        # Some providers emit WAV headers with placeholder/extreme nframes values.
        # Configure output format fields explicitly and let wave compute data length
        # from bytes actually written.
        merged.setnchannels(format_signature[0])
        merged.setsampwidth(format_signature[1])
        merged.setframerate(format_signature[2])
        merged.setcomptype(format_signature[3], format_signature[4])
        for part in parts:
            with wave.open(str(part), "rb") as handle:
                handle_params = handle.getparams()
                part_signature = (
                    handle_params.nchannels,
                    handle_params.sampwidth,
                    handle_params.framerate,
                    handle_params.comptype,
                    handle_params.compname,
                )
                if part_signature != format_signature:
                    raise RuntimeError(
                        "Cannot merge WAV parts with mismatched audio parameters."
                    )
                merged.writeframes(handle.readframes(handle.getnframes()))


def _get_dedalus_client():
    if load_dotenv is not None:
        load_dotenv(dotenv_path=REPO_ROOT / ".env")
    try:
        from dedalus_labs import Dedalus  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "dedalus-labs is not installed in this interpreter. "
            "Run: pip install -r requirements.txt"
        ) from exc
    return Dedalus()


def _status(message: str) -> None:
    print(f"[status] {message}", flush=True)


def generate_audio(
    script_path: Path,
    output_path: Path,
    model: str,
    voice: str,
    speed: float,
    max_chars: int,
    speaker_mode: str,
    keep_parts: bool,
) -> tuple[int, int]:
    started_at = time.monotonic()
    _status(f"Starting audio generation: script={script_path} output={output_path}")

    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

    _status("Loading script text")
    raw_text = script_path.read_text(encoding="utf-8")
    _status("Cleaning script into speakable text")
    speakable = _clean_script_to_speakable_text(raw_text, speaker_mode=speaker_mode)
    if not speakable:
        raise ValueError("No speakable content found in script after cleanup.")
    _status(f"Speakable text ready ({len(speakable)} chars)")

    _status(f"Chunking text (max {max_chars} chars per request)")
    chunks = _chunk_text(speakable, max_chars=max_chars)
    if not chunks:
        raise ValueError("No text chunks generated.")
    _status(f"Prepared {len(chunks)} chunk(s)")

    parts_dir = output_path.parent / f"{output_path.stem}_parts"
    _status(f"Preparing intermediate directory: {parts_dir}")
    parts_dir.mkdir(parents=True, exist_ok=True)
    for stale in sorted(parts_dir.glob("part_*.wav")):
        stale.unlink(missing_ok=True)
    part_paths: list[Path] = []

    _status("Initializing Dedalus client")
    client = _get_dedalus_client()
    try:
        total = len(chunks)
        for index, chunk in enumerate(chunks, start=1):
            _status(f"Synthesizing chunk {index}/{total} ({len(chunk)} chars)")
            part_path = parts_dir / f"part_{index:03d}.wav"
            response = client.audio.speech.create(
                model=model,
                voice=voice,
                input=chunk,
                response_format="wav",
                speed=speed,
            )
            response.write_to_file(part_path)
            part_paths.append(part_path)
            _status(f"Wrote chunk {index}/{total} -> {part_path}")
    finally:
        client.close()
        _status("Closed Dedalus client")

    _status(f"Merging {len(part_paths)} part(s) into final WAV")
    _merge_wav_parts(part_paths, output_path)
    _status(f"Merged {len(part_paths)} part(s) -> {output_path}")

    if not keep_parts:
        _status("Cleaning intermediate part files")
        for path in part_paths:
            path.unlink(missing_ok=True)
        try:
            parts_dir.rmdir()
            _status(f"Removed intermediate parts directory: {parts_dir}")
        except OSError:
            print(
                f"Intermediate part files removed, directory not empty: {parts_dir}",
                file=sys.stderr,
            )
    else:
        _status(f"Keeping intermediate parts in: {parts_dir}")

    elapsed = time.monotonic() - started_at
    _status(f"Audio generation complete in {elapsed:.1f}s")

    return len(chunks), len(speakable)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        chunk_count, char_count = generate_audio(
            script_path=Path(args.script_path),
            output_path=Path(args.output_path),
            model=args.model,
            voice=args.voice,
            speed=args.speed,
            max_chars=args.max_chars,
            speaker_mode=args.speaker_mode,
            keep_parts=args.keep_parts,
        )
    except Exception as exc:
        print(f"Audio generation failed: {exc}", file=sys.stderr)
        return 1

    print(f"Done. Speakable chars: {char_count}. Chunks: {chunk_count}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
