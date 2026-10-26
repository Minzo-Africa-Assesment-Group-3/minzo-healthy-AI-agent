from fastapi import Header, HTTPException, status

from app.core.config import X_SERVICE_KEY


def verify_service_key(
    x_service_key: str | None = Header(
        default=None,
        alias="X-Service-Key",
    ),
) -> None:
    if not X_SERVICE_KEY or x_service_key != X_SERVICE_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid service credentials.",
        )
        