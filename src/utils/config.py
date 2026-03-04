from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings managed by pydantic-settings.
    Reads from environment variables and .env file.
    Falls back to environment variables if .env file is absent.
    """

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_ignore_empty=True,
    )

    # Allure TestOps Configuration
    ALLURE_ENDPOINT: str = Field(default="https://demo.testops.cloud", description="Allure TestOps Base URL")
    ALLURE_PROJECT_ID: int | None = Field(default=None, description="Default Project ID")
    ALLURE_API_TOKEN: SecretStr | None = Field(default=None, description="Allure API Token")

    # Application Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Logging format (json or console)")
    HOST: str = Field(default="127.0.0.1", description="Host to bind the server to")
    PORT: int = Field(default=8000, description="Port to bind the server to")
    MCP_MODE: Literal["http", "stdio"] = Field(default="stdio", description="Running mode: http or stdio")
    TELEMETRY_ENABLED: bool | None = Field(
        default=None,
        description="Optional telemetry override. When unset, TelemetryConfig.enabled is used.",
    )
    TELEMETRY_UMAMI_WEBSITE_ID: str | None = Field(
        default=None,
        description="Optional Umami website id override. When unset, TelemetryConfig.umami_website_id is used.",
    )
    TELEMETRY_UMAMI_HOSTNAME: str | None = Field(
        default=None,
        description="Optional Umami hostname override. When unset, TelemetryConfig.umami_hostname is used.",
    )


@dataclass(frozen=True)
class TelemetryConfig:
    """Telemetry settings are configured in code, with optional env opt-out."""

    enabled: bool = True
    umami_base_url: str = "https://collector.nmro.cc"
    umami_website_id: str | None = "e011ac28-1d83-475e-b74a-6c610162dddb"
    umami_hostname: str = "lucius-mcp.prod"
    hash_salt: str | None = None


settings = Settings()
telemetry_config = TelemetryConfig()
