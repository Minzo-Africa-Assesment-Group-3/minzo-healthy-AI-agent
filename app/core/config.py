
from functools import lru_cache

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    log_level: str = "INFO"

    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-4o-mini"

    # Key used to authenticate requests coming into this AI service.
    service_api_key: SecretStr | None = Field(
        default=None,
        validation_alias="X_SERVICE_KEY",
    )

    # Express backend address.
    express_api_base_url: str = Field(
        default="http://127.0.0.1:3000",
        validation_alias="MINZO_API_URL",
    )

    # Separate credentials for Express requests and moderation callbacks.
    express_service_token: SecretStr | None = None
    ai_moderation_service_key: SecretStr | None = None

    express_request_timeout_seconds: float = Field(
        default=10.0,
        gt=0,
        le=60,
    )

    moderation_policy_version: str = "2026-10-15"

    moderation_flag_confidence_threshold: float = Field(
        default=0.85,
        ge=0,
        le=1,
    )
    moderation_block_confidence_threshold: float = Field(
        default=0.95,
        ge=0,
        le=1,
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_moderation_thresholds(self):
        if (
            self.moderation_block_confidence_threshold
            < self.moderation_flag_confidence_threshold
        ):
            raise ValueError(
                "The block confidence threshold must be greater than "
                "or equal to the flag confidence threshold."
            )

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


# Compatibility aliases for the files we have already created.
_settings = get_settings()

OPENAI_API_KEY = (
    _settings.openai_api_key.get_secret_value()
    if _settings.openai_api_key
    else None
)
OPENAI_MODEL = _settings.openai_model

MINZO_API_URL = _settings.express_api_base_url

X_SERVICE_KEY = (
    _settings.service_api_key.get_secret_value()
    if _settings.service_api_key
    else None
)

AI_MODERATION_SERVICE_KEY = (
    _settings.ai_moderation_service_key.get_secret_value()
    if _settings.ai_moderation_service_key
    else None
)

EXPRESS_SERVICE_TOKEN = (
    _settings.express_service_token.get_secret_value()
    if _settings.express_service_token
    else None
)

EXPRESS_REQUEST_TIMEOUT_SECONDS = (
    _settings.express_request_timeout_seconds
)
