from typing import Any

import pytest

from src.client import AllureClient
from src.services.test_case_service import TestCaseService
from src.tools.create_test_case import create_test_case
from src.utils.auth import get_auth_context
from tests.e2e.helpers.cleanup import CleanupTracker


@pytest.mark.asyncio
async def test_full_house_creation(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: Any,
    pixel_b64: str,
    api_token: str,
) -> None:
    """
    E2E-1: The "Full House" Test Case.
    Verifies creation with name, desc, steps, tags, attachments using real API.
    """
    # Test Data
    name = "E2E Full House Real"
    description = "# Markdown Desc"

    steps = [{"action": "Login", "expected": "Dashboard"}]
    tags = ["e2e", "integration"]
    attachments = [
        {
            "name": "evidence.png",
            "content": pixel_b64,
            "content_type": "image/png",
        }
    ]

    # Call Tool
    result_msg = await create_test_case(
        project_id=project_id,
        name=name,
        description=description,
        steps=steps,
        tags=tags,
        attachments=attachments,
        api_token=api_token,
    )

    # Verifications
    assert "Created Test Case ID:" in result_msg
    assert name in result_msg

    # Extract ID from message "Created Test Case ID: <id> Name: <name>"
    import re

    match = re.search(r"ID: (\d+)", result_msg)
    assert match, "Could not extract ID from result message"
    test_case_id = int(match.group(1))

    # Track for cleanup
    cleanup_tracker.track_test_case(test_case_id)

    # Verify in Allure
    service = TestCaseService(
        get_auth_context(api_token=api_token),
        client=allure_client,
    )
    fetched_case = await service.get_test_case(test_case_id)

    assert fetched_case.name == name
    assert fetched_case.description == description

    # Verify Tags
    fetched_tags = [t.name for t in (fetched_case.tags or [])]
    for tag in tags:
        assert tag in fetched_tags

    # Verify Scenario (Steps)
    scenario = await allure_client.get_test_case_scenario(test_case_id)
    assert scenario.steps is not None
    assert len(scenario.steps) >= len(steps)

    # Check for step content
    step_found = False
    for step in scenario.steps:
        if step.actual_instance and hasattr(step.actual_instance, "body"):
            if step.actual_instance.body == "Login":
                step_found = True
                break
    assert step_found, "Step 'Login' not found in scenario"

    # Verify Global Attachment
    # Attachments are added as steps in the scenario in our implementation
    attachment_found = False
    for step in scenario.steps:
        if step.actual_instance and hasattr(step.actual_instance, "attachment_id"):
            if step.actual_instance.name == "evidence.png":
                attachment_found = True
                break
    assert attachment_found, "Global attachment 'evidence.png' not found in scenario"


@pytest.mark.asyncio
async def test_url_attachment_flow(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: Any,
    api_token: str,
) -> None:
    """
    E2E-2: Test Case with URL Attachment.
    Verifies that the tool downloads content from URL and uploads it to Allure.
    """
    name = "URL Attachment Test Real"
    # Use a stable, high-availability public test URL (small text file)
    url = "https://www.google.com/robots.txt"
    filename = "robots.txt"

    attachments = [
        {
            "name": filename,
            "url": url,
            "content_type": "text/plain",
        }
    ]

    # Call Tool
    result_msg = await create_test_case(
        project_id=project_id,
        name=name,
        attachments=attachments,
        api_token=api_token,
    )

    # Verifications
    assert "Created Test Case ID:" in result_msg

    # Extract ID
    import re

    match = re.search(r"ID: (\d+)", result_msg)
    assert match
    test_case_id = int(match.group(1))

    # Track for cleanup
    cleanup_tracker.track_test_case(test_case_id)

    # Verify Attachment in Allure
    scenario = await allure_client.get_test_case_scenario(test_case_id)

    attachment_found = False
    for step in scenario.steps:
        if step.actual_instance and hasattr(step.actual_instance, "attachment_id"):
            if step.actual_instance.name == filename:
                attachment_found = True
                break
    assert attachment_found, f"Attachment '{filename}' not found in scenario"


@pytest.mark.asyncio
async def test_e2e_3_custom_fields_creation(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    api_token: str,
) -> None:
    """
    E2E-3: Custom Fields Creation.
    Create a test case with custom fields using real TestOps instance.
    """
    service = TestCaseService(
        get_auth_context(api_token=api_token),
        client=allure_client,
    )

    # Create test case with custom fields
    # Note: Custom fields must exist in the project
    case_name = "E2E-3 Custom Fields Test"
    custom_fields = {"Feature": "Flow", "Component": "Authentication"}

    created_case = await service.create_test_case(
        project_id=project_id, name=case_name, description="Testing custom fields", custom_fields=custom_fields
    )

    test_case_id = created_case.id
    assert test_case_id is not None
    cleanup_tracker.track_test_case(test_case_id)
    assert created_case.name == case_name

    # Verify custom fields were set
    fetched_case = await service.get_test_case(test_case_id)
    assert fetched_case.custom_fields is not None

    # Custom fields should be present
    cf_values = {cf.custom_field.name: cf.name for cf in fetched_case.custom_fields if cf.custom_field}
    assert "Priority" in cf_values or "Component" in cf_values  # At least one should be set


@pytest.mark.asyncio
async def test_e2e_4_minimal_creation(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    api_token: str,
) -> None:
    """
    E2E-4: Minimal Creation.
    Create test case with only required fields (project_id, name).
    """
    service = TestCaseService(
        get_auth_context(api_token=api_token),
        client=allure_client,
    )

    case_name = "E2E-4 Minimal Test Case"

    created_case = await service.create_test_case(project_id=project_id, name=case_name)

    test_case_id = created_case.id
    assert test_case_id is not None
    cleanup_tracker.track_test_case(test_case_id)
    assert created_case.name == case_name

    # Verify it was created with defaults
    fetched_case = await service.get_test_case(test_case_id)
    assert fetched_case.id == test_case_id
    assert fetched_case.name == case_name
    assert fetched_case.description is None or fetched_case.description == ""


@pytest.mark.asyncio
async def test_e2e_5_step_level_attachments(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    pixel_b64: str,
    api_token: str,
) -> None:
    """
    E2E-5: Step-level Attachments.
    Create test case with attachments nested in steps.
    """
    service = TestCaseService(
        get_auth_context(api_token=api_token),
        client=allure_client,
    )

    case_name = "E2E-5 Step Attachments Test"
    # Small 1x1 transparent PNG

    steps = [
        {
            "action": "Navigate to login page",
            "expected": "Login form displayed",
            "attachments": [{"name": "login-screen.png", "content": pixel_b64, "content_type": "image/png"}],
        }
    ]

    created_case = await service.create_test_case(project_id=project_id, name=case_name, steps=steps)

    test_case_id = created_case.id
    assert test_case_id is not None
    cleanup_tracker.track_test_case(test_case_id)

    # Verify scenario has the step with attachment
    scenario = await allure_client.get_test_case_scenario(test_case_id)
    assert scenario.steps is not None
    assert len(scenario.steps) > 0

    # Look for the attachment in the step's children
    found_attachment = False
    for step in scenario.steps:
        if step.actual_instance and hasattr(step.actual_instance, "steps"):
            child_steps = step.actual_instance.steps
            if child_steps:
                for child in child_steps:
                    if child.actual_instance and hasattr(child.actual_instance, "attachment_id"):
                        found_attachment = True
                        break

    assert found_attachment, "Step-level attachment not found in scenario"


@pytest.mark.asyncio
async def test_e2e_6_complex_step_hierarchy(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    pixel_b64: str,
    api_token: str,
) -> None:
    """
    E2E-6: Complex Step Hierarchy.
    Create test case with multiple steps, expected results, and attachments.
    """
    service = TestCaseService(
        get_auth_context(api_token=api_token),
        client=allure_client,
    )

    case_name = "E2E-6 Complex Hierarchy Test"

    steps = [
        {"action": "Step 1: Login", "expected": "Dashboard visible"},
        {
            "action": "Step 2: Navigate to settings",
            "expected": "Settings page loaded",
            "attachments": [{"name": "settings.png", "content": pixel_b64, "content_type": "image/png"}],
        },
        {"action": "Step 3: Update profile", "expected": "Profile updated successfully"},
    ]

    created_case = await service.create_test_case(project_id=project_id, name=case_name, steps=steps)

    test_case_id = created_case.id
    assert test_case_id is not None
    cleanup_tracker.track_test_case(test_case_id)

    # Verify scenario has all steps
    scenario = await allure_client.get_test_case_scenario(test_case_id)
    assert scenario.steps is not None
    assert len(scenario.steps) >= 3, f"Expected at least 3 steps, got {len(scenario.steps)}"


@pytest.mark.asyncio
async def test_e2e_7_edge_cases(
    project_id: int,
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    api_token: str,
) -> None:
    """
    E2E-7: Edge Cases.
    Test with empty description, no steps, no tags.
    """
    service = TestCaseService(
        get_auth_context(api_token=api_token),
        client=allure_client,
    )

    case_name = "E2E-7 Edge Cases Test"

    # Create with empty optional fields
    created_case = await service.create_test_case(
        project_id=project_id, name=case_name, description="", steps=None, tags=None, attachments=None
    )

    test_case_id = created_case.id
    assert test_case_id is not None
    cleanup_tracker.track_test_case(test_case_id)
    assert created_case.name == case_name

    # Verify it was created
    fetched_case = await service.get_test_case(test_case_id)
    assert fetched_case.id == test_case_id
