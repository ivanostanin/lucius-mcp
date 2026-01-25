import pytest

from src.client import AllureClient
from src.client.exceptions import TestCaseNotFoundError
from src.services.search_service import SearchService
from src.services.test_case_service import TestCaseService
from src.tools.search import _format_test_case_details
from tests.e2e.helpers.cleanup import CleanupTracker


@pytest.mark.asyncio
async def test_get_test_case_details_with_full_content(
    allure_client: AllureClient,
    project_id: int,
    cleanup_tracker: CleanupTracker,
) -> None:
    """Test get_test_case_details with a test case that has steps, description, and preconditions."""

    # Create a test case with full details to ensure we have content to verify
    case_service = TestCaseService(client=allure_client)
    created = await case_service.create_test_case(
        name="E2E Test: Get Details with Full Content",
        description="This test case has a description for E2E testing",
        steps=[
            {"action": "Step 1: Perform action", "expected": "Expected result 1"},
            {"action": "Step 2: Verify outcome", "expected": "Expected result 2"},
        ],
        tags=["e2e-test", "get-details"],
    )
    test_case_id = created.id
    assert test_case_id is not None
    cleanup_tracker.track_test_case(test_case_id)

    # Now retrieve the details
    search_service = SearchService(client=allure_client)
    details = await search_service.get_test_case_details(test_case_id)
    text = _format_test_case_details(details)

    # Verify all expected content is present
    assert str(test_case_id) in text
    assert details.test_case.name in text
    assert "Status:" in text

    # Verify we have steps and description (from our created test case)
    assert "Steps:" in text
    assert "Description:" in text
    assert "Step 1: Perform action" in text
    assert "Expected result 1" in text

    # Verify tags are present
    assert "Tags:" in text
    assert "e2e-test" in text


@pytest.mark.asyncio
async def test_get_test_case_details_not_found(
    allure_client: AllureClient,
) -> None:
    service = SearchService(client=allure_client)
    with pytest.raises(TestCaseNotFoundError):
        await service.get_test_case_details(99999999)
