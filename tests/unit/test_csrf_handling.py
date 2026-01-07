import httpx
import pytest
import respx
from pydantic import SecretStr

from src.client import AllureClient
from src.client.generated.models.test_case_create_v2_dto import TestCaseCreateV2Dto


@pytest.mark.asyncio
@respx.mock
async def test_csrf_token_capture_and_injection() -> None:
    """Verify that CSRF token is captured from auth and used in subsequent calls."""
    base_url = "https://allure.example.com"
    token = SecretStr("api-token")

    # Mock auth endpoint
    auth_route = respx.post(f"{base_url}/api/uaa/oauth/token").mock(
        return_value=httpx.Response(
            200,
            json={"access_token": "mock-jwt", "expires_in": 3600},
            headers={"Set-Cookie": "XSRF-TOKEN=test-csrf-token; Path=/; Secure"},
        )
    )

    # Mock an API call (e.g., create_test_case)
    api_route = respx.post(f"{base_url}/api/testcase").mock(
        return_value=httpx.Response(200, json={"id": 123, "name": "Test Case"})
    )

    async with AllureClient(base_url, token) as client:
        # The __aenter__ calls _ensure_valid_token which calls _get_jwt_token
        assert client._csrf_token == "test-csrf-token"

        # Now make an API call
        data = TestCaseCreateV2Dto(name="Test Case", project_id=1)
        await client.create_test_case(project_id=1, data=data)

        # Verify the API call had the CSRF headers and cookies
        last_request = api_route.calls.last.request
        assert last_request.headers["X-XSRF-TOKEN"] == "test-csrf-token"
        assert "XSRF-TOKEN=test-csrf-token" in last_request.headers.get("Cookie", "")
        assert last_request.headers["Authorization"] == "Bearer mock-jwt"


@pytest.mark.asyncio
@respx.mock
async def test_logging_on_failure(caplog: pytest.LogCaptureFixture) -> None:
    """Verify that API failures are logged with exception details."""
    base_url = "https://allure.example.com"
    token = SecretStr("api-token")

    # Mock auth success
    respx.post(f"{base_url}/api/uaa/oauth/token").mock(
        return_value=httpx.Response(200, json={"access_token": "jwt", "expires_in": 3600})
    )

    # Mock API failure
    respx.post(f"{base_url}/api/testcase").mock(return_value=httpx.Response(400, content="Bad Request Data"))

    async with AllureClient(base_url, token) as client:
        data = TestCaseCreateV2Dto(name="Test Case", project_id=1)
        with pytest.raises(Exception):  # AllureValidationError
            await client.create_test_case(project_id=1, data=data)

    # Check logs
    assert "API request failed with status 400" in caplog.text
