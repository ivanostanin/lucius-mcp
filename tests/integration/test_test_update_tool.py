import typing
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.services.test_case_service import TestCaseUpdate
from src.tools.update_test_case import update_test_case


@pytest.fixture
def mock_service() -> typing.Generator[Mock]:
    with patch("src.tools.update_test_case.TestCaseService") as mock:
        yield mock


@pytest.fixture
def mock_client() -> typing.Generator[Mock]:
    with patch("src.tools.update_test_case.AllureClient") as mock:
        instance = mock.return_value
        instance.__aenter__.return_value = instance
        yield mock


@pytest.mark.asyncio
async def test_update_test_case_tool_issues(mock_service: Mock, mock_client: Mock) -> None:
    """Verify update tool handles issue arguments."""

    test_case_id = 99
    issues = ["PROJ-1"]
    remove_issues = ["PROJ-2"]
    clear_issues = True

    service_instance = mock_service.return_value
    # mock get_test_case to return something for validation/diff logic
    mock_current = Mock(id=test_case_id, name="Old", issues=[])
    service_instance.get_test_case = AsyncMock(return_value=mock_current)

    # mock update
    mock_updated = Mock(id=test_case_id, name="Old", issues=[])
    service_instance.update_test_case = AsyncMock(return_value=mock_updated)

    result = await update_test_case(
        test_case_id=test_case_id,
        issues=issues,
        remove_issues=remove_issues,
        clear_issues=clear_issues,
    )

    assert "99" in result
    assert "added 1 issues (PROJ-1)" in result
    assert "removed 1 issues (PROJ-2)" in result
    assert "cleared all issues" in result

    service_instance.update_test_case.assert_called_once()
    call_args = service_instance.update_test_case.call_args
    # call_args[0] = (test_case_id, update_data)
    assert call_args[0][0] == test_case_id
    update_data = call_args[0][1]

    assert isinstance(update_data, TestCaseUpdate)
    assert update_data.issues == issues
    assert update_data.remove_issues == remove_issues
    assert update_data.clear_issues == clear_issues
