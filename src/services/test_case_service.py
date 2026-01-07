from typing import Any

from src.client import AllureClient
from src.client.exceptions import AllureValidationError
from src.client.generated.models import (
    CustomFieldDto,
    CustomFieldValueWithCfDto,
    ScenarioStepCreateDto,
    TestCaseCreateV2Dto,
    TestCaseOverviewDto,
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

        # Create test case WITHOUT steps in scenario (steps will be added separately)
        data = TestCaseCreateV2Dto(
            name=name,
            description=description,
            scenario=None,  # No scenario initially
            tags=tag_dtos,
            custom_fields=cf_dtos,
            project_id=project_id,
            automated=False,
        )

        created_test_case = await self._client.create_test_case(project_id, data)
        test_case_id = created_test_case.id

        if test_case_id is None:
            raise AllureValidationError("Failed to get test case ID from created test case")

        # 2. Add steps one by one via separate API calls
        last_step_id: int | None = None
        last_step_id = await self._add_steps(project_id, test_case_id, steps, last_step_id)

        # 3. Add global attachments (appended at end of steps)
        await self._add_global_attachments(project_id, test_case_id, attachments, last_step_id)

        return created_test_case

    async def _add_steps(
        self,
        project_id: int,
        test_case_id: int,
        steps: list[dict[str, Any]] | None,
        last_step_id: int | None,
    ) -> int | None:
        """Add steps to a test case using separate API calls.

        Args:
            project_id: Project ID for attachment uploads.
            test_case_id: Test case ID to add steps to.
            steps: List of step definitions.
            last_step_id: ID of the last created step (for ordering).

        Returns:
            The ID of the last created step, or None if no steps were created.
        """
        if not steps:
            return last_step_id

        for s in steps:
            action = str(s.get("action", ""))
            expected = str(s.get("expected", ""))
            step_attachments: list[dict[str, str]] = s.get("attachments", [])

            # Action Step (body step)
            if action:
                step_dto = ScenarioStepCreateDto(
                    test_case_id=test_case_id,
                    body=action,
                )
                response = await self._client.create_scenario_step(
                    test_case_id=test_case_id,
                    step=step_dto,
                    after_id=last_step_id,
                )
                last_step_id = response.created_step_id

                # If there's an expected result, create it as a child step under the action
                if expected:
                    expected_step_dto = ScenarioStepCreateDto(
                        test_case_id=test_case_id,
                        body=expected,
                        parent_id=last_step_id,  # Set parent to make it a child (expected result)
                    )
                    await self._client.create_scenario_step(
                        test_case_id=test_case_id,
                        step=expected_step_dto,
                        after_id=None,  # Will be added under parent
                    )
                    # Don't update last_step_id since expected results are children

            # Step Attachments (added after the action step)
            if step_attachments and isinstance(step_attachments, list):
                for sa in step_attachments:
                    if isinstance(sa, dict):
                        attachment_row = await self._attachment_service.upload_attachment(project_id, sa)
                        attachment_step_dto = ScenarioStepCreateDto(
                            test_case_id=test_case_id,
                            attachment_id=attachment_row.id,
                        )
                        attachment_response = await self._client.create_scenario_step(
                            test_case_id=test_case_id,
                            step=attachment_step_dto,
                            after_id=last_step_id,
                        )
                        last_step_id = attachment_response.created_step_id

        return last_step_id

    async def _add_global_attachments(
        self,
        project_id: int,
        test_case_id: int,
        attachments: list[dict[str, str]] | None,
        last_step_id: int | None,
    ) -> None:
        """Add global attachments to a test case as attachment steps.

        Args:
            project_id: Project ID for attachment uploads.
            test_case_id: Test case ID to add attachments to.
            attachments: List of attachment definitions.
            last_step_id: ID of the last created step (for ordering).
        """
        if not attachments:
            return

        for attachment in attachments:
            attachment_row = await self._attachment_service.upload_attachment(project_id, attachment)
            attachment_step_dto = ScenarioStepCreateDto(
                test_case_id=test_case_id,
                attachment_id=attachment_row.id,
            )
            response = await self._client.create_scenario_step(
                test_case_id=test_case_id,
                step=attachment_step_dto,
                after_id=last_step_id,
            )
            last_step_id = response.created_step_id
