import pytest

from src.client import AllureClient
from src.tools.create_test_case import create_test_case
from src.tools.update_test_case import update_test_case
from tests.e2e.helpers.cleanup import CleanupTracker


@pytest.fixture
def run_name(test_run_id):
    return f"[{test_run_id}] Tool Output Test"


@pytest.mark.asyncio
async def test_create_tool_success_output(
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    project_id: int,
    run_name: str,
):
    """Verify create tool output is human friendly."""
    result = await create_test_case(
        project_id=project_id,
        name=run_name,
        description="Testing tool output",
    )

    # Check format: "Created Test Case ID: <id> Name: <name>"
    assert "Created Test Case ID:" in result
    assert f"Name: {run_name}" in result
    assert "{" not in result  # Should not be JSON

    # Extract ID to clean up
    # Expected format: "Created Test Case ID: 123 Name: ..."
    try:
        id_part = result.split("ID:")[1].split("Name:")[0].strip()
        test_case_id = int(id_part)
        cleanup_tracker.track_test_case(test_case_id)
    except (IndexError, ValueError):
        pytest.fail(f"Could not parse ID from tool output: {result}")


@pytest.mark.asyncio
async def test_update_tool_success_output(
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    project_id: int,
    run_name: str,
):
    """Verify update tool output is human friendly."""
    # Setup: Create via service first
    from src.services.test_case_service import TestCaseService

    service = TestCaseService(client=allure_client)

    created = await service.create_test_case(name=run_name)
    cleanup_tracker.track_test_case(created.id)

    # Test Update Tool
    result = await update_test_case(test_case_id=created.id, description="New Desc")

    # Check format: "Test Case <id> updated successfully. Changes: description"
    assert f"Test Case {created.id} updated successfully" in result
    assert "Changes: description" in result


@pytest.mark.asyncio
async def test_update_tool_not_found_error(project_id: int):
    """Verify error output for non-existent ID."""
    # Use a likely non-existent ID
    fake_id = 999999999

    # The tool raises exceptions (no try/except in tools).
    # Therefore we expect an exception, not a return value.

    with pytest.raises(Exception) as excinfo:
        await update_test_case(test_case_id=fake_id, description="Should fail")

    # Use string conversion of exception to check message
    error_msg = str(excinfo.value)
    assert "not found" in error_msg or "404" in error_msg


@pytest.mark.asyncio
async def test_create_tool_validation_error(project_id: int):
    """Verify validation error output."""
    # Create with invalid project_id

    with pytest.raises(Exception) as excinfo:
        await create_test_case(
            project_id=-1,  # Invalid project ID
            name="Invalid Project",
        )

    error_msg = str(excinfo.value)
    assert "Project ID is required" in error_msg or "must be positive" in error_msg
