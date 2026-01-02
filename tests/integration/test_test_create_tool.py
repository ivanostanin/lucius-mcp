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

    # Setup service mock
    service_instance = mock_service.return_value
    service_instance.create_test_case = AsyncMock()
    service_instance.create_test_case.return_value = Mock(id=777, name=name)

    result = await create_test_case(project_id=project_id, name=name, description=description, steps=steps, tags=tags)

    assert "777" in result
    assert name in result

    # Verify service call
    service_instance.create_test_case.assert_called_once()
    call_args = service_instance.create_test_case.call_args
    arg_project = call_args[0][0]
    arg_dto = call_args[0][1]

    assert arg_project == project_id
    assert arg_dto.name == name
    assert arg_dto.description == description
    assert len(arg_dto.scenario.steps) == 2
    assert arg_dto.scenario.steps[0].actual_instance.body == "A"
    # assert arg_dto.scenario.steps[0].type == "BodyStep" # if we want to check type
    assert arg_dto.scenario.steps[1].actual_instance.body == "B"
    # assert arg_dto.scenario.steps[1].type == "ExpectedBodyStep"
    assert arg_dto.tags[0].name == "t1"
