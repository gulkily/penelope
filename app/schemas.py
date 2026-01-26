from typing import Literal

from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    section: str = Field(..., description="Section key, e.g. summary or challenges.")
    text: str = Field(..., min_length=1)


class ItemUpdate(BaseModel):
    text: str = Field(..., min_length=1)


class ItemOrderUpdate(BaseModel):
    section: str = Field(..., description="Section key, e.g. summary or challenges.")
    ordered_ids: list[int] = Field(
        ...,
        min_items=1,
        description="Ordered item ids for the section.",
    )


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1)


class ProjectArchiveUpdate(BaseModel):
    archived: bool = Field(False)


class QuestionsUpdate(BaseModel):
    questions: str = Field("", description="Free-form questions or risks text.")


class SummaryUpdate(BaseModel):
    summary: str = Field("", description="Resident summary text.")


class ObjectiveUpdate(BaseModel):
    objective: str = Field("", description="North Star objective for the resident.")


class GoalUpdate(BaseModel):
    goal: int = Field(..., ge=1, description="Goal value for resident progress.")


class ProgressUpdate(BaseModel):
    progress: int = Field(0, ge=0, le=100, description="Progress percentage 0-100.")


class ProgressHistoryEntry(BaseModel):
    progress: int = Field(..., ge=0, le=100, description="Progress percentage 0-100.")
    recorded_at: str = Field(..., description="UTC ISO timestamp for the update.")


class ProgressHistoryResponse(BaseModel):
    history: list[ProgressHistoryEntry]


TranscriptSectionKey = Literal[
    "summary",
    "challenges",
    "opportunities",
    "milestones",
]


class TranscriptUpdateRequest(BaseModel):
    transcript: str = Field(..., min_length=1, description="Conversation transcript.")


class TranscriptItemSuggestion(BaseModel):
    section: TranscriptSectionKey = Field(
        ...,
        description="Target section for a new item.",
    )
    text: str = Field(..., min_length=1, description="Item text to add.")


class TranscriptUpdateProposal(BaseModel):
    summary: str | None = Field(None, description="Proposed summary update.")
    questions: str | None = Field(None, description="Proposed questions update.")
    objective: str | None = Field(None, description="Proposed objective update.")
    goal: int | None = Field(None, ge=1, description="Proposed goal value.")
    progress: int | None = Field(
        None,
        ge=0,
        le=100,
        description="Proposed progress percentage 0-100.",
    )
    progress_units: int | None = Field(
        None,
        ge=0,
        description="Proposed progress units (absolute count toward the goal).",
    )
    progress_units_delta: int | None = Field(
        None,
        description="Proposed progress change in units (delta).",
    )
    items_to_add: list[TranscriptItemSuggestion] = Field(
        default_factory=list,
        description="New list items to add by section.",
    )


class TranscriptUpdateResponse(BaseModel):
    proposal: TranscriptUpdateProposal


class TranscriptionResponse(BaseModel):
    text: str = Field("", description="Transcribed text.")
    status: str = Field("complete", description="Status: queued|processing|complete|error.")
    progress: int | None = Field(
        None,
        ge=0,
        le=100,
        description="Optional progress percentage for upload/transcription.",
    )
