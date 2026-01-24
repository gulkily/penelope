from __future__ import annotations

import os

from app.schemas import TranscriptUpdateProposal

DEFAULT_LLM_MODEL = "openai/gpt-4o-mini"


class LLMProviderError(RuntimeError):
    pass


def _get_dedalus_client():
    try:
        from dedalus_labs import AsyncDedalus  # type: ignore
    except ImportError as exc:  # pragma: no cover - import guard
        raise LLMProviderError(
            "Dedalus SDK not installed. Add 'dedalus-labs' to requirements."
        ) from exc

    api_key = os.getenv("DEDALUS_API_KEY", "").strip()
    if api_key:
        return AsyncDedalus(api_key=api_key)
    return AsyncDedalus()


async def run_transcript_llm(messages: list[dict]) -> TranscriptUpdateProposal:
    client = _get_dedalus_client()
    model = os.getenv("LLM_MODEL", DEFAULT_LLM_MODEL).strip() or DEFAULT_LLM_MODEL

    completion = await client.chat.completions.parse(
        model=model,
        messages=messages,
        response_format=TranscriptUpdateProposal,
        temperature=0,
    )

    try:
        parsed = completion.choices[0].message.parsed
    except (AttributeError, IndexError) as exc:
        raise LLMProviderError("Dedalus returned an empty response.") from exc

    if parsed is None:
        raise LLMProviderError("Dedalus returned no parsed output.")

    return parsed
