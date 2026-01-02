"""E2E test for client connectivity and sandbox authentication.
Verified as part of Story 1.2 code review.
"""

import pytest
import respx
from httpx import Response
from pydantic import SecretStr

from src.client import AllureClient


@pytest.fixture
def base_url() -> str:
    return "https://demo.testops.cloud"


@pytest.fixture
def token() -> SecretStr:
    return SecretStr("test-api-token")


@pytest.mark.asyncio
@respx.mock
async def test_client_connectivity_e2e(base_url: str, token: SecretStr) -> None:
    """Verify that AllureClient can exchange token and maintain session."""

    # Mock OAuth exchange
    respx.post(f"{base_url}/api/uaa/oauth/token").mock(
        return_value=Response(200, json={"access_token": "mock-jwt-token", "expires_in": 3600})
    )

    # Mock a simple connectivity check (e.g., getting current user or similar)
    # For now, we just verify the context manager entry works.
    async with AllureClient(base_url, token) as client:
        assert client._jwt_token == "mock-jwt-token"  # noqa: S105
        assert client._is_entered is True

    assert client._is_entered is False
