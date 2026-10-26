
from app.clients.moderation_api import ModerationApiClient
from app.schemas.review_evaluation import (
    ReviewEvaluationRequest,
    ReviewEvaluationResponse,
)
from app.services.moderation import moderate_comment, adapt_moderation_decision


DECISIONS = {
    "allow": "APPROVED",
    "flag": "FLAGGED",
    "block": "REJECTED",
}


async def evaluate_review(
    request: ReviewEvaluationRequest,
    callback: ModerationApiClient,
) -> ReviewEvaluationResponse:
    # Make sure the callback is configured before asking the AI to moderate.
    callback.require_configured()

    # Use your existing moderation function.
    analysis = moderate_comment(request.text)

    decision = DECISIONS[analysis.action]
    reason = analysis.explanation.strip()[:1000]

    # If the explanation is unusable, send the review for human review.
    if len(reason) < 3:
        decision = "FLAGGED"
        reason = (
            "The AI did not provide a usable explanation. "
            "Human review is required."
        )

    # Send the decision to Express and wait for confirmation.
    saved = await callback.record_decision(
        review_id=request.reviewId,
        review_updated_at=request.reviewUpdatedAt,
        decision=decision,
        reason=reason,
    )

    return ReviewEvaluationResponse(
        reviewId=request.reviewId,
        reviewUpdatedAt=request.reviewUpdatedAt,
        decision=decision,
        reason=reason,
        confidence=analysis.confidence,
        categories=analysis.categories,
        moderationId=saved.moderation.id,
    )
