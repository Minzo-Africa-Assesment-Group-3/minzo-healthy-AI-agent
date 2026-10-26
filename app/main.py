
from fastapi import FastAPI

from app.api.routes.assistant import router as assistant_router
from app.api.routes.moderation import router as moderation_router


app = FastAPI(
    title="Minzo AI Service",
    description=(
        "AI-powered healthcare review moderation and "
        "assistant services for the Minzo healthcare directory."
    ),
    version="1.0.0",
)


@app.get("/", tags=["Health"])
async def health_check():
    """Confirm that the AI service is running."""
    return {
        "message": "Minzo AI Service is running.",
        "documentation": "/docs",
        "services": [
            "review moderation",
            "healthcare directory assistant",
        ],
    }


app.include_router(moderation_router)
app.include_router(assistant_router)
