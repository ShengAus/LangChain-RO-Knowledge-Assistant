from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3)


class AssistantResponse(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)


class LLMAnswerPayload(BaseModel):
    answer: str
