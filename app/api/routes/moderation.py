import logging
from fastapi import APIRouter, Depends, HTTPException

import httpx

from app.clients.moderation_api import (
    ModerationApiClient,
    ModerationCallbackError,
)
from app.core.config import (
    EXPRESS_REQUEST_TIMEOUT_SECONDS,
    MINZO_API_URL,
)
from app.core.security import verify_service_key
from app.schemas.review_evaluation import (
    ReviewEvaluationRequest,
    ReviewEvaluationResponse,
)
from app.services.review_evaluation import evaluate_review


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/v1/moderation",
    tags=["Moderation"],
)


@router.post(
    "/customer-reviews/evaluate",
    response_model=ReviewEvaluationResponse,
    dependencies=[Depends(verify_service_key)],
)
async def evaluate_customer_review(
    request: ReviewEvaluationRequest,
):
    try:
        async with httpx.AsyncClient(
            base_url=MINZO_API_URL,
            timeout=EXPRESS_REQUEST_TIMEOUT_SECONDS,
        ) as client:
            callback = ModerationApiClient(client)

            return await evaluate_review(
                request=request,
                callback=callback,
            )

    except ModerationCallbackError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={
                "code": exc.code,
                "message": str(exc),
            },
        ) from exc

    except Exception:
        logger.exception("Unexpected error during review moderation")
        raise HTTPException(
            status_code=503,
            detail="Review moderation is temporarily unavailable.",
    ) from None
