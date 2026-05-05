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
        instance = Mock()
        instance.get_base_url.return_value = "https://example.com"
        instance.get_project.return_value = 99
        mock.from_env.return_value.__aenter__.return_value = instance
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
        project_id=project_id,
        name=name,
        description=description,
        steps=steps,
        tags=tags,
        custom_fields=custom_fields,
        test_layer_id=5,
        output_format="plain",
    )

    assert "777" in result
    assert name in result
    assert "Test Case URL: https://example.com/project/99/test-cases/777" in result

    # Verify service call
    service_instance.create_test_case.assert_called_once()
    call_args = service_instance.create_test_case.call_args
    # Verify kwargs were passed correctly
    # We check that the arguments passed match what we expect
    # Since call_args can be (args, kwargs), we might need to inspect closely.
    # The tool calls: await service.create_test_case(name=..., ...)
    # So all are kwargs.

    actual_kwargs = call_args.kwargs
    assert actual_kwargs["name"] == name
    assert actual_kwargs["custom_fields"] == custom_fields
    assert actual_kwargs["steps"] == steps
    assert actual_kwargs["test_layer_id"] == 5


@pytest.mark.asyncio
async def test_create_test_case_tool_with_issues(mock_service: Mock, mock_client: Mock) -> None:
    """Verify tool creates service and calls create_test_case with issues."""
    name = "Tool Test Issues"
    issues = ["PROJ-123"]

    service_instance = mock_service.return_value
    service_instance.create_test_case = AsyncMock()
    service_instance.create_test_case.return_value = Mock(id=778, name=name)

    result = await create_test_case(
        name=name,
        issues=issues,
        output_format="plain",
    )

    assert "778" in result
    assert "Test Case URL: https://example.com/project/99/test-cases/778" in result
    service_instance.create_test_case.assert_called_once()
    actual_kwargs = service_instance.create_test_case.call_args.kwargs
    assert actual_kwargs["name"] == name
    assert actual_kwargs["issues"] == issues


@pytest.mark.asyncio
async def test_create_test_case_tool_json_includes_url(mock_service: Mock, mock_client: Mock) -> None:
    name = "Tool Test JSON"

    service_instance = mock_service.return_value
    service_instance.create_test_case = AsyncMock()
    service_instance.create_test_case.return_value = Mock(id=779, name=name)

    output = await create_test_case(name=name, output_format="json")

    assert output.content == []
    assert output.structured_content["id"] == 779
    assert output.structured_content["url"] == "https://example.com/project/99/test-cases/779"
