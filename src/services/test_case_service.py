from typing import Any

from src.client import AllureClient
from src.client.exceptions import AllureValidationError
from src.client.generated.models import (
    AttachmentStepDto,
    BodyStepDto,
    CustomFieldDto,
    CustomFieldValueWithCfDto,
    ExpectedBodyStepDto,
    SharedStepScenarioDtoStepsInner,
    TestCaseCreateV2Dto,
    TestCaseOverviewDto,
    TestCaseScenarioV2Dto,
    TestTagDto,
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
        name: str,
        description: str | None = None,
        steps: list[dict[str, Any]] | None = None,
        tags: list[str] | None = None,
        attachments: list[dict[str, str]] | None = None,
        custom_fields: dict[str, str] | None = None,
    ) -> TestCaseOverviewDto:
        """Create a new test case.

        Args:
            project_id: The ID of the project where the test case will be created.
            name: The name of the test case.
            description: Optional description.
            steps: Optional list of steps [{'action': '...', 'expected': '...', 'attachments': [...]}]
            tags: Optional list of tags.
            attachments: Optional list of test-case level attachments.
            custom_fields: Optional dictionary of custom fields (Name -> Value).

        Returns:
            The created test case overview.

        Raises:
            AllureAPIError: If the API request fails.
            AllureValidationError: If validation fails.
        """
        # 1. Validation
        if not project_id:
            raise AllureValidationError("Project ID is required")
        if not name or not name.strip():
            raise AllureValidationError("Test Case name is required")
        if len(name) > 255:
            raise AllureValidationError("Test Case name must be 255 characters or less")

        # 2. Build Steps
        step_dtos = await self._build_steps(project_id, steps)

        # Global Attachments (Appended to end of steps)
        if attachments:
            for attachment in attachments:
                attachment_row = await self._attachment_service.upload_attachment(project_id, attachment)
                step_dtos.append(
                    SharedStepScenarioDtoStepsInner(
                        actual_instance=AttachmentStepDto(attachmentId=attachment_row.id, type="AttachmentStep")
                    )
                )

        # Tags DTOs
        tag_dtos = []
        if tags:
            for t in tags:
                tag_dtos.append(TestTagDto(name=t))

        # Custom Fields DTOs
        cf_dtos = []
        if custom_fields:
            for key, value in custom_fields.items():
                cf_dtos.append(CustomFieldValueWithCfDto(custom_field=CustomFieldDto(name=key), name=value))

        # Construct Main DTO
        scenario = TestCaseScenarioV2Dto(steps=step_dtos)

        data = TestCaseCreateV2Dto(
            name=name,
            description=description,
            scenario=scenario,
            tags=tag_dtos,
            custom_fields=cf_dtos,
            project_id=project_id,
            automated=False,
        )

        return await self._client.create_test_case(project_id, data)

    async def _build_steps(
        self, project_id: int, steps: list[dict[str, Any]] | None
    ) -> list[SharedStepScenarioDtoStepsInner]:
        """Build step DTOs from input list."""
        step_dtos: list[SharedStepScenarioDtoStepsInner] = []
        if not steps:
            return step_dtos

        for s in steps:
            action = str(s.get("action", ""))
            expected = str(s.get("expected", ""))
            step_attachments: list[dict[str, str]] = s.get("attachments", [])  # List[dict]

            # Action Step
            if action:
                step_dtos.append(
                    SharedStepScenarioDtoStepsInner(
                        actual_instance=BodyStepDto(
                            body=action,
                            type="BodyStep",
                        )
                    )
                )

            # Step Attachments (Interleaved)
            if step_attachments and isinstance(step_attachments, list):
                for sa in step_attachments:
                    if isinstance(sa, dict):
                        sa_row = await self._attachment_service.upload_attachment(project_id, sa)
                        step_dtos.append(
                            SharedStepScenarioDtoStepsInner(
                                actual_instance=AttachmentStepDto(attachmentId=sa_row.id, type="AttachmentStep")
                            )
                        )

            # Expected Result Step
            if expected:
                step_dtos.append(
                    SharedStepScenarioDtoStepsInner(
                        actual_instance=ExpectedBodyStepDto(
                            body=expected,
                            type="ExpectedBodyStep",
                        )
                    )
                )
        return step_dtos
