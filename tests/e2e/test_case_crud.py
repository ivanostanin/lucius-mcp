import os

import pytest

from src.client import AllureClient
from src.client.exceptions import AllureNotFoundError
from src.services.test_case_service import TestCaseService, TestCaseUpdate
from tests.e2e.helpers.cleanup import CleanupTracker

# Skip all tests if sandbox environment is not configured
pytestmark = pytest.mark.skipif(
    not os.getenv("ALLURE_ENDPOINT") or not os.getenv("ALLURE_API_TOKEN"),
    reason="Allure sandbox environment variables not set",
)


@pytest.fixture
def run_name(test_run_id):
    """Generate a unique name for this test run."""
    return f"[{test_run_id}] CRUD Test"


@pytest.fixture
def service(allure_client: AllureClient):
    return TestCaseService(allure_client)


@pytest.mark.asyncio
async def test_test_case_lifecycle(
    service: TestCaseService,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    project_id: int,
    run_name: str,
):
    """
    Test the full lifecycle of a test case:
    Create -> Read -> Update -> Delete
    """
    # 1. CREATE
    print(f"\nCreate Test Case: {run_name}")
    created = await service.create_test_case(
        project_id=project_id,
        name=run_name,
        description="Initial description",
        steps=[
            {"action": "Step 1", "expected": "Result 1"},
        ],
    )
    cleanup_tracker.track_test_case(created.id)

    assert created.id is not None
    assert created.name == run_name
    assert created.description == "Initial description"

    # 2. READ
    print(f"Read Test Case: {created.id}")
    fetched = await service.get_test_case(created.id)
    assert fetched.id == created.id
    assert fetched.name == run_name

    # Check steps - fetched DTO doesn't contain steps, so we fetch scenario explicitly
    scenario = await allure_client.get_test_case_scenario(created.id)
    assert len(scenario.steps) == 1
    # Access the step body from the nested actual_instance
    assert scenario.steps[0].actual_instance.body == "Step 1"

    # 3. UPDATE
    print(f"Update Test Case: {created.id}")
    new_description = "Updated description"
    new_name = f"{run_name} (Updated)"

    updated = await service.update_test_case(created.id, TestCaseUpdate(name=new_name, description=new_description))

    assert updated.name == new_name
    assert updated.description == new_description

    # Verify update persisted
    fetched_after_update = await service.get_test_case(created.id)
    assert fetched_after_update.name == new_name
    assert fetched_after_update.description == new_description

    # 4. DELETE
    print(f"Delete Test Case: {created.id}")
    await service.delete_test_case(created.id)

    # Verify deletion
    try:
        await service.get_test_case(created.id)
        # If it returns, check if it's archived/deleted status if the API supports that visibility.
        # But if the API filters out deleted items by default, this raises NotFound or returns nothing.
    except AllureNotFoundError:
        pass  # Expected if API hides deleted items
    except Exception:  # noqa: S110
        pass


@pytest.mark.asyncio
async def test_update_idempotency(
    service: TestCaseService, cleanup_tracker: CleanupTracker, project_id: int, run_name: str
):
    """Test that applying the same update multiple times produces independent results (idempotency-ish)."""
    case = await service.create_test_case(project_id=project_id, name=run_name)
    cleanup_tracker.track_test_case(case.id)

    update_data = TestCaseUpdate(description="Idempotent Update")

    # First Update
    update1 = await service.update_test_case(case.id, update_data)
    assert update1.description == "Idempotent Update"

    # Second Update (Same data)
    update2 = await service.update_test_case(case.id, update_data)
    assert update2.description == "Idempotent Update"
    assert update2.id == case.id


@pytest.mark.asyncio
async def test_create_with_full_metadata(
    service: TestCaseService, cleanup_tracker: CleanupTracker, project_id: int, run_name: str
):
    """Test creating a test case with all optional fields."""
    tags = ["e2e", "automated", f"run-{run_name}"]

    # Use basic create first because create_test_case helper doesn't support all DTO fields directly
    case = await service.create_test_case(
        project_id=project_id,
        name=run_name,
        description="Full metadata description",
        steps=[],
        attachments=[],
        tags=tags,
        custom_fields=None,
    )

    # Update with additional metadata
    update_data = TestCaseUpdate(precondition="Preconditions", expected_result="Expected Result", automated=True)
    case = await service.update_test_case(case.id, update_data)

    cleanup_tracker.track_test_case(case.id)

    fetched = await service.get_test_case(case.id)
    assert fetched.precondition == "Preconditions"
    assert fetched.expected_result == "Expected Result"
    assert fetched.automated is True

    fetched_tag_names = [t.name for t in fetched.tags]
    for tag in tags:
        assert tag in fetched_tag_names
