from typing import Any

from pydantic import ValidationError as PydanticValidationError

from src.client import AllureClient
from src.client.exceptions import AllureValidationError
from src.client.generated.models import (
    CustomFieldDto,
    CustomFieldValueWithCfDto,
    ScenarioStepCreateDto,
    TestCaseCreateV2Dto,
    TestCaseOverviewDto,
    TestCaseTreeSelectionDto,
    TestTagDto,
)
from src.services.attachment_service import AttachmentService

# Maximum lengths based on API constraints
MAX_NAME_LENGTH = 255
MAX_TAG_LENGTH = 255
MAX_BODY_LENGTH = 10000  # Step body limit


class TestCaseService:
    """Service for managing Test Cases in Allure TestOps."""

    def __init__(self, client: AllureClient, attachment_service: AttachmentService | None = None) -> None:
        self._client = client
        self._attachment_service = attachment_service or AttachmentService(client)
        self._cf_cache: dict[int, dict[str, int]] = {}  # {project_id: {name: id}}

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
        # 1. Input Validation
        self._validate_project_id(project_id)
        self._validate_name(name)
        self._validate_steps(steps)
        self._validate_tags(tags)
        self._validate_attachments(attachments)
        self._validate_custom_fields(custom_fields)

        # 2. Resolve custom fields if provided
        resolved_custom_fields = []
        if custom_fields:
            project_cfs = await self._get_resolved_custom_fields(project_id)
            for key, value in custom_fields.items():
                cf_id = project_cfs.get(key)
                if cf_id is None:
                    raise AllureValidationError(f"Custom field '{key}' not found in project {project_id}.")

                resolved_custom_fields.append(
                    CustomFieldValueWithCfDto(custom_field=CustomFieldDto(id=cf_id, name=key), name=value)
                )

        # 3. Create TestCaseCreateV2Dto with validation
        tag_dtos = self._build_tag_dtos(tags)
        try:
            data = TestCaseCreateV2Dto(
                project_id=project_id,
                name=name,
                description=description,
                tags=tag_dtos,
                custom_fields=resolved_custom_fields,
            )
        except PydanticValidationError as e:
            raise AllureValidationError(f"Invalid test case data: {e}") from e

        # 4. Create the test case
        created_test_case = await self._client.create_test_case(project_id, data)
        test_case_id = created_test_case.id

        if test_case_id is None:
            raise AllureValidationError("Failed to get test case ID from created test case")

        # 5. Add steps one by one via separate API calls
        last_step_id: int | None = None
        last_step_id = await self._add_steps(test_case_id, steps, last_step_id)

        # 6. Add global attachments (appended at end of steps)
        await self._add_global_attachments(test_case_id, attachments, last_step_id)

        return created_test_case

    # ==========================================
    # Validation Methods
    # ==========================================

    def _validate_project_id(self, project_id: int) -> None:
        """Validate project ID."""
        if not isinstance(project_id, int):
            raise AllureValidationError(f"Project ID must be an integer, got {type(project_id).__name__}")
        if project_id <= 0:
            raise AllureValidationError("Project ID is required and must be positive")

    def _validate_name(self, name: str) -> None:
        """Validate test case name."""
        if not isinstance(name, str):
            raise AllureValidationError(f"Test Case name must be a string, got {type(name).__name__}")
        if not name or not name.strip():
            raise AllureValidationError("Test case name is required.")
        if len(name) > MAX_NAME_LENGTH:
            raise AllureValidationError(f"Test case name must be {MAX_NAME_LENGTH} characters or less.")

    def _validate_steps(self, steps: list[dict[str, Any]] | None) -> None:  # noqa: C901
        """Validate steps list structure and content."""
        if steps is None:
            return

        if not isinstance(steps, list):
            raise AllureValidationError(f"Steps must be a list, got {type(steps).__name__}")

        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                raise AllureValidationError(f"Step at index {i} must be a dictionary, got {type(step).__name__}")

            action = step.get("action")
            expected = step.get("expected")
            step_attachments = step.get("attachments")

            if action is not None and not isinstance(action, str):
                raise AllureValidationError(f"Step {i}: 'action' must be a string, got {type(action).__name__}")
            if action and len(action) > MAX_BODY_LENGTH:
                raise AllureValidationError(f"Step {i}: 'action' must be {MAX_BODY_LENGTH} characters or less")

            if expected is not None and not isinstance(expected, str):
                raise AllureValidationError(f"Step {i}: 'expected' must be a string, got {type(expected).__name__}")
            if expected and len(expected) > MAX_BODY_LENGTH:
                raise AllureValidationError(f"Step {i}: 'expected' must be {MAX_BODY_LENGTH} characters or less")

            if step_attachments is not None:
                if not isinstance(step_attachments, list):
                    raise AllureValidationError(
                        f"Step {i}: 'attachments' must be a list, got {type(step_attachments).__name__}"
                    )
                for j, att in enumerate(step_attachments):
                    if not isinstance(att, dict):
                        raise AllureValidationError(
                            f"Step {i}, attachment {j}: must be a dictionary, got {type(att).__name__}"
                        )

    def _validate_tags(self, tags: list[str] | None) -> None:
        """Validate tags list."""
        if tags is None:
            return

        if not isinstance(tags, list):
            raise AllureValidationError(f"Tags must be a list, got {type(tags).__name__}")

        for i, tag in enumerate(tags):
            if not isinstance(tag, str):
                raise AllureValidationError(f"Tag at index {i} must be a string, got {type(tag).__name__}")
            if not tag.strip():
                raise AllureValidationError(f"Tag at index {i} cannot be empty")
            if len(tag) > MAX_TAG_LENGTH:
                raise AllureValidationError(f"Tag at index {i} must be {MAX_TAG_LENGTH} characters or less")

    def _validate_attachments(self, attachments: list[dict[str, str]] | None) -> None:
        """Validate attachments list structure."""
        if attachments is None:
            return

        if not isinstance(attachments, list):
            raise AllureValidationError(f"Attachments must be a list, got {type(attachments).__name__}")

        for i, att in enumerate(attachments):
            if not isinstance(att, dict):
                raise AllureValidationError(f"Attachment at index {i} must be a dictionary, got {type(att).__name__}")
            # Must have either 'content' (base64) or 'url'
            if "content" not in att and "url" not in att:
                raise AllureValidationError(f"Attachment at index {i} must have either 'content' or 'url' key")
            # Must have 'name' for base64 content
            if "content" in att and "name" not in att:
                raise AllureValidationError(f"Attachment at index {i} with 'content' must also have 'name'")

    def _validate_custom_fields(self, custom_fields: dict[str, str] | None) -> None:
        """Validate custom fields dictionary."""
        if custom_fields is None:
            return

        if not isinstance(custom_fields, dict):
            raise AllureValidationError(f"Custom fields must be a dictionary, got {type(custom_fields).__name__}")

        for key, value in custom_fields.items():
            if not isinstance(key, str):
                raise AllureValidationError(f"Custom field key must be a string, got {type(key).__name__}")
            if not isinstance(value, str):
                raise AllureValidationError(
                    f"Custom field value for '{key}' must be a string, got {type(value).__name__}"
                )
            if not key.strip():
                raise AllureValidationError("Custom field key cannot be empty")

    # ==========================================
    # DTO Building Methods
    # ==========================================

    def _build_tag_dtos(self, tags: list[str] | None) -> list[TestTagDto]:
        """Build validated TestTagDto list."""
        if not tags:
            return []

        tag_dtos = []
        for t in tags:
            try:
                tag_dtos.append(TestTagDto(name=t))
            except PydanticValidationError as e:
                raise AllureValidationError(f"Invalid tag '{t}': {e}") from e
        return tag_dtos

    async def _get_resolved_custom_fields(self, project_id: int) -> dict[str, int]:
        """Get or fetch custom field name-to-id mapping for a project."""
        if project_id in self._cf_cache:
            return self._cf_cache[project_id]

        try:
            from src.client.generated.api.test_case_custom_field_controller_api import TestCaseCustomFieldControllerApi

            api = TestCaseCustomFieldControllerApi(self._client.api_client)
            selection = TestCaseTreeSelectionDto(project_id=project_id)
            cfs = await api.get_custom_fields_with_values2(test_case_tree_selection_dto=selection)

            mapping = {}
            for cf_with_values in cfs:
                if cf_with_values.custom_field and cf_with_values.custom_field.custom_field:
                    inner_cf = cf_with_values.custom_field.custom_field
                    if inner_cf.name and inner_cf.id:
                        mapping[inner_cf.name] = inner_cf.id

            self._cf_cache[project_id] = mapping
            return mapping
        except Exception as e:
            # If we fail to fetch CFs, we might want to warn or raise.
            # For now, let's raise as it's critical for resolving names to IDs.
            raise AllureValidationError(f"Failed to fetch custom fields for project {project_id}: {e}") from e

    def _build_custom_field_dtos(self, custom_fields: dict[str, str] | None) -> list[CustomFieldValueWithCfDto]:
        """DEPRECATED: Use inline resolution in create_test_case."""
        if not custom_fields:
            return []

        cf_dtos = []
        for key, value in custom_fields.items():
            if not key:
                raise AllureValidationError("Custom field key cannot be empty.")
            if not isinstance(value, str):
                raise AllureValidationError(f"Custom field '{key}' value must be a string.")
            cf_dtos.append(CustomFieldValueWithCfDto(custom_field=CustomFieldDto(name=key), name=value))
        return cf_dtos

    def _build_scenario_step_dto(
        self,
        test_case_id: int,
        body: str | None = None,
        attachment_id: int | None = None,
        parent_id: int | None = None,
    ) -> ScenarioStepCreateDto:
        """Build and validate a ScenarioStepCreateDto."""
        try:
            return ScenarioStepCreateDto(
                test_case_id=test_case_id,
                body=body,
                attachment_id=attachment_id,
                parent_id=parent_id,
            )
        except PydanticValidationError as e:
            raise AllureValidationError(f"Invalid scenario step data: {e}") from e

    # ==========================================
    # Step Creation Methods
    # ==========================================

    async def _add_steps(
        self,
        test_case_id: int,
        steps: list[dict[str, Any]] | None,
        last_step_id: int | None,
    ) -> int | None:
        """Add steps to a test case using separate API calls.

        Args:
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

            current_parent_id: int | None = None
            last_child_id: int | None = None

            # Action Step (body step)
            if action:
                step_dto = self._build_scenario_step_dto(test_case_id=test_case_id, body=action)
                response = await self._client.create_scenario_step(
                    test_case_id=test_case_id,
                    step=step_dto,
                    after_id=last_step_id,
                )
                current_parent_id = response.created_step_id
                last_step_id = current_parent_id

                # If there's an expected result, create it as a child step under the action
                if expected:
                    expected_step_dto = self._build_scenario_step_dto(
                        test_case_id=test_case_id,
                        body=expected,
                        parent_id=current_parent_id,
                    )
                    expected_response = await self._client.create_scenario_step(
                        test_case_id=test_case_id,
                        step=expected_step_dto,
                        after_id=None,  # First child
                    )
                    last_child_id = expected_response.created_step_id

                # Step Attachments (added as children of the action step)
                if step_attachments and isinstance(step_attachments, list):
                    for sa in step_attachments:
                        if isinstance(sa, dict):
                            attachment_row = await self._attachment_service.upload_attachment(test_case_id, sa)
                            attachment_step_dto = self._build_scenario_step_dto(
                                test_case_id=test_case_id,
                                attachment_id=attachment_row.id,
                                parent_id=current_parent_id,
                            )
                            attachment_response = await self._client.create_scenario_step(
                                test_case_id=test_case_id,
                                step=attachment_step_dto,
                                after_id=last_child_id,
                            )
                            last_child_id = attachment_response.created_step_id

        return last_step_id

    async def _add_global_attachments(
        self,
        test_case_id: int,
        attachments: list[dict[str, str]] | None,
        last_step_id: int | None,
    ) -> None:
        """Add global attachments to a test case as attachment steps.

        Args:
            test_case_id: Test case ID to add attachments to.
            attachments: List of attachment definitions.
            last_step_id: ID of the last created step (for ordering).
        """
        if not attachments:
            return

        for attachment in attachments:
            attachment_row = await self._attachment_service.upload_attachment(test_case_id, attachment)
            attachment_step_dto = self._build_scenario_step_dto(
                test_case_id=test_case_id,
                attachment_id=attachment_row.id,
            )
            response = await self._client.create_scenario_step(
                test_case_id=test_case_id,
                step=attachment_step_dto,
                after_id=last_step_id,
            )
            last_step_id = response.created_step_id
