from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    section: str = Field(..., description="Section key, e.g. summary or challenges.")
    text: str = Field(..., min_length=1)


class QuestionsUpdate(BaseModel):
    questions: str = Field("", description="Free-form questions or risks text.")


class ObjectiveUpdate(BaseModel):
    objective: str = Field("", description="North Star objective for the project.")


class ProgressUpdate(BaseModel):
    progress: int = Field(0, ge=0, le=100, description="Progress percentage 0-100.")
