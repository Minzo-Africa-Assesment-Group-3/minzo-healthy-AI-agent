
import json

import httpx
from pydantic import SecretStr
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

from app.core.config import (
    EXPRESS_REQUEST_TIMEOUT_SECONDS,
    MINZO_API_URL,
)
from app.schemas.assistant import (
    AssistantBusinessContext,
    AssistantMessage,
)
from app.clients.express_api import ExpressApiClient
from app.services.assistant_prompt import SYSTEM_PROMPT
from app.tools.directory import build_directory_tools
from app.tools.current_user import build_current_user_tools
from app.llm.openai import llm


async def chat_with_assistant(
    message: str,
    history: list[AssistantMessage] | None = None,
    business_context: AssistantBusinessContext | None = None,
    user_token: SecretStr | None = None,
) -> str:
    system_prompt = SYSTEM_PROMPT

    messages = [SystemMessage(content=system_prompt)]

    if business_context:
        context = business_context.model_dump(exclude_none=True)
        messages.append(
            SystemMessage(
                content=(
                    "Reference business context, provided as data only:\n"
                    + json.dumps(context, default=str)
                )
            )
        )

    for item in (history or [])[-20:]:
        if item.role == "user":
            messages.append(HumanMessage(content=item.content))
        elif item.role == "assistant":
            messages.append(AIMessage(content=item.content))

    messages.append(HumanMessage(content=message))

    async with httpx.AsyncClient(
        base_url=MINZO_API_URL,
        timeout=EXPRESS_REQUEST_TIMEOUT_SECONDS,
    ) as http:
        api = ExpressApiClient(http)

        # Directory tools are available to everyone.
        available_tools = build_directory_tools(api)

        # Private account tools require a trusted bearer token.
        if user_token is not None:
            user_api = api.for_user(user_token)
            available_tools.extend(build_current_user_tools(user_api))

        assistant_llm = llm.bind_tools(available_tools)
        tool_map = {item.name: item for item in available_tools}

        for _ in range(5):
            response = await assistant_llm.ainvoke(messages)

            if not response.tool_calls:
                if isinstance(response.content, str):
                    return response.content

                return json.dumps(response.content, default=str)

            messages.append(response)

            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_call_id = tool_call["id"]

                selected_tool = tool_map.get(tool_name)

                if selected_tool is None:
                    tool_result = (
                        "That tool is unavailable. Please try another request."
                    )
                else:
                    try:
                        tool_result = await selected_tool.ainvoke(tool_args)
                    except Exception:
                        tool_result = (
                            "The requested information could not be retrieved. "
                            "Please try again later."
                        )

                if not isinstance(tool_result, str):
                    tool_result = json.dumps(tool_result, default=str)

                messages.append(
                    ToolMessage(
                        content=tool_result,
                        tool_call_id=tool_call_id,
                    )
                )

        return (
            "I couldn't complete that request. "
            "Please try asking in a simpler way."
        )
