"""E2E test for client connectivity and sandbox authentication.
Verified as part of Story 1.2 code review.
"""

import pytest
import respx
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
async def test_client_connectivity_e2e(allure_client: AllureClient) -> None:
    """Verify that AllureClient can exchange token and maintain session."""
    async with allure_client as client:
        assert len(client._jwt_token) > 64
        assert client._is_entered is True
