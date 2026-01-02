"""Reusable AllureClient fixture with OAuth mocking."""

from collections.abc import AsyncGenerator

import pytest
import respx
from httpx import Response
from pydantic import SecretStr

from src.client import AllureClient


@pytest.fixture
async def allure_client() -> AsyncGenerator[AllureClient]:
    """
    Fixture that provides an initialized AllureClient with mocked OAuth.
    Uses respx for network mocking.
    """
    base_url = "https://allure.example.com"
    token = SecretStr("mock-token")

    with respx.mock:
        # Mock OAuth token exchange
        respx.post(f"{base_url}/api/uaa/oauth/token").mock(
            return_value=Response(200, json={"access_token": "mock-jwt-token", "expires_in": 3600})
        )

        async with AllureClient(base_url, token) as client:
            yield client
