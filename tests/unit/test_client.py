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
        assert client._client is not None
        assert client._jwt_token == "mock-jwt-token" # noqa: S105
        assert client._token_expires_at is not None
    assert oauth_route.called


@pytest.mark.asyncio
@respx.mock
async def test_client_context_manager_closes(base_url: str, token: SecretStr, oauth_route: respx.Route) -> None:
    """Test that client closes properly on context manager exit."""
    async with AllureClient(base_url, token) as client:
        http_client = client._client
        assert http_client is not None
        assert not http_client.is_closed

    # After exiting context manager
    assert http_client.is_closed
    assert oauth_route.called


@pytest.mark.asyncio
async def test_request_not_initialized(base_url: str, token: SecretStr) -> None:
    """Test that _request raises error when client not initialized."""
    client = AllureClient(base_url, token)
    with pytest.raises(AllureAPIError, match="Client not initialized"):
        await client._request("GET", "/api/test")


@pytest.mark.asyncio
@respx.mock
async def test_request_success(base_url: str, token: SecretStr, oauth_route: respx.Route) -> None:
    """Test successful HTTP request."""
    route = respx.get(f"{base_url}/api/test").mock(return_value=Response(200, json={"status": "ok"}))

    async with AllureClient(base_url, token) as client:
        response = await client._request("GET", "/api/test")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert route.called
    assert oauth_route.called


@pytest.mark.asyncio
@respx.mock
async def test_request_404_raises_not_found(base_url: str, token: SecretStr, oauth_route: respx.Route) -> None:
    """Test that 404 raises AllureNotFoundError."""
    respx.get(f"{base_url}/api/notfound").mock(return_value=Response(404, text="Not Found"))

    async with AllureClient(base_url, token) as client:
        with pytest.raises(AllureNotFoundError, match="Resource not found"):
            await client._request("GET", "/api/notfound")


@pytest.mark.asyncio
@respx.mock
async def test_request_400_raises_validation_error(base_url: str, token: SecretStr, oauth_route: respx.Route) -> None:
    """Test that 400 raises AllureValidationError."""
    respx.post(f"{base_url}/api/create").mock(return_value=Response(400, text="Bad Request"))

    async with AllureClient(base_url, token) as client:
        with pytest.raises(AllureValidationError, match="Validation error"):
            await client._request("POST", "/api/create")


@pytest.mark.asyncio
@respx.mock
async def test_request_401_raises_auth_error(base_url: str, token: SecretStr, oauth_route: respx.Route) -> None:
    """Test that 401 raises AllureAuthError."""
    respx.get(f"{base_url}/api/secure").mock(return_value=Response(401, text="Unauthorized"))

    async with AllureClient(base_url, token) as client:
        with pytest.raises(AllureAuthError, match="Authentication failed"):
            await client._request("GET", "/api/secure")


@pytest.mark.asyncio
@respx.mock
async def test_request_403_raises_auth_error(base_url: str, token: SecretStr, oauth_route: respx.Route) -> None:
    """Test that 403 raises AllureAuthError."""
    respx.get(f"{base_url}/api/forbidden").mock(return_value=Response(403, text="Forbidden"))

    async with AllureClient(base_url, token) as client:
        with pytest.raises(AllureAuthError, match="Authentication failed"):
            await client._request("GET", "/api/forbidden")


@pytest.mark.asyncio
@respx.mock
async def test_request_429_raises_rate_limit_error(base_url: str, token: SecretStr, oauth_route: respx.Route) -> None:
    """Test that 429 raises AllureRateLimitError."""
    respx.get(f"{base_url}/api/rate-limit").mock(return_value=Response(429, text="Too Many Requests"))

    async with AllureClient(base_url, token) as client:
        with pytest.raises(AllureRateLimitError, match="Rate limit exceeded"):
            await client._request("GET", "/api/rate-limit")


@pytest.mark.asyncio
@respx.mock
async def test_request_500_raises_generic_api_error(base_url: str, token: SecretStr, oauth_route: respx.Route) -> None:
    """Test that 500 raises generic AllureAPIError."""
    respx.get(f"{base_url}/api/error").mock(return_value=Response(500, text="Internal Server Error"))

    async with AllureClient(base_url, token) as client:
        with pytest.raises(AllureAPIError, match="API request failed"):
            await client._request("GET", "/api/error")


@pytest.mark.asyncio
@respx.mock
async def test_placeholder_methods_not_implemented(base_url: str, token: SecretStr, oauth_route: respx.Route) -> None:
    """Test that placeholder methods raise NotImplementedError."""
    async with AllureClient(base_url, token) as client:
        with pytest.raises(NotImplementedError):
            await client.get_test_case(1)

        with pytest.raises(NotImplementedError):
            await client.update_test_case(1, {})

        with pytest.raises(NotImplementedError):
            await client.delete_test_case(1)

        with pytest.raises(NotImplementedError):
            await client.create_shared_step(1, {})

        with pytest.raises(NotImplementedError):
            await client.list_shared_steps(1)

        with pytest.raises(NotImplementedError):
            await client.update_shared_step(1, {})

        with pytest.raises(NotImplementedError):
            await client.delete_shared_step(1)

        with pytest.raises(NotImplementedError):
            await client.list_test_cases(1)

        with pytest.raises(NotImplementedError):
            await client.search_test_cases(1, "query")


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
    respx.get(f"{base_url}/api/test").mock(return_value=Response(200, json={"status": "ok"}))

    async with AllureClient(base_url, token) as client:
        assert call_count == 1
        assert client._jwt_token == "jwt-token-1" # noqa: S105

        # Simulate token expiry by setting expires_at to the past
        client._token_expires_at = time.time() - 10

        # Next request should trigger token refresh
        await client._request("GET", "/api/test")

        assert call_count == 2
        assert client._jwt_token == "jwt-token-2" # noqa: S105
