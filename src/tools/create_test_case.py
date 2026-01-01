"""Tool for creating Test Cases in Allure TestOps."""

from src.client import AllureClient
from src.client.models.test_cases import (
    BodyStepDto,
    ExpectedBodyStepDto,
    TestCaseCreateV2Dto,
    TestCaseScenarioV2Dto,
    TestTagDto,
)
from src.services.test_case_service import TestCaseService
from src.utils.config import settings


async def create_test_case(
    project_id: int,
    name: str,
    description: str | None = None,
    steps: list[dict[str, str]] | None = None,
    tags: list[str] | None = None,
    attachments: list[dict[str, str]] | None = None,
) -> str:
    """Create a new test case in Allure TestOps.

    Args:
        project_id: The ID of the project.
        name: The name of the test case.
        description: A markdown description of the test case.
        steps: List of steps. Each step must be a dict with 'action' and 'expected' keys.
               Example: [{'action': 'Login', 'expected': 'Dashboard visible'}]
        tags: List of tag names.
        attachments: List of attachments.
                     Example Base64: [{'name': 's.png', 'content': '<base64>', 'content_type': 'image/png'}]
                     Example URL: [{'name': 'report.pdf', 'url': 'http://example.com/report.pdf',
                                    'content_type': 'application/pdf'}]

    Returns:
        A message confirming creation with the ID and Name.
    """

    # Construct Steps DTOs
    step_dtos: list[BodyStepDto | ExpectedBodyStepDto] = []
    if steps:
        for s in steps:
            # Simple step mapping. For more complex structures, more logic needed.
            action = s.get("action", "")
            expected = s.get("expected", "")
            if action:
                step_dtos.append(
                    BodyStepDto(
                        body=action,
                        type="BodyStep",
                    )
                )
            if expected:
                step_dtos.append(
                    ExpectedBodyStepDto(
                        body=expected,
                        type="ExpectedBodyStep",
                    )
                )

    # Construct Tags DTOs
    tag_dtos = []
    if tags:
        for t in tags:
            tag_dtos.append(TestTagDto(name=t))

    # Construct Main DTO
    scenario = TestCaseScenarioV2Dto(steps=step_dtos)

    data = TestCaseCreateV2Dto(
        name=name,
        description=description,
        scenario=scenario,
        tags=tag_dtos,
        projectId=project_id,
        automation="manual",  # Assuming manual creation via tool implies manual kind
    )

    # Allure API Token must be set
    token = settings.ALLURE_API_TOKEN
    if token is None:
        return "Error: ALLURE_API_TOKEN is not configured."

    async with AllureClient(base_url=settings.ALLURE_ENDPOINT, token=token) as client:
        service = TestCaseService(client)
        result = await service.create_test_case(project_id, data, attachments=attachments)

        return f"Created Test Case ID: {result.id} Name: {result.name}"
