import pytest

from src.client import AllureClient
from src.services.test_case_service import TestCaseService
from src.tools.create_test_case import create_test_case
from src.tools.update_test_case import update_test_case
from tests.e2e.helpers.cleanup import CleanupTracker


async def _get_first_issue_key(client: AllureClient) -> str | None:
    """Helper to find a valid issue key pattern or return None if no integration."""
    integrations = await client.api_client.get_all_integrations()
    if not integrations:
        return None
    # If using Jira or similar, we might need a valid key.
    # For now, we can try a dummy key if the system doesn't validate strictly,
    # or skip if we can't determine a valid one.
    # But usually, providing 'TEST-123' might work if validation is loose
    # or fail if strict.
    # Let's try to search for existing issues? No API for that easily.
    # We'll use a dummy key and expect either success or specific error.
    return "TEST-123"


@pytest.mark.asyncio
async def test_e2e_issue_lifecycle(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
) -> None:
    """
    E2E Issue Linking Lifecycle:
    1. Create TC with issue.
    2. Verify issue linked.
    3. Remove issue via update.
    4. Verify issue removed.
    5. Add issue via update.
    6. Verify issue added.
    """
    # Check if we have integrations
    integrations = await allure_client.get_integrations()
    if not integrations:
        pytest.skip("No integrations configured in the environment. Skipping issue link E2E.")

    # We assume 'TEST-123' is a valid format or acceptable dummy.
    # If the system validates against real Jira, this might fail.
    # But for E2E in a sandbox, we hope for loose validation or mock.
    # If strictly valid key needed, we'd need env var.
    issue_key = "TEST-123"

    # 1. Create with issue
    name = "E2E Issue Link Validation"
    result = await create_test_case(name=name, issues=[issue_key], project_id=project_id)

    assert "Created Test Case ID:" in result
    import re

    match = re.search(r"ID: (\d+)", result)
    assert match
    test_case_id = int(match.group(1))
    cleanup_tracker.track_test_case(test_case_id)

    # 2. Verify issue linked
    service = TestCaseService(client=allure_client)
    tc = await service.get_test_case(test_case_id)
    assert tc.issues, "Issues should be present"
    assert any(i.name == issue_key for i in tc.issues), f"Issue {issue_key} not found in {tc.issues}"

    # 3. Remove issue via update
    await update_test_case(test_case_id=test_case_id, remove_issues=[issue_key])

    # 4. Verify removal
    tc = await service.get_test_case(test_case_id)
    current_issues = [i.name for i in (tc.issues or [])]
    assert issue_key not in current_issues, "Issue should be removed"

    # 5. Add issue via update
    await update_test_case(test_case_id=test_case_id, issues=[issue_key])

    # 6. Verify addition
    tc = await service.get_test_case(test_case_id)
    assert any(i.name == issue_key for i in (tc.issues or [])), "Issue should be re-added"

    # 7. Clear issues
    await update_test_case(test_case_id=test_case_id, clear_issues=True)
    tc = await service.get_test_case(test_case_id)
    assert not tc.issues, "Issues should be cleared"
