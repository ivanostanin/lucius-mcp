"""Integration tests for AllureClient setup and environment configuration."""

import os
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from pydantic import SecretStr

from src.client import AllureClient


@pytest.mark.asyncio
@patch.dict(
    os.environ, {"ALLURE_ENDPOINT": "https://env.allure.com", "ALLURE_API_TOKEN": "env-token", "ALLURE_PROJECT_ID": "1"}
)
async def test_client_from_env_success() -> None:
    """Test that client can be initialized from environment variables."""
    with (
        patch.dict(os.environ, {"ALLURE_ENDPOINT": "https://env.allure.com", "ALLURE_API_TOKEN": "env-token"}),
        patch("src.utils.auth_resolution.load_auth_config", return_value=None),
    ):
        client = AllureClient.from_env()
        assert client._base_url == "https://env.allure.com"
        assert client._token.get_secret_value() == "env-token"


@pytest.mark.asyncio
async def test_client_from_env_missing() -> None:
    """Test from_env raises KeyError when variables are missing."""
    with patch.dict(os.environ, {}, clear=True), patch("src.utils.auth_resolution.load_auth_config", return_value=None):
        with pytest.raises(KeyError, match="ALLURE_API_TOKEN is not set"):
            AllureClient.from_env()


@pytest.mark.asyncio
async def test_client_from_env_missing_endpoint_after_token() -> None:
    """Test from_env raises endpoint error once token is configured."""
    with (
        patch.dict(os.environ, {"ALLURE_API_TOKEN": "env-token", "ALLURE_PROJECT_ID": "1"}, clear=True),
        patch("src.utils.auth_resolution.load_auth_config", return_value=None),
        patch(
            "src.utils.auth_resolution.get_current_settings",
            return_value=SimpleNamespace(ALLURE_ENDPOINT=None, ALLURE_API_TOKEN=None, ALLURE_PROJECT_ID=1),
        ),
    ):
        with pytest.raises(KeyError, match="ALLURE_ENDPOINT is not set"):
            AllureClient.from_env()


@pytest.mark.asyncio
async def test_client_init_parameters() -> None:
    """Verify that init parameters are correctly stored."""
    base_url = "https://custom.allure.com"
    token = SecretStr("custom-token")

    client = AllureClient(base_url, token, project=1)
    assert client._base_url == base_url
    assert client._token == token


@pytest.mark.asyncio
async def test_client_requires_leading_scheme() -> None:
    """Verify that base_url is expected to be a full URL with scheme."""
    with pytest.raises(ValueError, match="Invalid base_url scheme"):
        AllureClient("demo.testops.cloud", SecretStr("token"), project=1)

    # These should NOT raise
    AllureClient("http://demo.testops.cloud", SecretStr("token"), project=1)
    AllureClient("https://demo.testops.cloud", SecretStr("token"), project=1)


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
        client = AllureClient(endpoint, SecretStr(token), project=1)
        assert client._base_url == endpoint
        assert client._token.get_secret_value() == token
