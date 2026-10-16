from fastapi import FastAPI,  HTTPException, status
from pydantic import BaseModel, Field

from app.agent import moderate_comment


app = FastAPI(
    title="Review Moderation API",
    description="AI-powered moderation service for healthcare reviews",
    version="1.0.0",
)


class CommentRequest(BaseModel):
    comment: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Healthcare review to moderate",
    )
    

@app.get("/")
def root():
    return{
        "message": "Review Moderation API is running"
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
