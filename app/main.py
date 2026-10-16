from fastapi import FastAPI,  HTTPException, status
from pydantic import BaseModel, Field

from app.agent import moderate_comment, chat_with_assistant
from app.schemas import AssistantResponse, AssistantRequest


app = FastAPI(
    title="Minzo AI Service",
    description="AI-powered moderation service for healthcare reviews",
    version="1.0.0",
)


class CommentRequest(BaseModel):
    comment: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Healthcare review to mo",
    )


class AssistantRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User message for the Minzo assistant",
    )


@app.get("/")
def root():
    return{
        "message": "Review Moderation API is running. Add /docs to url to see the documentation."
    }


@app.post("/moderate")
def moderate(request: CommentRequest):
    try:
        result = moderate_comment(request.comment)

        return result

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The moderation service is temporarily unavailable. Please try again later.",
        )      

@app.post("/assistant", response_model=AssistantResponse)
def assistant(request: AssistantRequest):
    try:
        result = chat_with_assistant(request.message)

        return AssistantResponse(respons=result)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The moderation service is temporarily unavailable. Please try again later.",
        )      

