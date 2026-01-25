import pytest

from src.client import AllureClient
from src.services.test_case_service import TestCaseService
from tests.e2e.helpers.cleanup import CleanupTracker


@pytest.mark.asyncio
@pytest.mark.test_id("1.5-E2E-001")
async def test_delete_test_case_e2e(
    allure_client: AllureClient,
    project_id: int,
    cleanup_tracker: CleanupTracker,
) -> None:
    """Test ID: 1.5-E2E-001 - Soft Delete Test Case (P0)

    Story 1.5: Soft Delete & Archive
    Test Design: test-design-story-1.5.md

    Validates that delete_test_case sets status to 'Archived' (not 404) and
    that the operation is idempotent.
    """
    service = TestCaseService(client=allure_client)

    # GIVEN: A test case exists in Allure TestOps
    created = await service.create_test_case(
        name="E2E Delete Test",
        description="Temporary test case for delete verification",
    )
    assert created.id is not None
    test_case_id = created.id
    cleanup_tracker.track_test_case(test_case_id)

    # WHEN: The test case is deleted
    result = await service.delete_test_case(test_case_id)

    # THEN: The test case is marked as archived (not hard deleted)
    assert result.status == "archived"
    assert result.test_case_id == test_case_id
    assert result.name == "E2E Delete Test"

    # AND: Deleting again is idempotent
    result_again = await service.delete_test_case(test_case_id)
    assert result_again.status == "archived"
