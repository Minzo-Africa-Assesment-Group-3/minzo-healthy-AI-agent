
from typing import Literal

from pydantic import Field

from app.schemas.common import StrictModel
from app.schemas.moderation import AbuseCategory, BusinessContext


ModerationAction = Literal["APPROVED", "FLAGGED", "REJECTED"]
PublicationStatus = Literal["PUBLISHED", "HIDDEN"]


class ReviewEvaluationRequest(StrictModel):
    reviewId: str = Field(min_length=1)
    reviewUpdatedAt: str = Field(min_length=1)
    stars: int = Field(ge=1, le=5)
    text: str = Field(min_length=1)
    business: BusinessContext


class ModerationRecord(StrictModel):
    id: str = Field(min_length=1)
    decision: ModerationAction


class ModerationCallbackResponse(StrictModel):
    reviewId: str
    moderationStatus: ModerationAction
    publicationStatus: PublicationStatus
    moderation: ModerationRecord


class ReviewEvaluationResponse(StrictModel):
    reviewId: str
    reviewUpdatedAt: str
    decision: ModerationAction
    reason: str = Field(min_length=3, max_length=1000)
    confidence: float = Field(ge=0, le=1)
    categories: list[AbuseCategory] = Field(min_length=1)
    moderationId: str = Field(min_length=1)
