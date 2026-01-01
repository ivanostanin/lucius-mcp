"""Service for Test Case business logic."""

from src.client import AllureClient
from src.client.models.attachments import AttachmentStepDto
from src.client.models.test_cases import (
    TestCaseCreateV2Dto,
    TestCaseOverviewDto,
    TestCaseScenarioV2Dto,
)
from src.services.attachment_service import AttachmentService


class TestCaseService:
    """Service for managing Test Cases in Allure TestOps."""

    def __init__(self, client: AllureClient, attachment_service: AttachmentService | None = None) -> None:
        self._client = client
        self._attachment_service = attachment_service or AttachmentService(client)

    async def create_test_case(
        self,
        project_id: int,
        data: TestCaseCreateV2Dto,
        attachments: list[dict[str, str]] | None = None,
    ) -> TestCaseOverviewDto:
        """Create a new test case.

        Args:
            project_id: The ID of the project where the test case will be created.
            data: The test case creation data.
            attachments: Optional list of attachments to add.
                         Format: [{'name': '...', 'content': '...', 'content_type': '...'}]

        Returns:
            The created test case overview.

        Raises:
            AllureAPIError: If the API request fails.
            AllureValidationError: If validation fails.
        """
        if attachments:
            if not data.scenario:
                data.scenario = TestCaseScenarioV2Dto(steps=[])
            if data.scenario.steps is None:
                data.scenario.steps = []

            for attachment in attachments:
                attachment_row = await self._attachment_service.upload_attachment(project_id, attachment)

                # Create attachment step
                step = AttachmentStepDto(attachmentId=attachment_row.id, type="AttachmentStep")
                data.scenario.steps.append(step)

        return await self._client.create_test_case(project_id, data)
