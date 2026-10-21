import os
import json

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

from app.schemas import ModerationResult
from app.tools.directory import DIRECTORY_TOOLS


load_dotenv()

# --------- LLM configuration ------
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY"),
)


# --------- Moderation Agent ------
structured_llm = llm.with_structured_output(ModerationResult)


def moderate_comment(comment: str) -> ModerationResult:
    prompt = f"""
        You are a content moderation agent for a healthcare review platform.

        Your job is to review comments written about healthcare professionals
        and healthcare institutions.

        The platform allows users to write both positive and negative reviews.
        Negative reviews are allowed as long as they are respectful and relevant
        to the user's experience.

        Classify the comment into exactly one of these categories:

        1. allowed
        - Genuine positive or negative feedback.
        - Criticism of a doctor, healthcare professional, or institution is allowed
            when expressed respectfully.
        - Complaints about waiting times, service quality, communication,
            treatment experience, cost, etc. are allowed.

        2. abusive
        - Insults
        - Harassment
        - Threats
        - Degrading or hateful language directed at a person or institution
        - Profanity used to attack or harass someone

        3. spam
        - Advertising or promotional content unrelated to the user's healthcare
            experience
        - Repeated promotional messages
        - Suspicious links or marketing content
        - Content designed primarily to promote a product, service, or website
            rather than review the healthcare experience

        Important rules:

        - Do NOT reject a review simply because it is negative.
        - Do NOT reject a review merely because it expresses dissatisfaction.
        - The user is allowed to criticize healthcare professionals or institutions.
        - Focus on whether the criticism is expressed as a legitimate review
        rather than harassment or abuse.
        - Do not invent information that is not present in the comment.

        If the comment is allowed:
        - allowed = true
        - category = "allowed"
        - reason should briefly explain why it is acceptable.
        - suggestion can be an empty string.

        If the comment is abusive or spam:
        - allowed = false
        - identify the correct category.
        - explain briefly why it was rejected.
        - provide a polite suggestion telling the user how to rewrite it.

        Comment to moderate: {comment}
    """

    return structured_llm.invoke(prompt)


# --------- Assitant Agent ------
assistant_llm = llm.bind_tools(DIRECTORY_TOOLS)
DIRECTORY_TOOL_MAP = {
    tool.name: tool
    for tool in DIRECTORY_TOOLS
}

def chat_with_assistant(message:str) -> str:
    """Generate a response from the Minzo conversation assitant.
    """
    system_prompt = SystemMessage(
        content="""You are the Minzo healthcare directory assitance.
        This is a healthcare directory focused on Liberia.
        
        Your job is to help users with:
        - Finding healthvcare businesses and professionals
        - Unerstanding healthcare directory information
        - Finding information about services
        - Answering questions about using the Minzo healthycare platform
        
        Be helpful, concise and clear.
        
        Important rules:
        - Do not invent businesses, doctors, services, rating, reviews, or other directory information.
        - When directory tools are avaliable, use them to retrieve current information instead of guessing.
        - Do not claim that you performed an action that you did not perform.
        - If you do not have enough information to answer the question, say so clearly.
        - Do not provide medical diagnosis or emergency medical instructions.
        - You are a directory assitant, not a doctor.
        
    """)
    
    messages = [
        system_prompt,
        HumanMessage(content=message),
    ]
    response = assistant_llm.ainvoke(message)
    
    return response.content
