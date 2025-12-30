from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings managed by pydantic-settings.
    Reads from environment variables and .env file.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Allure TestOps Configuration
    ALLURE_ENDPOINT: str = Field(default="https://demo.testops.cloud", description="Allure TestOps Base URL")
    ALLURE_PROJECT_ID: int | None = Field(default=None, description="Default Project ID")
    ALLURE_API_TOKEN: SecretStr | None = Field(default=None, description="Allure API Token")

    # Application Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    HOST: str = Field(default="127.0.0.1", description="Host to bind the server to")
    PORT: int = Field(default=8000, description="Port to bind the server to")
    MCP_MODE: Literal["http", "stdio"] = Field(default="http", description="Running mode: http or stdio")


# Global settings instance
settings = Settings()
