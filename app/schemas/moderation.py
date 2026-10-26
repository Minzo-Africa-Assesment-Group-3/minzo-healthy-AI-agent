from typing import Literal
from pydantic import Field, model_validator

from app.schemas.common import StrictModel


AbuseCategory = Literal[
    "harassment",
    "hate",
    "threat",
    "sexual_content",
    "personal_information",
    "spam",
    "fraud",
    "profanity",
    "none",
]


class BusinessContext(StrictModel):
    id: str
    name: str
    
    
class CustomerReviewModerationRequest(StrictModel):
    reviewId: str
    reviewUpdatedAt: str
    stars: int = Field(..., ge=1, le=5)
    text: str = Field(..., min_length=1)
    business: BusinessContext
    
    
class CustomerReviewModerationResponse(StrictModel):
    reviewId: str
    decision: str
    reason: str | None = None
    confidence: float = Field(..., ge=0, le=1)
    categories: list[str]
    callbackStatus: str


class ReviewModerationDecision(StrictModel):
    is_abusive: bool
    action: Literal["allow", "flag", "block"]
    categories: list[AbuseCategory] = Field(min_length=1)
    severity: Literal["none", "low", "medium", "high"]
    confidence: float = Field(ge=0, le=1)
    explanation: str
    requires_human_review: bool

    @model_validator(mode="after")
    def validate_categories(self):
        if len(self.categories) != len(set(self.categories)):
            raise ValueError("Categories must not contain duplicates")

        if "none" in self.categories and len(self.categories) != 1:
            raise ValueError(
                "'none' cannot be combined with another category"
            )

        return self
