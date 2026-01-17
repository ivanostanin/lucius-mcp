"""Integration tests for delete_test_case tool."""

import typing
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.services.test_case_service import DeleteResult
from src.tools.delete_test_case import delete_test_case


@pytest.fixture
def mock_service() -> typing.Generator[Mock]:
    """Mock TestCaseService."""
    with patch("src.tools.delete_test_case.TestCaseService") as mock:
        yield mock


@pytest.fixture
def mock_client() -> typing.Generator[Mock]:
    """Mock AllureClient."""
    with patch("src.tools.delete_test_case.AllureClient") as mock:
        instance = mock.return_value
        instance.__aenter__.return_value = instance
        yield mock


@pytest.mark.asyncio
@pytest.mark.test_id("1.5-INTEGRATION-001")
async def test_delete_test_case_tool_confirmation_required(mock_service: Mock, mock_client: Mock) -> None:
    """Test ID: 1.5-INTEGRATION-001 - Tool requires confirm=True parameter (P2)"""
    # GIVEN: Tool is called without confirm parameter (defaults to False)
    test_case_id = 123

    # WHEN: Tool is invoked
    result = await delete_test_case(test_case_id=test_case_id, confirm=False)

    # THEN: Returns warning message requiring confirmation
    assert "requires confirmation" in result
    assert "confirm=True" in result
    assert str(test_case_id) in result

    # AND: Service is never instantiated (safety check prevented execution)
    mock_service.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.test_id("1.5-INTEGRATION-002")
async def test_delete_test_case_tool_success_message(mock_service: Mock, mock_client: Mock) -> None:
    """Test ID: 1.5-INTEGRATION-002 - Tool returns correct success message (P2)"""
    # GIVEN: Service returns successful deletion result
    test_case_id = 456
    test_case_name = "Login Test"

    service_instance = mock_service.return_value
    service_instance.delete_test_case = AsyncMock()
    service_instance.delete_test_case.return_value = DeleteResult(
        test_case_id=test_case_id, status="archived", name=test_case_name, message="Archived successfully"
    )

    # WHEN: Tool is called with confirm=True
    result = await delete_test_case(test_case_id=test_case_id, confirm=True)

    # THEN: Returns success message with correct format
    assert result.startswith("✅ Archived Test Case")
    assert str(test_case_id) in result
    assert test_case_name in result
    assert f"Archived Test Case {test_case_id}: '{test_case_name}'" in result

    # AND: Service was called correctly
    service_instance.delete_test_case.assert_called_once_with(test_case_id)


@pytest.mark.asyncio
@pytest.mark.test_id("1.5-INTEGRATION-003")
async def test_delete_test_case_tool_already_deleted_message(mock_service: Mock, mock_client: Mock) -> None:
    """Test ID: 1.5-INTEGRATION-003 - Tool returns correct already-deleted message (P2)"""
    # GIVEN: Service returns already_deleted status (idempotent case)
    test_case_id = 789

    service_instance = mock_service.return_value
    service_instance.delete_test_case = AsyncMock()
    service_instance.delete_test_case.return_value = DeleteResult(
        test_case_id=test_case_id,
        status="already_deleted",
        message="Test case was already deleted or doesn't exist",
    )

    # WHEN: Tool is called with confirm=True
    result = await delete_test_case(test_case_id=test_case_id, confirm=True)

    # THEN: Returns already-deleted message with correct format
    assert result.startswith("ℹ️ Test Case")  # noqa: RUF001
    assert str(test_case_id) in result
    assert "already archived or doesn't exist" in result

    # AND: Service was called
    service_instance.delete_test_case.assert_called_once_with(test_case_id)


@pytest.mark.asyncio
@pytest.mark.test_id("1.5-INTEGRATION-004")
async def test_delete_test_case_tool_error_handling(mock_service: Mock, mock_client: Mock) -> None:
    """Test ID: 1.5-INTEGRATION-004 - Tool handles service errors gracefully (P2)"""
    # GIVEN: Service raises an exception
    test_case_id = 999

    service_instance = mock_service.return_value
    service_instance.delete_test_case = AsyncMock()
    service_instance.delete_test_case.side_effect = Exception("API connection failed")

    # WHEN: Tool is called with confirm=True
    result = await delete_test_case(test_case_id=test_case_id, confirm=True)

    # THEN: Returns error message without raising exception
    assert "Error archiving test case" in result
    assert "API connection failed" in result

    # AND: Service was called (exception caught by tool)
    service_instance.delete_test_case.assert_called_once_with(test_case_id)
