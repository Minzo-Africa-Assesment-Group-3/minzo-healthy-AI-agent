from typing import Literal, Any

from pydantic import BaseModel, Field


class ModerationResult(BaseModel):
    allowed: bool
    category: Literal["allowed", "abusive", "spam"]
    reason: str
    suggestion: str

class ChatMessage(BaseModel):
    role: str
    content: str


class AssistantRequest(BaseModel):
    conversation_id: str | None = None
    message: str = Field(..., min_length=1, max_length=2000)
    history: list[ChatMessage] = Field(default_factory=list)
    business_context: dict[str, Any] | None = None


class AssistantResponse(BaseModel):
    conversation_id: str | None = None
    response: str
    proposed_action: dict[str, Any] | None = None
