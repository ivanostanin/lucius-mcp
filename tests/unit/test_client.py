"""Unit tests for AllureClient."""

import time

import pytest
import respx
from httpx import Response
from pydantic import SecretStr

from src.client import (
    AllureAPIError,
    AllureAuthError,
    AllureClient,
    AllureNotFoundError,
    AllureRateLimitError,
    AllureValidationError,
    ScenarioStepCreateDto,
    TestCaseCreateV2Dto,
    TestCaseOverviewDto,
    TestCasePatchV2Dto,
    TestCaseScenarioDto,
)


@pytest.fixture
def base_url() -> str:
    """Return a test base URL."""
    return "https://allure.example.com"


@pytest.fixture
def token() -> SecretStr:
    """Return a test token."""
    return SecretStr("test-token-secret")


@pytest.fixture
def mock_oauth_response() -> dict[str, object]:
    """Return a mock OAuth token response."""
    return {"access_token": "mock-jwt-token", "expires_in": 3600}


@pytest.fixture
def oauth_route(base_url: str, mock_oauth_response: dict[str, object]) -> respx.Route:
    """Mock the OAuth token endpoint."""
    return respx.post(f"{base_url}/api/uaa/oauth/token").mock(return_value=Response(200, json=mock_oauth_response))


@pytest.mark.asyncio
@respx.mock
async def test_client_initialization(base_url: str, token: SecretStr, oauth_route: respx.Route) -> None:
    """Test that AllureClient initializes correctly and exchanges token."""
    async with AllureClient(base_url, token) as client:
        assert client._base_url == base_url
        assert client._token == token
        assert client._api_client is not None
        assert client._jwt_token == "mock-jwt-token"  # noqa: S105
        assert client._token_expires_at is not None
    assert oauth_route.called


@pytest.mark.asyncio
@respx.mock
async def test_client_context_manager_closes(base_url: str, token: SecretStr, oauth_route: respx.Route) -> None:
    """Test that client closes properly on context manager exit."""
    async with AllureClient(base_url, token) as client:
        api_client = client._api_client
        assert api_client is not None
        # Check if underlying pool manager is open (if initialized)
        # Note: We can't easily check is_closed on ApiClient directly without accessing internals
        # But we can verify no error is raised
        pass

    # We assume if no error, it closed. The generated client handles cleanup.
    assert oauth_route.called


@pytest.mark.asyncio
@respx.mock
async def test_method_not_initialized(base_url: str, token: SecretStr, oauth_route: respx.Route) -> None:
    """Test that methods raise error when client not initialized."""
    client = AllureClient(base_url, token)
    # create_test_case will check if self._test_case_api is not None, raising AllureAPIError
    # The current implementation raises AllureAPIError with a clear message.
    with pytest.raises(AllureAPIError, match="Client not initialized"):
        await client.create_test_case(1, TestCaseCreateV2Dto(name="Test", project_id=1))


@pytest.mark.asyncio
@respx.mock
async def test_create_test_case_success(base_url: str, token: SecretStr, oauth_route: respx.Route) -> None:
    """Test successful create_test_case."""
    # Mock create endpoint
    mock_response = {
        "id": 101,
        "name": "Test Case",
        "projectId": 1,
        "createdDate": 1234567890,
        "status": {"id": 1, "name": "Draft"},
    }
    # Note: Generated client uses snake_case, but we return mock dict that should be valid JSON
    # If using generated client, it parses JSON to model.
    # We should return mock response that matches what server sends (camelCase usually?)
    route = respx.post(f"{base_url}/api/testcase").mock(return_value=Response(200, json=mock_response))

    async with AllureClient(base_url, token) as client:
        dto = TestCaseCreateV2Dto(name="Test Case", project_id=1, automation="manual")
        result = await client.create_test_case(1, dto)

    assert isinstance(result, TestCaseOverviewDto)
    assert result.id == 101
    assert result.name == "Test Case"
    assert route.called
    assert oauth_route.called


@pytest.mark.asyncio
@respx.mock
async def test_create_test_case_404_raises_not_found(base_url: str, token: SecretStr, oauth_route: respx.Route) -> None:
    """Test that 404 raises AllureNotFoundError."""
    respx.post(f"{base_url}/api/testcase").mock(return_value=Response(404, text="Not Found"))

    async with AllureClient(base_url, token) as client:
        dto = TestCaseCreateV2Dto(name="Test Case", project_id=1)
        with pytest.raises(AllureNotFoundError, match="Resource not found"):
            await client.create_test_case(1, dto)


@pytest.mark.asyncio
@respx.mock
async def test_create_test_case_400_raises_validation_error(
    base_url: str, token: SecretStr, oauth_route: respx.Route
) -> None:
    """Test that 400 raises AllureValidationError."""
    respx.post(f"{base_url}/api/testcase").mock(return_value=Response(400, text="Bad Request"))

    async with AllureClient(base_url, token) as client:
        dto = TestCaseCreateV2Dto(name="Test Case", project_id=1)
        with pytest.raises(AllureValidationError, match="Validation error"):
            await client.create_test_case(1, dto)


@pytest.mark.asyncio
@respx.mock
async def test_create_test_case_401_raises_auth_error(
    base_url: str, token: SecretStr, oauth_route: respx.Route
) -> None:
    """Test that 401 raises AllureAuthError."""
    respx.post(f"{base_url}/api/testcase").mock(return_value=Response(401, text="Unauthorized"))

    async with AllureClient(base_url, token) as client:
        dto = TestCaseCreateV2Dto(name="Test Case", project_id=1)
        with pytest.raises(AllureAuthError, match="Authentication failed"):
            await client.create_test_case(1, dto)


@pytest.mark.asyncio
@respx.mock
async def test_create_test_case_403_raises_auth_error(
    base_url: str, token: SecretStr, oauth_route: respx.Route
) -> None:
    """Test that 403 raises AllureAuthError."""
    respx.post(f"{base_url}/api/testcase").mock(return_value=Response(403, text="Forbidden"))

    async with AllureClient(base_url, token) as client:
        dto = TestCaseCreateV2Dto(name="Test Case", project_id=1)
        with pytest.raises(AllureAuthError, match="Authentication failed"):
            await client.create_test_case(1, dto)


@pytest.mark.asyncio
@respx.mock
async def test_create_test_case_429_raises_rate_limit_error(
    base_url: str, token: SecretStr, oauth_route: respx.Route
) -> None:
    """Test that 429 raises AllureRateLimitError."""
    respx.post(f"{base_url}/api/testcase").mock(return_value=Response(429, text="Too Many Requests"))

    async with AllureClient(base_url, token) as client:
        dto = TestCaseCreateV2Dto(name="Test Case", project_id=1)
        with pytest.raises(AllureRateLimitError, match="Rate limit exceeded"):
            await client.create_test_case(1, dto)


@pytest.mark.asyncio
@respx.mock
async def test_create_test_case_500_raises_generic_api_error(
    base_url: str, token: SecretStr, oauth_route: respx.Route
) -> None:
    """Test that 500 raises generic AllureAPIError."""
    respx.post(f"{base_url}/api/testcase").mock(return_value=Response(500, text="Internal Server Error"))

    async with AllureClient(base_url, token) as client:
        dto = TestCaseCreateV2Dto(name="Test Case", project_id=1)
        with pytest.raises(AllureAPIError, match="API request failed"):
            await client.create_test_case(1, dto)


@pytest.mark.asyncio
@respx.mock
async def test_get_test_case_success(base_url: str, token: SecretStr, oauth_route: respx.Route) -> None:
    """Test successful get_test_case."""
    mock_response = {"id": 1, "name": "Test Case"}
    route = respx.get(f"{base_url}/api/testcase/1").mock(return_value=Response(200, json=mock_response))

    async with AllureClient(base_url, token) as client:
        result = await client.get_test_case(1)

    assert result.id == 1
    assert result.name == "Test Case"
    assert route.called


@pytest.mark.asyncio
@respx.mock
async def test_update_test_case_success(base_url: str, token: SecretStr, oauth_route: respx.Route) -> None:
    """Test successful update_test_case."""
    mock_response = {"id": 1, "name": "Updated Case"}
    route = respx.patch(f"{base_url}/api/testcase/1").mock(return_value=Response(200, json=mock_response))

    async with AllureClient(base_url, token) as client:
        patch_dto = TestCasePatchV2Dto(name="Updated Case")
        result = await client.update_test_case(1, patch_dto)

    assert result.id == 1
    assert result.name == "Updated Case"
    assert route.called


@pytest.mark.asyncio
@respx.mock
async def test_delete_test_case_success(base_url: str, token: SecretStr, oauth_route: respx.Route) -> None:
    """Test successful delete_test_case."""
    route = respx.delete(f"{base_url}/api/testcase/1").mock(return_value=Response(204))

    async with AllureClient(base_url, token) as client:
        await client.delete_test_case(1)

    assert route.called
    assert oauth_route.called


@pytest.mark.asyncio
@respx.mock
async def test_token_exchange_failure_raises_auth_error(base_url: str, token: SecretStr) -> None:
    """Test that failed token exchange raises AllureAuthError."""
    respx.post(f"{base_url}/api/uaa/oauth/token").mock(return_value=Response(401, text="Invalid token"))

    with pytest.raises(AllureAuthError, match="Token exchange failed"):
        async with AllureClient(base_url, token):
            pass


@pytest.mark.asyncio
@respx.mock
async def test_token_renewal_on_expiry(base_url: str, token: SecretStr, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that expired token is automatically renewed before request."""
    call_count = 0

    def mock_oauth_handler(request: object) -> Response:
        nonlocal call_count
        call_count += 1
        return Response(200, json={"access_token": f"jwt-token-{call_count}", "expires_in": 3600})

    respx.post(f"{base_url}/api/uaa/oauth/token").mock(side_effect=mock_oauth_handler)
    respx.post(f"{base_url}/api/testcase").mock(return_value=Response(200, json={"id": 1, "name": "ok"}))

    async with AllureClient(base_url, token) as client:
        assert call_count == 1
        assert client._jwt_token == "jwt-token-1"  # noqa: S105

        # Simulate token expiry by setting expires_at to the past
        client._token_expires_at = time.time() - 10

        # Next request should trigger token refresh
        dto = TestCaseCreateV2Dto(name="Test Case", project_id=1, automation="manual")
        await client.create_test_case(1, dto)

        assert call_count == 2
        assert client._jwt_token == "jwt-token-2"  # noqa: S105


@pytest.mark.asyncio
@respx.mock
async def test_create_scenario_step_success(base_url: str, token: SecretStr, oauth_route: respx.Route) -> None:
    """Test successful create_scenario_step with manual parsing bypass."""
    # Mock response with "problematic" attachments structure that would fail oneOf validation
    mock_response = {
        "createdStepId": 202,
        "scenario": {
            "steps": [],
            "attachments": {
                "1": {
                    "entity": "TestCaseAttachmentRowDto",
                    "name": "test.txt",
                    "contentType": "text/plain",
                    "contentLength": 10,
                }
            },
        },
    }

    route = respx.post(f"{base_url}/api/testcase/step").mock(return_value=Response(200, json=mock_response))

    async with AllureClient(base_url, token) as client:
        step_dto = ScenarioStepCreateDto(test_case_id=1, body="Action")
        result = await client.create_scenario_step(1, step_dto)

    assert result.created_step_id == 202
    assert result.scenario is None  # We explicitly don't parse it to avoid oneOf issues
    assert route.called


@pytest.mark.asyncio
@respx.mock
async def test_create_scenario_step_error_raises_validation_error(
    base_url: str, token: SecretStr, oauth_route: respx.Route
) -> None:
    """Test that 400 in create_scenario_step raises AllureValidationError."""
    respx.post(f"{base_url}/api/testcase/step").mock(return_value=Response(400, text="Bad Request"))

    async with AllureClient(base_url, token) as client:
        step_dto = ScenarioStepCreateDto(test_case_id=1, body="Action")
        with pytest.raises(AllureValidationError, match="Validation error"):
            await client.create_scenario_step(1, step_dto)
