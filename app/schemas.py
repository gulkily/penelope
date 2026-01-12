from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    section: str = Field(..., description="Section key, e.g. summary or challenges.")
    text: str = Field(..., min_length=1)


class QuestionsUpdate(BaseModel):
    questions: str = Field("", description="Free-form questions or risks text.")
