
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import SecretStr

from app.core.security import verify_service_key
from app.schemas.assistant import AssistantRequest, AssistantResponse
from app.services.assistant import chat_with_assistant

router = APIRouter(prefix="/v1/assistant", tags=["Assistant"])


@router.post(
    "/messages",
    response_model=AssistantResponse,
    dependencies=[Depends(verify_service_key)],
)
async def ai_assistant(
    request: AssistantRequest,
    authorization: str | None = Header(default=None),
) -> AssistantResponse:
    user_token = None

    if authorization is not None:
        scheme, separator, token = authorization.partition(" ")

        if (
            not separator
            or scheme.lower() != "bearer"
            or not token.strip()
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header.",
            )

        user_token = SecretStr(token.strip())

    try:
        answer = await chat_with_assistant(
            message=request.message,
            history=request.history,
            business_context=request.business_context,
            user_token=user_token,
        )

        return AssistantResponse(
            conversation_id=request.conversation_id,
            answer=answer,
            proposed_action=None,
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "The assistant service is temporarily unavailable. "
                "Please try again later."
            ),
        ) from None
