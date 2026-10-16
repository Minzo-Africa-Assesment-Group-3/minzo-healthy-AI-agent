from typing import Literal

from pydantic import BaseModel


class ModerationResult(BaseModel):
    allowed: bool
    category: Literal["allowed", "abusive", "spam"]
    reason: str
    suggestion: str