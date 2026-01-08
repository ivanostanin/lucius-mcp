import json
import pytest
import respx
from httpx import Response

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
