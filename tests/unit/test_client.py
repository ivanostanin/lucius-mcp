"""Unit tests for AllureClient."""

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


@pytest.mark.asyncio
async def test_client_initialization(base_url: str, token: SecretStr) -> None:
    """Test that AllureClient initializes correctly."""
    async with AllureClient(base_url, token) as client:
        assert client._base_url == base_url
        assert client._token == token
        assert client._client is not None


@pytest.mark.asyncio
async def test_client_context_manager_closes(base_url: str, token: SecretStr) -> None:
    """Test that client closes properly on context manager exit."""
    async with AllureClient(base_url, token) as client:
        http_client = client._client
        assert http_client is not None
        assert not http_client.is_closed

    # After exiting context manager
    assert http_client.is_closed


@pytest.mark.asyncio
async def test_request_not_initialized(base_url: str, token: SecretStr) -> None:
    """Test that _request raises error when client not initialized."""
    client = AllureClient(base_url, token)
    with pytest.raises(AllureAPIError, match="Client not initialized"):
        await client._request("GET", "/api/test")


@pytest.mark.asyncio
@respx.mock
async def test_request_success(base_url: str, token: SecretStr) -> None:
    """Test successful HTTP request."""
    route = respx.get(f"{base_url}/api/test").mock(return_value=Response(200, json={"status": "ok"}))

    async with AllureClient(base_url, token) as client:
        response = await client._request("GET", "/api/test")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert route.called


@pytest.mark.asyncio
@respx.mock
async def test_request_404_raises_not_found(base_url: str, token: SecretStr) -> None:
    """Test that 404 raises AllureNotFoundError."""
    respx.get(f"{base_url}/api/notfound").mock(return_value=Response(404, text="Not Found"))

    async with AllureClient(base_url, token) as client:
        with pytest.raises(AllureNotFoundError, match="Resource not found"):
            await client._request("GET", "/api/notfound")


@pytest.mark.asyncio
@respx.mock
async def test_request_400_raises_validation_error(base_url: str, token: SecretStr) -> None:
    """Test that 400 raises AllureValidationError."""
    respx.post(f"{base_url}/api/create").mock(return_value=Response(400, text="Bad Request"))

    async with AllureClient(base_url, token) as client:
        with pytest.raises(AllureValidationError, match="Validation error"):
            await client._request("POST", "/api/create")


@pytest.mark.asyncio
@respx.mock
async def test_request_401_raises_auth_error(base_url: str, token: SecretStr) -> None:
    """Test that 401 raises AllureAuthError."""
    respx.get(f"{base_url}/api/secure").mock(return_value=Response(401, text="Unauthorized"))

    async with AllureClient(base_url, token) as client:
        with pytest.raises(AllureAuthError, match="Authentication failed"):
            await client._request("GET", "/api/secure")


@pytest.mark.asyncio
@respx.mock
async def test_request_403_raises_auth_error(base_url: str, token: SecretStr) -> None:
    """Test that 403 raises AllureAuthError."""
    respx.get(f"{base_url}/api/forbidden").mock(return_value=Response(403, text="Forbidden"))

    async with AllureClient(base_url, token) as client:
        with pytest.raises(AllureAuthError, match="Authentication failed"):
            await client._request("GET", "/api/forbidden")


@pytest.mark.asyncio
@respx.mock
async def test_request_429_raises_rate_limit_error(base_url: str, token: SecretStr) -> None:
    """Test that 429 raises AllureRateLimitError."""
    respx.get(f"{base_url}/api/rate-limit").mock(return_value=Response(429, text="Too Many Requests"))

    async with AllureClient(base_url, token) as client:
        with pytest.raises(AllureRateLimitError, match="Rate limit exceeded"):
            await client._request("GET", "/api/rate-limit")


@pytest.mark.asyncio
@respx.mock
async def test_request_500_raises_generic_api_error(base_url: str, token: SecretStr) -> None:
    """Test that 500 raises generic AllureAPIError."""
    respx.get(f"{base_url}/api/error").mock(return_value=Response(500, text="Internal Server Error"))

    async with AllureClient(base_url, token) as client:
        with pytest.raises(AllureAPIError, match="API request failed"):
            await client._request("GET", "/api/error")


@pytest.mark.asyncio
async def test_placeholder_methods_not_implemented(base_url: str, token: SecretStr) -> None:
    """Test that placeholder methods raise NotImplementedError."""
    async with AllureClient(base_url, token) as client:
        with pytest.raises(NotImplementedError):
            await client.create_test_case(1, {})

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
