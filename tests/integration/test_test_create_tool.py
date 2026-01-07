import typing
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.tools.create_test_case import create_test_case


@pytest.fixture
def mock_service() -> typing.Generator[Mock]:
    with patch("src.tools.create_test_case.TestCaseService") as mock:
        yield mock


@pytest.fixture
def mock_client() -> typing.Generator[Mock]:
    with patch("src.tools.create_test_case.AllureClient") as mock:
        instance = mock.return_value
        instance.__aenter__.return_value = instance
        yield mock


@pytest.mark.asyncio
async def test_create_test_case_tool_success(mock_service: Mock, mock_client: Mock) -> None:
    """Verify tool creates service and calls create_test_case."""

    project_id = 99
    name = "Tool Test"
    description = "Desc"
    steps = [{"action": "A", "expected": "B"}]
    tags = ["t1"]
    custom_fields = {"Layer": "UI", "Priority": "High"}

    # Setup service mock
    service_instance = mock_service.return_value
    service_instance.create_test_case = AsyncMock()
    service_instance.create_test_case.return_value = Mock(id=777, name=name)

    result = await create_test_case(
        project_id=project_id, name=name, description=description, steps=steps, tags=tags, custom_fields=custom_fields
    )

    assert "777" in result
    assert name in result

    # Verify service call
    service_instance.create_test_case.assert_called_once()
    call_args = service_instance.create_test_case.call_args
    # Verify kwargs were passed correctly
    # We check that the arguments passed match what we expect
    # Since call_args can be (args, kwargs), we might need to inspect closely.
    # The tool calls: await service.create_test_case(project_id=..., ...)
    # So all are kwargs.

    actual_kwargs = call_args.kwargs
    assert actual_kwargs["project_id"] == project_id
    assert actual_kwargs["name"] == name
    assert actual_kwargs["custom_fields"] == custom_fields
    assert actual_kwargs["steps"] == steps
