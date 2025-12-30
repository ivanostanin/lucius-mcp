import pytest
from starlette.requests import Request
from starlette.types import Scope, Receive, Send

# Import will fail initially
from src.utils.error import AllureAPIError, ResourceNotFoundError, agent_hint_handler


def test_allure_api_error_structure():
    err = AllureAPIError("Something went wrong", suggestions=["Check configuration"])
    assert str(err) == "Something went wrong"
    assert "Check configuration" in err.suggestions


def test_specific_error_types():
    err = ResourceNotFoundError("Test Case 123 not found")
    assert isinstance(err, AllureAPIError)
    assert "Test Case 123 not found" in str(err)
    # Check if suggestions are populated by default or passed
    assert err.suggestions


@pytest.mark.asyncio
async def test_agent_hint_format():
    # Mocking a basic request
    scope: Scope = {"type": "http"}

    async def receive() -> dict:
        return {}

    async def send(message: dict) -> None:
        pass

    request = Request(scope, receive)

    exc = ResourceNotFoundError("Item missing", suggestions=["Create item first"])

    response = await agent_hint_handler(request, exc)

    assert response.status_code == 404  # Should map to 404
    body = response.body.decode()

    # Check Agent Hint format
    assert "❌ Error: Item missing" in body
    assert "Suggestions:" in body
    assert "- Create item first" in body
