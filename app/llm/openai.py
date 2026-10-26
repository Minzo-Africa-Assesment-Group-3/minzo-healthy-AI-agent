
from langchain_openai import ChatOpenAI

from app.core.config import OPENAI_API_KEY, OPENAI_MODEL
from app.schemas.moderation import ReviewModerationDecision


llm = ChatOpenAI(
    model=OPENAI_MODEL,
    temperature=0,
    api_key=OPENAI_API_KEY,
)

moderation_llm = llm.with_structured_output(
    ReviewModerationDecision
)
