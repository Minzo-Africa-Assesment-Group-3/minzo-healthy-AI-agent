
import asyncio
import logging

import httpx
from pydantic import ValidationError, SecretStr

from app.core.config import (
    AI_MODERATION_SERVICE_KEY,
    EXPRESS_REQUEST_TIMEOUT_SECONDS,
)
from app.schemas.review_evaluation import ModerationCallbackResponse


logger = logging.getLogger(__name__)


class ModerationCallbackError(RuntimeError):
    def __init__(
        self,
        status_code: int,
        code: str,
        detail: str,
    ):
        super().__init__(detail)
        self.status_code = status_code
        self.code = code


class ModerationApiClient:
    def __init__(self, client: httpx.AsyncClient):
        self._client = client
        self._service_key = AI_MODERATION_SERVICE_KEY

    def require_configured(self) -> None:
        if not self._service_key:
            raise ModerationCallbackError(
                503,
                "callback_not_configured",
                "The moderation callback service key is not configured.",
            )

    async def record_decision(
        self,
        *,
        review_id: str,
        review_updated_at: str,
        decision: str,
        reason: str,
    ) -> ModerationCallbackResponse:
        self.require_configured()

        path = (
            "/api/v1/automation/customer-reviews/"
            f"{review_id}/moderation"
        )

        service_key = (
            self._service_key.get_secret_value()
            if isinstance(self._service_key, SecretStr)
            else self._service_key
        )

        for attempt in range(3):
            response = None

            try:
                response = await self._client.patch(
                    path,
                    headers={
                        "X-Service-Key": service_key,
                        "Accept": "application/json",
                    },
                    json={
                        "decision": decision,
                        "reason": reason,
                        "reviewUpdatedAt": review_updated_at,
                    },
                    timeout=EXPRESS_REQUEST_TIMEOUT_SECONDS,
                    follow_redirects=False,
                )
            except httpx.TransportError:
                # Retry temporary network failures.
                pass

            if response is not None:
                if response.status_code in {404, 409}:
                    raise ModerationCallbackError(
                        response.status_code,
                        "review_missing_or_changed",
                        "The review was missing or changed. "
                        "The decision was not confirmed.",
                    )

                if response.status_code == 200:
                    try:
                        result = ModerationCallbackResponse.model_validate(
                            response.json()
                        )

                        expected_publication = (
                            "HIDDEN"
                            if decision == "REJECTED"
                            else "PUBLISHED"
                        )

                        if (
                            result.reviewId != review_id
                            or result.moderationStatus != decision
                            or result.moderation.decision != decision
                            or result.publicationStatus
                            != expected_publication
                        ):
                            raise ValueError(
                                "The backend response does not match "
                                "the requested decision."
                            )

                        return result

                    except (ValidationError, ValueError):
                        raise ModerationCallbackError(
                            502,
                            "invalid_callback_response",
                            "The backend returned an invalid confirmation.",
                        ) from None

                if response.status_code < 500:
                    logger.warning(
                        "Moderation callback rejected: status=%s, response=%s",
                        response.status_code,
                        response.text[:1000],
                    )
                    raise ModerationCallbackError(
                        502,
                        "callback_rejected",
                        "The backend rejected the moderation callback. "
                        f"Backend status: {response.status_code}.",
                    )

            if attempt < 2:
                logger.warning(
                    "Retrying moderation callback, attempt %s",
                    attempt + 2,
                )
                await asyncio.sleep(0.25 * (2**attempt))

        raise ModerationCallbackError(
            502,
            "callback_unavailable",
            "The backend did not confirm that the decision was saved.",
        )
