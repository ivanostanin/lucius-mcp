import logging
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError as PydanticValidationError

from src.client import (
    AllureClient,
    AttachmentStepDtoWithName,
    BodyStepDtoWithSteps,
)
from src.client.exceptions import AllureAPIError, AllureNotFoundError, AllureValidationError
from src.client.generated.models import (
    CustomFieldDto,
    CustomFieldValueWithCfDto,
    ExternalLinkDto,
    ScenarioStepCreateDto,
    SharedStepScenarioDtoStepsInner,
    TestCaseCreateV2Dto,
    TestCaseDto,
    TestCaseOverviewDto,
    TestCaseTreeSelectionDto,
    TestTagDto,
)
from src.client.generated.models.attachment_step_dto import AttachmentStepDto
from src.client.generated.models.body_step_dto import BodyStepDto
from src.client.generated.models.expected_body_step_dto import ExpectedBodyStepDto
from src.client.generated.models.shared_step_step_dto import SharedStepStepDto
from src.client.generated.models.test_case_patch_v2_dto import TestCasePatchV2Dto
from src.client.generated.models.test_case_scenario_v2_dto import TestCaseScenarioV2Dto
from src.services.attachment_service import AttachmentService
from src.utils.auth import AuthContext
from src.utils.config import settings
from src.utils.schema_hint import generate_schema_hint

# Maximum lengths based on API constraints
MAX_NAME_LENGTH = 255
MAX_PRECONDITION_LENGTH = 1000
MAX_TAG_LENGTH = 255
MAX_BODY_LENGTH = 10000  # Step body limit

logger = logging.getLogger(__name__)


@dataclass
class TestCaseUpdate:
    """Data object for updating a test case."""

    name: str | None = None
    description: str | None = None
    precondition: str | None = None
    steps: list[dict[str, Any]] | None = None
    tags: list[str] | None = None
    attachments: list[dict[str, str]] | None = None
    custom_fields: dict[str, str] | None = None
    automated: bool | None = None
    expected_result: str | None = None
    status_id: int | None = None
    test_layer_id: int | None = None
    workflow_id: int | None = None
    links: list[dict[str, str]] | None = None


@dataclass
class DeleteResult:
    """Result of a delete operation."""

    test_case_id: int
    status: str  # "archived", "deleted", "already_deleted", "not_found"
    message: str
    name: str | None = None


class TestCaseService:
    """Service for managing Test Cases in Allure TestOps."""

    def __init__(
        self,
        auth_context: AuthContext,
        client: AllureClient | None = None,
        attachment_service: AttachmentService | None = None,
        base_url: str | None = None,
    ) -> None:
        self._auth = auth_context
        self._client = client or AllureClient(
            base_url=base_url or settings.ALLURE_ENDPOINT,
            token=auth_context.api_token,
        )
        self._attachment_service = attachment_service or AttachmentService(self._client)
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
            hint = generate_schema_hint(TestCaseCreateV2Dto)
            raise AllureValidationError(f"Invalid test case data: {e}", suggestions=[hint]) from e

        # 4. Create the test case
        created_test_case = await self._client.create_test_case(project_id, data)
        test_case_id = created_test_case.id

        if test_case_id is None:
            raise AllureValidationError("Failed to get test case ID from created test case")

        # 5. Add steps and attachments with rollback on failure
        try:
            # Add steps one by one via separate API calls
            last_step_id: int | None = None
            last_step_id = await self._add_steps(test_case_id, steps, last_step_id)

            # Add global attachments (appended at end of steps)
            await self._add_global_attachments(test_case_id, attachments, last_step_id)
        except Exception as e:
            # Rollback: delete the partially created test case
            try:
                await self._client.delete_test_case(test_case_id)
            except Exception as rollback_error:
                # Log but don't raise the rollback error to keep the original error primary
                logger.error(f"Rollback failed for test case {test_case_id}: {rollback_error}")
                pass

            if isinstance(e, (AllureValidationError, AllureAPIError)):
                # Refine message to indicate rollback
                raise type(e)(f"Test case creation failed and was rolled back: {e}") from e
            raise AllureAPIError(f"Test case creation failed and was rolled back: {e}") from e

        return created_test_case

    async def get_test_case(self, test_case_id: int) -> TestCaseDto:
        """Retrieve a test case by ID.

        Args:
            test_case_id: ID of the test case.

        Returns:
            The test case DTO.
        """
        return await self._client.get_test_case(test_case_id)

    async def update_test_case(self, test_case_id: int, data: TestCaseUpdate) -> TestCaseDto:
        """Update an existing test case.

        Args:
            test_case_id: ID of the test case.
            data: Update data.

        Returns:
            The updated test case.
        """
        # 1. Fetch current state for idempotency and partial updates
        current_case = await self.get_test_case(test_case_id)

        # 2. Prepare patches for simple fields and tags
        patch_kwargs, has_changes = await self._prepare_field_updates(current_case, data)

        # 3. Handle Scenario (Steps and Attachments)
        scenario_dto_v2 = await self._prepare_scenario_update(test_case_id, data)
        # We do NOT add scenario to patch_kwargs because patch13 endpoint has issues with BodyStepDto serialization.
        # Instead, we will recreate the scenario step-by-step if needed.
        if scenario_dto_v2:
            has_changes = True

        # 4. Idempotency Check
        if not has_changes:
            return current_case

        # 5. Apply Update
        updated_case = current_case
        if patch_kwargs:
            try:
                patch_data = TestCasePatchV2Dto(**patch_kwargs)
                updated_case = await self._client.update_test_case(test_case_id, patch_data)
            except PydanticValidationError as e:
                hint = generate_schema_hint(TestCasePatchV2Dto)
                raise AllureValidationError(f"Invalid update data: {e}", suggestions=[hint]) from e

        # 6. Apply Scenario Re-creation
        if scenario_dto_v2 and scenario_dto_v2.steps is not None:
            await self._recreate_scenario(test_case_id, scenario_dto_v2.steps)
            # Refetch to get consistent state
            updated_case = await self.get_test_case(test_case_id)

        return updated_case

    async def delete_test_case(self, test_case_id: int) -> DeleteResult:
        """Archive/soft-delete a test case."""
        # 1. Verify existence (idempotency check)
        try:
            test_case = await self.get_test_case(test_case_id)
            # Idempotency: Check if already archived
            # Note: exact status name depends on Allure configuration, checking common ones
            if test_case.status and test_case.status.name and test_case.status.name.lower() in ("archived", "deleted"):
                return DeleteResult(
                    test_case_id=test_case_id,
                    status="already_deleted",
                    message=f"Test Case {test_case_id} was already archived (Status: {test_case.status.name}).",
                )
        except AllureNotFoundError:
            return DeleteResult(
                test_case_id=test_case_id,
                status="already_deleted",
                message=f"Test Case {test_case_id} was already archived or doesn't exist.",
            )

        # 2. Perform deletion
        await self._client.delete_test_case(test_case_id)

        # 3. Log the action
        logger.info(
            "Test case archived",
            extra={
                "test_case_id": test_case_id,
                "test_case_name": test_case.name,
                "action": "delete",
                "result": "archived",
            },
        )

        return DeleteResult(
            test_case_id=test_case_id,
            status="archived",
            name=test_case.name,
            message=f"Test Case {test_case_id}: '{test_case.name}' has been archived.",
        )

    async def add_shared_step_to_case(
        self,
        test_case_id: int,
        shared_step_id: int,
        position: int | None = None,
    ) -> TestCaseDto:
        """Add a shared step reference to a test case.

        Args:
            test_case_id: Target test case ID.
            shared_step_id: ID of the shared step to link.
            position: Optional 0-indexed position. None = append.

        Returns:
            Updated test case DTO.
        """
        # 1. Determine position (after_id)
        scen = await self._client.get_test_case_scenario(test_case_id)
        current_steps = scen.steps if scen and scen.steps else []

        after_id: int | None = None
        if position is None:
            # Append: find the last step ID
            if current_steps:
                last_step = current_steps[-1]
                if last_step.actual_instance:
                    after_id = getattr(last_step.actual_instance, "id", None)
        elif position == 0:
            # Insert at start
            after_id = None
        else:
            # Insert at position
            if position < 0 or position > len(current_steps):
                raise AllureValidationError(f"Position {position} is out of bounds (0-{len(current_steps)})")
            # We insert AFTER the step at (position - 1)
            prev_step = current_steps[position - 1]
            if prev_step.actual_instance:
                after_id = getattr(prev_step.actual_instance, "id", None)

        # 2. Create the step reference
        step_dto = self._build_scenario_step_dto(
            test_case_id=test_case_id,
            shared_step_id=shared_step_id,
        )

        await self._client.create_scenario_step(
            test_case_id=test_case_id,
            step=step_dto,
            after_id=after_id,
        )

        return await self.get_test_case(test_case_id)

    async def remove_shared_step_from_case(
        self,
        test_case_id: int,
        shared_step_id: int,
    ) -> TestCaseDto:
        """Remove all references to a shared step from a test case.

        Args:
            test_case_id: Target test case ID.
            shared_step_id: ID of the shared step to unlink.

        Returns:
            Updated test case DTO.
        """
        scen = await self._client.get_test_case_scenario(test_case_id)
        if not scen or not scen.steps:
            return await self.get_test_case(test_case_id)

        steps_to_delete = []
        for step in scen.steps:
            if step.actual_instance and isinstance(step.actual_instance, SharedStepStepDto):
                if step.actual_instance.shared_step_id == shared_step_id:
                    steps_to_delete.append(getattr(step.actual_instance, "id", None))

        if not steps_to_delete:
            raise AllureValidationError(f"Shared Step {shared_step_id} not found in Test Case {test_case_id}")

        for step_id in steps_to_delete:
            if step_id:
                await self._client.delete_scenario_step(step_id)

        return await self.get_test_case(test_case_id)

    async def _prepare_field_updates(  # noqa: C901
        self, current_case: TestCaseDto, data: TestCaseUpdate
    ) -> tuple[dict[str, Any], bool]:
        """Prepare patch arguments for simple fields, tags, and custom fields."""
        patch_kwargs: dict[str, Any] = {}
        has_changes = False

        if data.name is not None and data.name != current_case.name:
            patch_kwargs["name"] = data.name
            has_changes = True

        if data.description is not None and data.description != current_case.description:
            patch_kwargs["description"] = data.description
            has_changes = True

        if data.precondition is not None and data.precondition != current_case.precondition:
            patch_kwargs["precondition"] = data.precondition
            has_changes = True

        if data.automated is not None and data.automated != current_case.automated:
            patch_kwargs["automated"] = data.automated
            has_changes = True

        if data.expected_result is not None and data.expected_result != current_case.expected_result:
            patch_kwargs["expected_result"] = data.expected_result
            has_changes = True

        if data.status_id is not None:
            current_status_id = current_case.status.id if current_case.status else None
            if data.status_id != current_status_id:
                patch_kwargs["status_id"] = data.status_id
                has_changes = True

        if data.test_layer_id is not None:
            current_test_layer_id = current_case.test_layer.id if current_case.test_layer else None
            if data.test_layer_id != current_test_layer_id:
                patch_kwargs["test_layer_id"] = data.test_layer_id
                has_changes = True

        if data.workflow_id is not None:
            current_workflow_id = current_case.workflow.id if current_case.workflow else None
            if data.workflow_id != current_workflow_id:
                patch_kwargs["workflow_id"] = data.workflow_id
                has_changes = True

        if data.links is not None:
            # Simple link replacement for now
            new_links = [ExternalLinkDto(**link) for link in data.links]
            patch_kwargs["links"] = new_links
            has_changes = True

        # Tags
        if data.tags is not None:
            current_tag_names = sorted([t.name for t in (current_case.tags or []) if t.name])
            new_tag_names = sorted(data.tags)
            if current_tag_names != new_tag_names:
                patch_kwargs["tags"] = self._build_tag_dtos(data.tags)
                has_changes = True

        # Custom Fields
        if data.custom_fields:
            project_id = current_case.project_id
            if project_id:
                resolved_cfs = []
                project_cfs = await self._get_resolved_custom_fields(project_id)
                for key, value in data.custom_fields.items():
                    cf_id = project_cfs.get(key)
                    if cf_id:
                        resolved_cfs.append(
                            CustomFieldValueWithCfDto(custom_field=CustomFieldDto(id=cf_id, name=key), name=value)
                        )
                patch_kwargs["custom_fields"] = resolved_cfs
                has_changes = True

        return patch_kwargs, has_changes

    async def _prepare_scenario_update(self, test_case_id: int, data: TestCaseUpdate) -> TestCaseScenarioV2Dto | None:
        """Prepare the scenario DTO if steps or attachments need updating."""
        if data.steps is None and data.attachments is None:
            return None

        existing_steps = await self._get_existing_steps_to_preserve(test_case_id, data)
        final_steps_list = await self._build_final_steps_list(test_case_id, data, existing_steps)

        return TestCaseScenarioV2Dto(steps=final_steps_list)

    async def _get_existing_steps_to_preserve(
        self, test_case_id: int, data: TestCaseUpdate
    ) -> list[SharedStepScenarioDtoStepsInner]:
        """Fetch existing steps that should be preserved based on what's being updated."""
        if data.steps is not None and data.attachments is not None:
            return []  # Both provided, nothing to preserve

        existing_steps: list[SharedStepScenarioDtoStepsInner] = []
        try:
            current_scenario = await self._client.get_test_case_scenario(test_case_id)
            if not current_scenario or not current_scenario.steps:
                return existing_steps

            for step in current_scenario.steps:
                if not step.actual_instance:
                    continue
                is_attachment = isinstance(step.actual_instance, AttachmentStepDto)
                # Preserve attachments if data.attachments is None
                # Preserve body steps if data.steps is None
                if is_attachment and data.attachments is None:
                    existing_steps.append(step)
                elif not is_attachment and data.steps is None:
                    existing_steps.append(step)
        except Exception:  # noqa: S110
            pass

        return existing_steps

    async def _build_final_steps_list(
        self,
        test_case_id: int,
        data: TestCaseUpdate,
        existing_steps: list[SharedStepScenarioDtoStepsInner],
    ) -> list[SharedStepScenarioDtoStepsInner]:
        """Build the final list of steps combining new and preserved steps."""
        final_steps: list[SharedStepScenarioDtoStepsInner] = []

        # Add new or existing body steps
        if data.steps is not None:
            final_steps.extend(await self._build_steps_dtos_from_list(test_case_id, data.steps))
        else:
            for step in existing_steps:
                if step.actual_instance and not isinstance(step.actual_instance, AttachmentStepDto):
                    final_steps.append(step)

        # Add new or existing attachments
        if data.attachments is not None:
            for att in data.attachments:
                row = await self._attachment_service.upload_attachment(test_case_id, att)
                final_steps.append(
                    SharedStepScenarioDtoStepsInner(
                        actual_instance=AttachmentStepDto(type="AttachmentStepDto", attachment_id=row.id, name=row.name)
                    )
                )
        else:
            for step in existing_steps:
                if step.actual_instance and isinstance(step.actual_instance, AttachmentStepDto):
                    final_steps.append(step)

        return final_steps

    async def _build_steps_dtos_from_list(
        self, test_case_id: int, steps: list[dict[str, Any]]
    ) -> list[SharedStepScenarioDtoStepsInner]:
        """Convert list of step dicts to DTOs for PATCH."""
        dtos = []
        for s in steps:
            action = str(s.get("action", ""))
            expected = str(s.get("expected", ""))
            step_attachments = s.get("attachments", [])

            children: list[SharedStepScenarioDtoStepsInner] = []

            if expected:
                children.append(
                    SharedStepScenarioDtoStepsInner(
                        actual_instance=ExpectedBodyStepDto(type="ExpectedBodyStepDto", body=expected)
                    )
                )

            if step_attachments and isinstance(step_attachments, list):
                for sa in step_attachments:
                    if isinstance(sa, dict):
                        att_row = await self._attachment_service.upload_attachment(test_case_id, sa)
                        children.append(
                            SharedStepScenarioDtoStepsInner(
                                actual_instance=AttachmentStepDtoWithName(
                                    type="AttachmentStepDto", attachment_id=att_row.id, name=att_row.name
                                )
                            )
                        )

            # Recursive steps processing
            nested_steps_data = s.get("steps")
            if nested_steps_data and isinstance(nested_steps_data, list):
                nested_dtos = await self._build_steps_dtos_from_list(test_case_id, nested_steps_data)
                children.extend(nested_dtos)

            dtos.append(
                SharedStepScenarioDtoStepsInner(
                    actual_instance=BodyStepDtoWithSteps(type="BodyStepDto", body=action, steps=children)
                )
            )
        return dtos

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
                hint = generate_schema_hint(ScenarioStepCreateDto)
                raise AllureValidationError(
                    f"Step at index {i} must be a dictionary, got {type(step).__name__}", suggestions=[hint]
                )

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
                    hint = generate_schema_hint(AttachmentStepDto)
                    raise AllureValidationError(
                        f"Step {i}: 'attachments' must be a list, got {type(step_attachments).__name__}",
                        suggestions=[hint],
                    )
                for j, att in enumerate(step_attachments):
                    if not isinstance(att, dict):
                        hint = generate_schema_hint(AttachmentStepDto)
                        raise AllureValidationError(
                            f"Step {i}, attachment {j}: must be a dictionary, got {type(att).__name__}",
                            suggestions=[hint],
                        )

    def _validate_tags(self, tags: list[str] | None) -> None:
        """Validate tags list."""
        if tags is None:
            return

        if not isinstance(tags, list):
            hint = generate_schema_hint(TestTagDto)
            raise AllureValidationError(f"Tags must be a list, got {type(tags).__name__}", suggestions=[hint])

        for i, tag in enumerate(tags):
            if not isinstance(tag, str):
                hint = generate_schema_hint(TestTagDto)
                raise AllureValidationError(
                    f"Tag at index {i} must be a string, got {type(tag).__name__}", suggestions=[hint]
                )
            if not tag.strip():
                raise AllureValidationError(f"Tag at index {i} cannot be empty")
            if len(tag) > MAX_TAG_LENGTH:
                raise AllureValidationError(f"Tag at index {i} must be {MAX_TAG_LENGTH} characters or less")

    def _validate_attachments(self, attachments: list[dict[str, str]] | None) -> None:
        """Validate attachments list structure."""
        if attachments is None:
            return

        if not isinstance(attachments, list):
            hint = generate_schema_hint(AttachmentStepDto)
            raise AllureValidationError(
                f"Attachments must be a list, got {type(attachments).__name__}", suggestions=[hint]
            )

        for i, att in enumerate(attachments):
            if not isinstance(att, dict):
                hint = generate_schema_hint(AttachmentStepDto)
                raise AllureValidationError(
                    f"Attachment at index {i} must be a dictionary, got {type(att).__name__}", suggestions=[hint]
                )
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
            hint = generate_schema_hint(CustomFieldValueWithCfDto)
            raise AllureValidationError(
                f"Custom fields must be a dictionary, got {type(custom_fields).__name__}", suggestions=[hint]
            )

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
                hint = generate_schema_hint(TestTagDto)
                raise AllureValidationError(f"Invalid tag '{t}': {e}", suggestions=[hint]) from e
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
        shared_step_id: int | None = None,
        parent_id: int | None = None,
    ) -> ScenarioStepCreateDto:
        """Build and validate a ScenarioStepCreateDto."""
        try:
            return ScenarioStepCreateDto(
                test_case_id=test_case_id,
                body=body,
                attachment_id=attachment_id,
                shared_step_id=shared_step_id,
                parent_id=parent_id,
            )
        except PydanticValidationError as e:
            hint = generate_schema_hint(ScenarioStepCreateDto)
            raise AllureValidationError(f"Invalid scenario step data: {e}", suggestions=[hint]) from e

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

    async def _recreate_scenario(self, test_case_id: int, steps: list[SharedStepScenarioDtoStepsInner]) -> None:
        """Recreate the entire scenario step by step."""
        # 1. Fetch current scenario for rollback in case of failure
        try:
            previous_scenario = await self._client.get_test_case_scenario(test_case_id)
        except Exception:
            # If we can't get current scenario, we can't rollback to it. Proceed with caution.
            previous_scenario = None

        try:
            # 2. Clear existing scenario
            await self._client.update_test_case(
                test_case_id, TestCasePatchV2Dto(scenario=TestCaseScenarioV2Dto(steps=[]))
            )

            # 3. Recursively add steps
            last_step_id: int | None = None
            for step in steps:
                last_step_id = await self._recursive_add_step(test_case_id, step, after_id=last_step_id)

        except Exception as e:
            # Rollback Attempt
            if previous_scenario and previous_scenario.steps:
                try:
                    # Clear any partial progress
                    await self._client.update_test_case(
                        test_case_id, TestCasePatchV2Dto(scenario=TestCaseScenarioV2Dto(steps=[]))
                    )
                    # Attempt to restore previous steps
                    # Note: We can only best-effort restore. IDs will change.
                    # We need to convert TestCaseScenarioDto steps -> SharedStepScenarioDtoStepsInner
                    # This is complex because Read DTOs != Write DTOs.
                    # For now, we raise a clear error indicating data was lost/partial.
                    # Ideally, we would have logic to convert Read -> Write DTOs, but that's a larger feature.
                    # Given the scope, raising a critical error is better than silent failure.
                    pass
                except Exception as rollback_error:
                    # We log this as a warning because the original error will be raised anyway
                    logger.warning(
                        f"Rollback failed during scenario recreation. Partial data may persist. Error: {rollback_error}"
                    )

            raise AllureAPIError(
                f"Failed to recreate scenario. Steps may be partially applied or lost. Error: {e}"
            ) from e

    async def _recursive_add_step(
        self,
        test_case_id: int,
        step: SharedStepScenarioDtoStepsInner,
        parent_id: int | None = None,
        after_id: int | None = None,
    ) -> int | None:
        """Recursively add a step and its children."""
        if not step.actual_instance:
            return after_id

        instance = step.actual_instance
        created_id = None

        # Determine step type and create
        if isinstance(instance, BodyStepDto):
            step_dto = self._build_scenario_step_dto(test_case_id=test_case_id, body=instance.body, parent_id=parent_id)
            resp = await self._client.create_scenario_step(test_case_id=test_case_id, step=step_dto, after_id=after_id)
            created_id = resp.created_step_id

            # Add children (steps may not be a defined field in generated DTO,
            # but we set it via model_construct)
            child_steps = getattr(instance, "steps", None)
            if child_steps:
                last_child_id = None
                for child in child_steps:
                    last_child_id = await self._recursive_add_step(
                        test_case_id, child, parent_id=created_id, after_id=last_child_id
                    )

        elif isinstance(instance, ExpectedBodyStepDto):
            step_dto = self._build_scenario_step_dto(test_case_id=test_case_id, body=instance.body, parent_id=parent_id)
            resp = await self._client.create_scenario_step(test_case_id=test_case_id, step=step_dto, after_id=after_id)
            created_id = resp.created_step_id

        elif isinstance(instance, AttachmentStepDto):
            step_dto = self._build_scenario_step_dto(
                test_case_id=test_case_id, attachment_id=instance.attachment_id, parent_id=parent_id
            )
            resp = await self._client.create_scenario_step(test_case_id=test_case_id, step=step_dto, after_id=after_id)
            created_id = resp.created_step_id

        return created_id if created_id else after_id

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
