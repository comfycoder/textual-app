"""Application settings.

Resolution order (highest priority first):
    1. CLI flags (passed in through Typer)
    2. Environment variables prefixed with AIQ_
    3. A .env-style file passed via --config
    4. Defaults defined here
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AIQ_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_base_url: str = Field(
        default="https://api.example.com",
        description="Base URL for the AIQ OpenAPI endpoints.",
    )
    tenant_id: str | None = Field(
        default=None,
        description="Entra tenant ID. Required for login.",
    )
    client_id: str | None = Field(
        default=None,
        description="Entra app registration client ID.",
    )
    request_timeout_seconds: float = Field(default=30.0)
    sidebar_width: int = Field(
        default=20,
        description="Dashboard sidebar width as a percentage (10–80). Set via AIQ_SIDEBAR_WIDTH.",
        ge=10,
        le=80,
    )
