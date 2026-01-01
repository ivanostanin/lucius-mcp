import pytest
from starlette.requests import Request
from starlette.types import Scope

from src.utils.error import (
    AllureAPIError,
    AuthenticationError,
    ResourceNotFoundError,
    ValidationError,
    agent_hint_handler,
)


@pytest.fixture
def mock_request():
    scope: Scope = {"type": "http"}

    async def receive():
        return {}

    request = Request(scope, receive)
    return request


@pytest.mark.asyncio
async def test_resource_not_found(mock_request):
    exc = ResourceNotFoundError("Test Case 123 not found")
    response = await agent_hint_handler(mock_request, exc)

    assert response.status_code == 404
    body = response.body.decode()
    assert "❌ Error: Test Case 123 not found" in body
    assert "Suggestions:" in body
    assert "Check if the ID is correct" in body


@pytest.mark.asyncio
async def test_validation_error(mock_request):
    exc = ValidationError("Invalid email format")
    response = await agent_hint_handler(mock_request, exc)

    assert response.status_code == 400
    body = response.body.decode()
    assert "❌ Error: Invalid email format" in body


@pytest.mark.asyncio
async def test_authentication_error(mock_request):
    exc = AuthenticationError("Invalid token")
    response = await agent_hint_handler(mock_request, exc)

    assert response.status_code == 401
    body = response.body.decode()
    assert "❌ Error: Invalid token" in body
    assert "Check ALLURE_API_TOKEN" in body


@pytest.mark.asyncio
async def test_unexpected_exception(mock_request):
    exc = ValueError("Database connection failed")
    response = await agent_hint_handler(mock_request, exc)

    assert response.status_code == 500
    body = response.body.decode()
    assert "❌ Unexpected Error: Database connection failed" in body
    assert "check the logs" in body
    # Stack trace should NOT be in the body for generic errors to avoid leaking internals
    assert "Traceback" not in body


def test_error_hierarchy():
    """Ensure all custom errors inherit from AllureAPIError"""
    assert issubclass(ResourceNotFoundError, AllureAPIError)
    assert issubclass(ValidationError, AllureAPIError)
    assert issubclass(AuthenticationError, AllureAPIError)
