import json
import os

import pytest
import respx
from httpx import Response

from src.client import AllureClient
from src.services.test_case_service import TestCaseService
from src.tools.create_test_case import create_test_case
from src.utils.config import settings


@pytest.mark.asyncio
async def test_full_house_creation() -> None:
    """
    E2E-1: The "Full House" Test Case.
    Verifies creation with name, desc, steps, tags, attachments.
    """
    project_id = 101

    # Mock data
    name = "E2E Full House"
    description = "# Markdown Desc"
    steps = [{"action": "Login", "expected": "Dashboard"}]
    tags = ["e2e", "integration"]
    attachments = [
        {
            "name": "evidence.png",
            "content": "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7",
            "content_type": "image/png",
        }
    ]

    # Expected API calls
    async with respx.mock(base_url=settings.ALLURE_ENDPOINT) as mock:
        # 0. Auth Mock
        mock.post("/api/uaa/oauth/token").respond(
            status_code=200,
            json={"access_token": "mock-token", "expires_in": 3600},
        )

        # 1. Test Case Creation Mock
        create_route = mock.post("/api/testcase").respond(
            status_code=200,
            json={
                "id": 200,
                "name": name,
                "description": description,
                "automated": False,
                "statusId": 1,
                "workflowId": 1,
                "projectId": project_id,
            },
        )

        # 2. Step Creation Mock (Dynamic responses for multiple calls)
        # We need to return different IDs for Action (301), Expected (302), and Attachment (303)
        step_ids = [301, 302, 303]

        def step_side_effect(request):
            step_id = step_ids.pop(0)
            return Response(200, json={"createdStepId": step_id})

        step_route = mock.post("/api/testcase/step").mock(side_effect=step_side_effect)

        # 3. Global Attachment Upload Mock
        upload_route = mock.post("/api/testcase/attachment", params={"testCaseId": "200"}).respond(
            status_code=200,
            json=[
                {
                    "id": 500,
                    "name": "evidence.png",
                    "entity": "ATTACHMENT",
                    "contentLength": 100,
                    "contentType": "image/png",
                }
            ],
        )

        # Call Tool
        result_msg = await create_test_case(
            project_id=project_id, name=name, description=description, steps=steps, tags=tags, attachments=attachments
        )

        # Verifications
        assert "Created Test Case ID: 200" in result_msg
        assert name in result_msg

        assert create_route.called
        assert upload_route.called
        assert step_route.call_count == 3

        # Verify initial creation payload doesn't have scenario
        create_request = create_route.calls.last.request
        create_payload = json.loads(create_request.content)
        assert "scenario" not in create_payload
        assert create_payload["name"] == name
        assert create_payload["description"] == description

        # Verify Action Step payload (First step call)
        action_call = step_route.calls[0]
        action_payload = json.loads(action_call.request.content)
        assert action_payload["body"] == "Login"
        assert action_payload["testCaseId"] == 200
        assert action_payload.get("parentId") is None
        # Check that it was called WITHOUT afterId (it's the first step)
        assert "afterId" not in action_call.request.url.params

        # Verify Expected Step payload (Second step call, child of action)
        expected_call = step_route.calls[1]
        expected_payload = json.loads(expected_call.request.content)
        assert expected_payload["body"] == "Dashboard"
        assert expected_payload.get("parentId") == 301
        assert (
            "afterId" not in expected_call.request.url.params
        )  # Children are added without afterId (to the beginning)

        # Verify Attachment Step payload (Third step call, after action)
        attachment_step_call = step_route.calls[2]
        attachment_payload = json.loads(attachment_step_call.request.content)
        assert attachment_payload["attachmentId"] == 500
        assert attachment_payload.get("parentId") is None
        assert attachment_step_call.request.url.params.get("afterId") == "301"


@pytest.mark.asyncio
async def test_url_attachment_flow() -> None:
    """
    E2E-2: Test Case with URL Attachment.
    Verifies that the tool downloads content from URL and uploads it to Allure.
    """
    project_id = 101
    name = "URL Attachment Test"
    url = "http://external.com/report.pdf"

    attachments = [
        {
            "name": "report.pdf",
            "url": url,
            "content_type": "application/pdf",
        }
    ]

    # Use a broader mock to capture both Allure API and external URL
    async with respx.mock() as mock:
        # 1. External Download Mock
        download_route = mock.get(url).respond(
            status_code=200,
            content=b"%PDF-1.4-mock-content",
        )

        mock.post(f"{settings.ALLURE_ENDPOINT}/api/uaa/oauth/token").respond(
            status_code=200,
            json={"access_token": "mock-token", "expires_in": 3600},
        )

        # 2. Test Case Creation Mock
        mock.post(f"{settings.ALLURE_ENDPOINT}/api/testcase").respond(
            status_code=200,
            json={
                "id": 201,
                "name": name,
                "description": None,
                "automated": False,
                "statusId": 1,
                "workflowId": 1,
                "projectId": project_id,
            },
        )

        # 3. Allure Upload Mock
        upload_route = mock.post(f"{settings.ALLURE_ENDPOINT}/api/testcase/attachment").respond(
            status_code=200,
            json=[
                {
                    "id": 600,
                    "name": "report.pdf",
                    "entity": "ATTACHMENT",
                    "contentLength": 100,
                    "contentType": "image/png",
                }
            ],
        )

        # 4. Attachment Step Mock
        mock.post(f"{settings.ALLURE_ENDPOINT}/api/testcase/step").respond(status_code=200, json={"createdStepId": 401})

        # Call Tool
        result_msg = await create_test_case(project_id=project_id, name=name, attachments=attachments)

        # Verifications
        assert "Created Test Case ID: 201" in result_msg

        # Verify Download
        assert download_route.called

        # Verify Upload
        assert upload_route.called


# ==========================================
# Real E2E Tests (using actual TestOps instance)
# ==========================================


@pytest.mark.skipif(
    not os.getenv("ALLURE_ENDPOINT") or not os.getenv("ALLURE_API_TOKEN"), reason="Allure environment variables not set"
)
@pytest.mark.asyncio
async def test_e2e_3_custom_fields_creation(project_id: int, allure_client: AllureClient) -> None:
    """
    E2E-3: Custom Fields Creation.
    Create a test case with custom fields using real TestOps instance.
    """
    service = TestCaseService(allure_client)
    test_case_id = None

    try:
        # Create test case with custom fields
        # Note: Custom fields must exist in the project
        case_name = "E2E-3 Custom Fields Test"
        custom_fields = {"Feature": "Flow", "Component": "Authentication"}

        created_case = await service.create_test_case(
            project_id=project_id, name=case_name, description="Testing custom fields", custom_fields=custom_fields
        )

        test_case_id = created_case.id
        assert test_case_id is not None
        assert created_case.name == case_name

        # Verify custom fields were set
        fetched_case = await service.get_test_case(test_case_id)
        assert fetched_case.custom_fields is not None

        # Custom fields should be present
        cf_values = {cf.custom_field.name: cf.name for cf in fetched_case.custom_fields if cf.custom_field}
        assert "Priority" in cf_values or "Component" in cf_values  # At least one should be set

    finally:
        if test_case_id:
            await allure_client.delete_test_case(test_case_id)


@pytest.mark.skipif(
    not os.getenv("ALLURE_ENDPOINT") or not os.getenv("ALLURE_API_TOKEN"), reason="Allure environment variables not set"
)
@pytest.mark.asyncio
async def test_e2e_4_minimal_creation(project_id: int, allure_client: AllureClient) -> None:
    """
    E2E-4: Minimal Creation.
    Create test case with only required fields (project_id, name).
    """
    service = TestCaseService(allure_client)
    test_case_id = None

    try:
        case_name = "E2E-4 Minimal Test Case"

        created_case = await service.create_test_case(project_id=project_id, name=case_name)

        test_case_id = created_case.id
        assert test_case_id is not None
        assert created_case.name == case_name

        # Verify it was created with defaults
        fetched_case = await service.get_test_case(test_case_id)
        assert fetched_case.id == test_case_id
        assert fetched_case.name == case_name
        assert fetched_case.description is None or fetched_case.description == ""

    finally:
        if test_case_id:
            await allure_client.delete_test_case(test_case_id)


@pytest.mark.skipif(
    not os.getenv("ALLURE_ENDPOINT") or not os.getenv("ALLURE_API_TOKEN"), reason="Allure environment variables not set"
)
@pytest.mark.asyncio
async def test_e2e_5_step_level_attachments(project_id: int, allure_client: AllureClient) -> None:
    """
    E2E-5: Step-level Attachments.
    Create test case with attachments nested in steps.
    """
    service = TestCaseService(allure_client)
    test_case_id = None

    try:
        case_name = "E2E-5 Step Attachments Test"
        # Small 1x1 transparent PNG
        pixel_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAAAAAA6fptVAAAACklEQVR4nGNiAAAABgANjd8qAAAAAElFTkSuQmCC"

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

    finally:
        if test_case_id:
            await allure_client.delete_test_case(test_case_id)


@pytest.mark.skipif(
    not os.getenv("ALLURE_ENDPOINT") or not os.getenv("ALLURE_API_TOKEN"), reason="Allure environment variables not set"
)
@pytest.mark.asyncio
async def test_e2e_6_complex_step_hierarchy(project_id: int, allure_client: AllureClient) -> None:
    """
    E2E-6: Complex Step Hierarchy.
    Create test case with multiple steps, expected results, and attachments.
    """
    service = TestCaseService(allure_client)
    test_case_id = None

    try:
        case_name = "E2E-6 Complex Hierarchy Test"
        pixel_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAAAAAA6fptVAAAACklEQVR4nGNiAAAABgANjd8qAAAAAElFTkSuQmCC"

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

        # Verify scenario has all steps
        scenario = await allure_client.get_test_case_scenario(test_case_id)
        assert scenario.steps is not None
        assert len(scenario.steps) >= 3, f"Expected at least 3 steps, got {len(scenario.steps)}"

    finally:
        if test_case_id:
            await allure_client.delete_test_case(test_case_id)


@pytest.mark.skipif(
    not os.getenv("ALLURE_ENDPOINT") or not os.getenv("ALLURE_API_TOKEN"), reason="Allure environment variables not set"
)
@pytest.mark.asyncio
async def test_e2e_7_edge_cases(project_id: int, allure_client: AllureClient) -> None:
    """
    E2E-7: Edge Cases.
    Test with empty description, no steps, no tags.
    """
    service = TestCaseService(allure_client)
    test_case_id = None

    try:
        case_name = "E2E-7 Edge Cases Test"

        # Create with empty optional fields
        created_case = await service.create_test_case(
            project_id=project_id, name=case_name, description="", steps=None, tags=None, attachments=None
        )

        test_case_id = created_case.id
        assert test_case_id is not None
        assert created_case.name == case_name

        # Verify it was created
        fetched_case = await service.get_test_case(test_case_id)
        assert fetched_case.id == test_case_id

    finally:
        if test_case_id:
            await allure_client.delete_test_case(test_case_id)
