
from typing import Literal
from uuid import uuid4

from pydantic import Field, field_validator

from app.schemas.common import StrictModel


class AssistantMessage(StrictModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=5_000)


class AssistantBusinessContext(StrictModel):
    business_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=128,
    )
    business_slug: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )


class AssistantRequest(StrictModel):
    conversation_id: str = Field(
        default_factory=lambda: str(uuid4()),
        min_length=1,
        max_length=128,
    )

    message: str = Field(min_length=1, max_length=5_000)

    business_context: AssistantBusinessContext | None = None

    history: list[AssistantMessage] = Field(
        default_factory=list,
        max_length=20,
    )

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("message must not be blank")

        return value


class AssistantResponse(StrictModel):
    conversation_id: str
    answer: str = Field(min_length=1, max_length=10_000)
    proposed_action: None = None
