import pytest
import respx

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
        # 1. Attachment Upload Mock
        upload_route = mock.post("/api/rs/attachment").respond(
            status_code=201,
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

        # 2. Test Case Creation Mock
        create_route = mock.post("/api/rs/testcase").respond(
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

        # Call Tool
        result_msg = await create_test_case(
            project_id=project_id, name=name, description=description, steps=steps, tags=tags, attachments=attachments
        )

        # Verifications
        assert "Created Test Case ID: 200" in result_msg
        assert name in result_msg

        # Verify Upload Request
        assert upload_route.called
        # Check payload/files? respx/httpx handling of multipart is complex to inspect via 'files'.
        # But we verify it was called.

        # Verify Creation Request
        assert create_route.called
        request = create_route.calls.last.request

        # Parse JSON from content
        import json

        payload = json.loads(request.content)

        assert payload["name"] == name
        assert payload["description"] == description
        assert payload["tags"][0]["name"] in tags

        # Verify Steps structure
        s = payload["scenario"]["steps"]
        # Expected: BodyStep(Login) -> ExpectedBodyStep(Dashboard) -> AttachmentStep(500)
        # Sequence depends on dictionary iteration? Or implementation?
        # Implementation: loops input steps (Action, Expected), THEN loops attachments.
        assert len(s) == 3
        # Check types via discriminatory field if it exists, or content
        # Note: We provided 'type' in implementation ("BodyStep", etc.)
        # Pydantic likely serialized it if we used 'model_dump'.
        print(s)

        assert s[0]["body"] == "Login"
        assert s[0]["type"] == "BodyStep"

        assert s[1]["body"] == "Dashboard"
        assert s[1]["type"] == "ExpectedBodyStep"

        assert s[2]["attachmentId"] == 500
        assert s[2]["type"] == "AttachmentStep"
