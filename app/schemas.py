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
