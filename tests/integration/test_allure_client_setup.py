"""Integration tests for AllureClient setup and environment configuration."""

import os
from unittest.mock import patch

import pytest
from pydantic import SecretStr

from src.client import AllureClient


@pytest.mark.asyncio
@patch.dict(os.environ, {"ALLURE_ENDPOINT": "https://env.allure.com", "ALLURE_API_TOKEN": "env-token"})
async def test_client_from_env_success() -> None:
    """Test that client can be initialized from environment variables."""
    # We need to reload settings if we want to test the actual pydantic-settings behavior
    # or just trust AllureClient.from_env uses the global settings object.
    # Since settings are already initialized, we might need to mock them or reload.
    from src.utils.config import Settings

    with patch.dict(os.environ, {"ALLURE_ENDPOINT": "https://env.allure.com", "ALLURE_API_TOKEN": "env-token"}):
        # Create a fresh settings instance for the test
        test_settings = Settings()
        with patch("src.client.client.settings", test_settings):
            client = AllureClient.from_env()
            assert client._base_url == "https://env.allure.com"
            assert client._token.get_secret_value() == "env-token"


@pytest.mark.asyncio
async def test_client_from_env_missing() -> None:
    """Test from_env raises KeyError when variables are missing."""
    from src.utils.config import Settings

    # We clear environment AND ensure Settings doesn't find the token
    with patch.dict(os.environ, {}, clear=True):
        test_settings = Settings(ALLURE_API_TOKEN=None)
        with patch("src.client.client.settings", test_settings):
            with pytest.raises(KeyError, match="ALLURE_API_TOKEN is not set"):
                AllureClient.from_env()


@pytest.mark.asyncio
async def test_client_init_parameters() -> None:
    """Verify that init parameters are correctly stored."""
    base_url = "https://custom.allure.com"
    token = SecretStr("custom-token")

    client = AllureClient(base_url, token)
    assert client._base_url == base_url
    assert client._token == token


@pytest.mark.asyncio
async def test_client_requires_leading_scheme() -> None:
    """Verify that base_url is expected to be a full URL with scheme."""
    with pytest.raises(ValueError, match="Invalid base_url scheme"):
        AllureClient("demo.testops.cloud", SecretStr("token"))

    # These should NOT raise
    AllureClient("http://demo.testops.cloud", SecretStr("token"))
    AllureClient("https://demo.testops.cloud", SecretStr("token"))


@pytest.mark.asyncio
@patch.dict(os.environ, {"ALLURE_ENDPOINT": "https://env.allure.com", "ALLURE_API_TOKEN": "env-token"})
async def test_client_environment_logic_parity() -> None:
    """
    This test verifies that the client logic aligns with how we expect
    environment variables to be used in the main app.
    """
    endpoint = os.getenv("ALLURE_ENDPOINT")
    token = os.getenv("ALLURE_API_TOKEN")

    assert endpoint == "https://env.allure.com"
    assert token == "env-token"  # noqa: S105

    if endpoint and token:
        client = AllureClient(endpoint, SecretStr(token))
        assert client._base_url == endpoint
        assert client._token.get_secret_value() == token
