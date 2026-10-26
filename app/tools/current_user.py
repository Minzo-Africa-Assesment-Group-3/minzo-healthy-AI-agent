
import json
from typing import Annotated, Any
from fastapi import HTTPException
from langchain_core.tools import BaseTool, tool
from pydantic import Field

from app.clients.current_user_api import CurrentUserApiClient
from app.clients.express_api import ExpressApiError


def _format_result(result: Any) -> str:
    return json.dumps(result, ensure_ascii=False, default=str)


def _validation_message(error: Exception) -> str:
    return (
        "Invalid tool arguments. Please use valid pagination values "
        "and try again."
    )


def _read(result: Any) -> str:
    return _format_result(result)


def build_current_user_tools(
    api: CurrentUserApiClient,
) -> list[BaseTool]:
    """Build read-only tools for the authenticated user's own account."""

    @tool
    async def get_my_profile() -> str:
        """Retrieve the signed-in user's own profile.

        Use this only when the user asks about their own account.
        Never use this tool to look up another person's account.
        """
        try:
            return _read(await api.get_profile())
        except HTTPException as exc:
            if exc.status_code in {401, 403}:
                return "Please sign in again to access your profile."
            raise
        except ExpressApiError:
            return (
                "Your profile is temporarily unavailable. "
                "Please try again later."
            )
    @tool
    async def get_my_reviews(
        page_number: Annotated[
            int, Field(ge=1, description="Page number, starting at 1")
        ] = 1,
        page_size: Annotated[
            int, Field(ge=1, le=20, description="Number of reviews to retrieve")
        ] = 10,
    ) -> str:
        """Retrieve the signed-in user's own reviews, newest first.

        Use this only when the user asks about their own reviews.
        Do not use it to retrieve another person's reviews.
        """
        try:
            return _read(
                await api.get_reviews(
                    page_number=page_number,
                    page_size=page_size,
                )
            )
        except HTTPException as exc:
            if exc.status_code in {401, 403}:
                return "Please sign in again to access your reviews."
            raise
        except ExpressApiError:
            return (
                "Your reviews are temporarily unavailable. "
                "Please try again later."
            )

    tools: list[BaseTool] = [
        get_my_profile,
        get_my_reviews,
    ]

    for user_tool in tools:
        user_tool.handle_tool_error = True
        user_tool.handle_validation_error = _validation_message

    return tools
