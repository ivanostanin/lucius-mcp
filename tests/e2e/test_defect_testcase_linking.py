"""E2E tests for defect-to-test-case linking."""

import re

import pytest

from src.client import AllureClient
from src.client.generated.exceptions import BadRequestException
from src.tools.create_test_case import create_test_case
from src.tools.defects import (
    create_defect,
    link_defect_to_test_case,
    list_defect_test_cases,
)
from tests.e2e.helpers.cleanup import CleanupTracker

pytestmark = pytest.mark.asyncio(loop_scope="module")


def _extract_id(text: str, pattern: str) -> int:
    match = re.search(pattern, text)
    if not match:
        raise AssertionError(f"Could not extract ID from output: {text}")
    return int(match.group(1))


async def test_defect_testcase_linking_lifecycle(
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    project_id: int,
    test_run_id: str,
) -> None:
    """Create defect and test case, link them, verify listing, and confirm idempotency."""
    integrations = await allure_client.get_integrations()
    if not integrations:
        pytest.skip("No integrations configured in the environment. Skipping defect-test-case linking E2E.")

    compatible_integration_ids = [integration.id for integration in integrations if integration.id is not None]
    if not compatible_integration_ids:
        pytest.skip("No integrations with IDs available in environment. Skipping defect-test-case linking E2E.")

    create_defect_output = await create_defect(
        name=f"[{test_run_id}] Defect Link E2E",
        description="Defect used for defect-test-case linking E2E validation",
    )
    defect_id = _extract_id(create_defect_output, r"Defect #(\d+)")
    cleanup_tracker.track_defect(defect_id)

    create_case_output = await create_test_case(
        name=f"[{test_run_id}] Test Case Link E2E",
        project_id=project_id,
    )
    test_case_id = _extract_id(create_case_output, r"Created Test Case ID: (\d+)")
    cleanup_tracker.track_test_case(test_case_id)

    issue_key = "PROJ-7401"
    link_output: str | None = None
    selected_integration_id: int | None = None
    for integration_id in compatible_integration_ids:
        try:
            link_output = await link_defect_to_test_case(
                defect_id=defect_id,
                test_case_id=test_case_id,
                issue_key=issue_key,
                integration_id=integration_id,
            )
            selected_integration_id = integration_id
            break
        except BadRequestException as exc:
            if "not configured for project" in str(exc).lower():
                continue
            raise

    if link_output is None or selected_integration_id is None:
        pytest.skip("No project-compatible integration found for defect-to-test-case linking.")

    assert f"Defect #{defect_id}" in link_output
    assert f"Test Case #{test_case_id}" in link_output
    assert issue_key in link_output

    linked_cases_output = await list_defect_test_cases(defect_id=defect_id)
    assert f"#{test_case_id}" in linked_cases_output

    idempotent_output = await link_defect_to_test_case(
        defect_id=defect_id,
        test_case_id=test_case_id,
        issue_key=issue_key,
        integration_id=selected_integration_id,
    )
    assert "already linked" in idempotent_output.lower()

    reuse_output = await link_defect_to_test_case(
        defect_id=defect_id,
        test_case_id=test_case_id,
    )
    assert "Defect" in reuse_output
    assert "Test Case" in reuse_output
