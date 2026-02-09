import logging
import re
from dataclasses import dataclass
from typing import TypedDict, cast

from pydantic import ValidationError as PydanticValidationError

from src.client import (
    AllureClient,
    AttachmentStepDtoWithName,
    StepWithExpected,
    TestCaseDtoWithCF,
)
from src.client.exceptions import AllureAPIError, AllureNotFoundError, AllureValidationError
from src.client.generated.models import (
    CustomFieldDto,
    CustomFieldValueDto,
    CustomFieldValueWithCfDto,
    ExternalLinkDto,
    IssueDto,
    ScenarioStepCreateDto,
    SharedStepScenarioDtoStepsInner,
    TestCaseBulkIssueDto,
    TestCaseCreateV2Dto,
    TestCaseDto,
    TestCaseOverviewDto,
    TestCaseTreeSelectionDto,
    TestLayerDto,
    TestTagDto,
)
from src.client.generated.models.attachment_step_dto import AttachmentStepDto
from src.client.generated.models.body_step_dto import BodyStepDto
from src.client.generated.models.expected_body_step_dto import ExpectedBodyStepDto
from src.client.generated.models.shared_step_step_dto import SharedStepStepDto
from src.client.generated.models.test_case_patch_v2_dto import TestCasePatchV2Dto
from src.client.generated.models.test_case_scenario_v2_dto import TestCaseScenarioV2Dto
from src.services.attachment_service import AttachmentService
from src.services.test_layer_service import TestLayerService
from src.utils.schema_hint import generate_schema_hint

# Maximum lengths based on API constraints
MAX_NAME_LENGTH = 255
MAX_PRECONDITION_LENGTH = 1000
MAX_TAG_LENGTH = 255
MAX_BODY_LENGTH = 10000  # Step body limit

logger = logging.getLogger(__name__)


class ResolvedCustomFieldInfo(TypedDict):
    id: int
    project_cf_id: int
    required: bool
    single_select: bool | None
    values: list[str]
    values_map: dict[str, int | None]


class CustomFieldDisplay(TypedDict):
    name: str
    required: bool
    values: list[str]


@dataclass
class TestCaseUpdate:
    """Data object for updating a test case."""

    name: str | None = None
    description: str | None = None
    precondition: str | None = None
    steps: list[dict[str, object]] | None = None
    tags: list[str] | None = None
    attachments: list[dict[str, str]] | None = None
    custom_fields: dict[str, str | list[str]] | None = None
    automated: bool | None = None
    expected_result: str | None = None
    status_id: int | None = None
    test_layer_id: int | None = None
    test_layer_name: str | None = None
    workflow_id: int | None = None
    links: list[dict[str, str]] | None = None
    issues: list[str] | None = None
    remove_issues: list[str] | None = None
    clear_issues: bool | None = None
    integration_id: int | None = None
    integration_name: str | None = None


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
        client: AllureClient,
        attachment_service: AttachmentService | None = None,
        test_layer_service: TestLayerService | None = None,
    ) -> None:
        self._client = client
        self._project_id = client.get_project()
        self._attachment_service = attachment_service or AttachmentService(self._client)
        self._test_layer_service = test_layer_service or TestLayerService(self._client)
        # {project_id: {name: {"id": int, "values": list[str]}}}
        self._cf_cache: dict[int, dict[str, ResolvedCustomFieldInfo]] = {}

    async def create_test_case(  # noqa: C901
        self,
        name: str,
        description: str | None = None,
        steps: list[dict[str, object]] | None = None,
        tags: list[str] | None = None,
        attachments: list[dict[str, str]] | None = None,
        custom_fields: dict[str, str | list[str]] | None = None,
        test_layer_id: int | None = None,
        test_layer_name: str | None = None,
        issues: list[str] | None = None,
        integration_id: int | None = None,
        integration_name: str | None = None,
    ) -> TestCaseOverviewDto:
        """Create a new test case.

        Args:
            name: The name of the test case.
            description: Optional description.
            steps: Optional list of steps [{'action': '...', 'expected': '...', 'attachments': [...]}]
            tags: Optional list of tags.
            attachments: Optional list of test-case level attachments.
            custom_fields: Optional dictionary of custom fields (Name -> Value).
            test_layer_id: Optional test layer ID to assign to the test case.
            test_layer_name: Optional test layer name to assign to the test case.
            issues: Optional list of issue keys to link (e.g., 'PROJ-123').
            integration_id: Optional integration ID for issue linking (required when multiple exist).
            integration_name: Optional integration name for issue linking (mutually exclusive with integration_id).

        Returns:
            The created test case overview.

        Raises:
            AllureAPIError: If the API request fails.
            AllureValidationError: If validation fails.
        """
        # 1. Input Validation
        self._validate_project_id(self._project_id)
        self._validate_name(name)
        self._validate_steps(steps)
        self._validate_tags(tags)
        self._validate_attachments(attachments)
        self._validate_custom_fields(custom_fields)

        # 2. Resolve test layer if provided
        resolved_test_layer_id = await self._validate_test_layer(
            test_layer_id=test_layer_id,
            test_layer_name=test_layer_name,
        )

        # 3. Resolve custom fields if provided
        resolved_custom_fields: list[CustomFieldValueWithCfDto] = []
        if custom_fields:
            project_cfs = await self._get_resolved_custom_fields(self._project_id)
            missing_fields: list[str] = []
            invalid_values: list[str] = []

            for key, value in custom_fields.items():
                cf_info = project_cfs.get(key)
                if cf_info is None:
                    missing_fields.append(key)
                    continue

                cf_id = cf_info["id"]
                allowed_values = cf_info["values"]
                values_map = cf_info["values_map"]

                if allowed_values:
                    invalid_for_field = False
                    input_values = [value] if isinstance(value, str) else value
                    for item in input_values:
                        if item not in allowed_values:
                            invalid_values.append(f"'{key}': '{item}' (Allowed: {', '.join(allowed_values)})")
                            invalid_for_field = True
                    if invalid_for_field:
                        continue
                else:
                    input_values = [value] if isinstance(value, str) else value

                for item in input_values:
                    val_id = values_map.get(item)
                    resolved_custom_fields.append(
                        CustomFieldValueWithCfDto(custom_field=CustomFieldDto(id=cf_id, name=key), id=val_id, name=item)
                    )

            error_messages = []

            if missing_fields:
                missing_list_str = "\n".join([f"- {name}" for name in missing_fields])
                error_messages.append(
                    f"The following custom fields were not found in project {self._project_id}:\n{missing_list_str}"
                )

            if invalid_values:
                invalid_list_str = "\n".join([f"- {item}" for item in invalid_values])
                error_messages.append(f"The following custom field values are invalid:\n{invalid_list_str}")

            if error_messages:
                full_error_msg = "\n\n".join(error_messages) + (
                    "\n\nUsage Hint:\n"
                    "1. Exclude all missing custom fields from your request.\n"
                    "2. Correct any invalid values to match the allowed options.\n"
                    "3. Only include fields that explicitly exist in the project configuration."
                )
                raise AllureValidationError(full_error_msg)

        # 4. Create TestCaseCreateV2Dto with validation
        tag_dtos = self._build_tag_dtos(tags)
        try:
            data = TestCaseCreateV2Dto(
                project_id=self._project_id,
                name=name,
                description=description,
                tags=tag_dtos,
                custom_fields=resolved_custom_fields,
                test_layer_id=resolved_test_layer_id,
            )
        except PydanticValidationError as e:
            hint = generate_schema_hint(TestCaseCreateV2Dto)
            raise AllureValidationError(f"Invalid test case data: {e}", suggestions=[hint]) from e

        # 5. Create the test case
        created_test_case = await self._client.create_test_case(data)
        test_case_id = created_test_case.id

        if test_case_id is None:
            raise AllureValidationError("Failed to get test case ID from created test case")

        # 6. Add steps and attachments with rollback on failure
        try:
            # Add steps one by one via separate API calls
            last_step_id: int | None = None
            last_step_id = await self._add_steps(test_case_id, steps, last_step_id)

            # Add global attachments (appended at end of steps)
            await self._add_global_attachments(test_case_id, attachments, last_step_id)

            # Add issue links
            if issues:
                await self.add_issues_to_test_case(
                    test_case_id,
                    issues,
                    integration_id=integration_id,
                    integration_name=integration_name,
                )
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

    async def get_test_case(self, test_case_id: int) -> TestCaseDtoWithCF:
        """Retrieve a test case by ID.

        Args:
            test_case_id: ID of the test case.

        Returns:
            The test case DTO.
        """
        return await self._client.get_test_case(test_case_id)

    async def get_custom_fields(self, name: str | None = None) -> list[CustomFieldDisplay]:
        """Get custom fields for the project with optional name filtering.

        This method uses the internal cache to avoid duplicate API calls when
        both get_custom_fields and create_test_case are used in the same session.
        """
        # Use cached resolution method to get field mapping
        cf_mapping = await self._get_resolved_custom_fields(self._project_id)

        result: list[CustomFieldDisplay] = []
        filter_name = name.lower() if name else None

        # Convert the cached mapping back to the display format
        for field_name, field_info in cf_mapping.items():
            if filter_name and filter_name not in field_name.lower():
                continue

            result.append({"name": field_name, "required": field_info["required"], "values": field_info["values"]})

        return result

    async def get_test_case_custom_fields_values(self, test_case_id: int) -> dict[str, str | list[str]]:
        """Fetch custom field values for a test case.

        Returns:
            Dictionary of {custom_field_name: value(s)}.
            Single value return as scalar, multiple/empty as list.
        """
        cfs = await self._client.get_test_case_custom_fields(test_case_id, self._project_id)
        result: dict[str, str | list[str]] = {}
        for cf in cfs:
            if cf.custom_field and cf.custom_field.custom_field and cf.custom_field.custom_field.name:
                name = cf.custom_field.custom_field.name
                values = cf.values or []
                # Normalize: Single value -> Scalar, else List
                if len(values) == 1:
                    single_name = values[0].name
                    result[name] = single_name if single_name is not None else []
                else:
                    result[name] = [v.name for v in values if v.name is not None]
        return result

    async def update_test_case_custom_fields(
        self, test_case_id: int, custom_fields: dict[str, str | list[str]]
    ) -> list[CustomFieldValueWithCfDto]:
        """Update only custom fields via dedicated endpoint.

        Args:
            test_case_id: ID of the test case.
            custom_fields: Mapping of Names -> Value(s).

        Returns:
            List of updated CF DTOs.
        """
        resolved_dtos = await self._build_custom_field_dtos(self._project_id, custom_fields)
        await self._client.update_test_case_custom_fields(test_case_id, resolved_dtos)
        return resolved_dtos

    async def update_test_case(self, test_case_id: int, data: TestCaseUpdate) -> TestCaseDto:  # noqa: C901
        """Update an existing test case.

        Args:
            test_case_id: ID of the test case.
            data: Update data.

        Returns:
            The updated test case.
        """
        # 1. Fetch current state for idempotency and partial updates
        current_case = await self.get_test_case(test_case_id)
        project_id = current_case.project_id or self._project_id

        # 2. Check if we can use the dedicated CF endpoint
        # If ONLY custom_fields are provided, use the dedicated endpoint
        has_metadata_changes = any(
            [
                data.name is not None,
                data.description is not None,
                data.precondition is not None,
                data.tags is not None,
                data.automated is not None,
                data.expected_result is not None,
                data.status_id is not None,
                data.test_layer_id is not None,
                data.workflow_id is not None,
                data.links is not None,
                data.issues is not None,
                data.remove_issues is not None,
                data.clear_issues is not None,
            ]
        )
        has_scenario_changes = data.steps is not None or data.attachments is not None
        if data.custom_fields is not None and not (has_metadata_changes or has_scenario_changes):
            current_cf_values = await self.get_test_case_custom_fields_values(test_case_id)
            current_normalized = self._normalize_custom_field_values_map(current_cf_values, drop_empty=False)
            desired_normalized = self._normalize_custom_field_values_map(data.custom_fields, drop_empty=False)
            if current_normalized == desired_normalized:
                return current_case
            await self.update_test_case_custom_fields(test_case_id, data.custom_fields)
            updated_case = await self.get_test_case(test_case_id)
            return updated_case if updated_case is not None else current_case

        if data.clear_issues:
            # Use current_case fetched at step 1 instead of re-fetching
            if current_case and current_case.issues:
                existing_keys = [i.name for i in current_case.issues if i.name]
                if existing_keys:
                    await self.remove_issues_from_test_case(test_case_id, existing_keys)

        if data.remove_issues:
            await self.remove_issues_from_test_case(test_case_id, data.remove_issues)

        if data.issues:
            await self.add_issues_to_test_case(
                test_case_id,
                data.issues,
                integration_id=data.integration_id,
                integration_name=data.integration_name,
            )

        # 4. Handle Metadata Patches
        patch_kwargs, has_changes = await self._prepare_field_updates(current_case, data)

        if data.test_layer_id is not None or data.test_layer_name is not None:
            current_test_layer_id = current_case.test_layer.id if current_case.test_layer else None
            resolved_layer_id = None
            skip_validation = False

            if data.test_layer_id is not None and data.test_layer_name is None:
                if data.test_layer_id == current_test_layer_id:
                    skip_validation = True
                    resolved_layer_id = data.test_layer_id

            if not skip_validation:
                # Resolve the ID using the validation helper
                # Note: _validate_test_layer handles mutual exclusivity check
                resolved_layer_id = await self._validate_test_layer(
                    test_layer_id=data.test_layer_id,
                    test_layer_name=data.test_layer_name,
                )

            current_test_layer_id = current_case.test_layer.id if current_case.test_layer else None

            # Only update if the resolved ID is different (and not None)
            if resolved_layer_id is not None and resolved_layer_id != current_test_layer_id:
                # Add to patch_kwargs which is now initialized
                patch_kwargs["test_layer_id"] = resolved_layer_id
                has_changes = True

        # 5. Handle Custom Fields in mixed update (replacement)
        if data.custom_fields is not None:
            # For mixed updates via patch13, we need to provide the FULL list of custom fields
            # since the API replaces them. We merge current + updates.
            current_cf_dtos = await self._client.get_test_case_custom_fields(test_case_id, project_id)

            # Build map of {field_name: CustomFieldValueWithCfDto[]}
            # We use list of DTOs to support multi-value fields in the map
            cf_map: dict[str, list[CustomFieldValueWithCfDto]] = {}
            for cf in current_cf_dtos:
                if cf.custom_field and cf.custom_field.custom_field and cf.custom_field.custom_field.name:
                    fname = cf.custom_field.custom_field.name
                    fid = cf.custom_field.custom_field.id
                    cf_map[fname] = [
                        CustomFieldValueWithCfDto(
                            custom_field=CustomFieldDto(id=fid, name=fname),
                            id=v.id,
                            name=v.name,
                        )
                        for v in (cf.values or [])
                    ]

            # Resolve New Field DTOs
            new_cf_dtos = await self._build_custom_field_dtos_legacy(project_id, data.custom_fields)

            # Merge into map
            for cf_dto in new_cf_dtos:
                custom_field = cf_dto.custom_field
                if custom_field is None or custom_field.name is None:
                    continue
                fname = custom_field.name
                if cf_dto.id is None and cf_dto.name is None:  # Clear indicator in building logic
                    cf_map.pop(fname, None)
                else:
                    # _build_custom_field_dtos_legacy returns flattened list, so we group them
                    if fname not in cf_map or data.custom_fields.get(fname) is not None:
                        # If explicitly mentioned in updates, replace entire field value list
                        cf_map[fname] = [cf_dto]
                    else:
                        # Append? No, the legacy builder for patch13 is tricky.
                        # Actually, if it's in data.custom_fields, we should have processed it already.
                        pass

            # Flatten map back to list
            final_cfs: list[CustomFieldValueWithCfDto] = []
            for item_list in cf_map.values():
                final_cfs.extend(item_list)

            current_cf_values = await self.get_test_case_custom_fields_values(test_case_id)
            current_normalized = self._normalize_custom_field_values_map(current_cf_values, drop_empty=True)
            desired_normalized = self._normalize_custom_field_values_map(data.custom_fields, drop_empty=True)
            if current_normalized != desired_normalized:
                patch_kwargs["customFields"] = final_cfs
                has_changes = True

        # 6. Handle Scenario
        scenario_dto_v2 = await self._prepare_scenario_update(test_case_id, data)
        if scenario_dto_v2:
            has_changes = True

        if not has_changes:
            return current_case

        # 7. Apply Update
        try:
            patch_data = TestCasePatchV2Dto(**patch_kwargs)
            await self._client.update_test_case(test_case_id, patch_data)
        except PydanticValidationError as e:
            hint = generate_schema_hint(TestCasePatchV2Dto)
            raise AllureValidationError(f"Invalid update data: {e}", suggestions=[hint]) from e

        # 8. Apply Scenario Re-creation
        if scenario_dto_v2 and scenario_dto_v2.steps is not None:
            await self._recreate_scenario(test_case_id, scenario_dto_v2.steps)

        updated_case = await self.get_test_case(test_case_id)
        return updated_case if updated_case is not None else current_case

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

    async def add_issues_to_test_case(
        self,
        test_case_id: int,
        issues: list[str],
        integration_id: int | None = None,
        integration_name: str | None = None,
    ) -> None:
        """Add issue links to a test case.

        Args:
            test_case_id: The test case ID.
            issues: List of issue keys (e.g. "PROJ-123").
            integration_id: Optional integration ID (required when multiple exist).
            integration_name: Optional integration name (mutually exclusive with integration_id).
        """
        if not issues:
            return

        # 1. Resolve integrations and build IssueDtos
        issue_dtos = await self._build_issue_dtos(
            issues,
            integration_id=integration_id,
            integration_name=integration_name,
        )

        # Idempotency Filter: Only link issues not already present
        current_case = await self.get_test_case(test_case_id)
        existing_names = {i.name.upper() for i in (current_case.issues or []) if i.name}
        issue_dtos = [io for io in issue_dtos if io.name not in existing_names]

        if not issue_dtos:
            return

        # 2. Build selection
        selection = TestCaseTreeSelectionDto(project_id=self._project_id, leafs_include=[test_case_id])

        # 3. Call Bulk API
        from src.client.generated.api.test_case_bulk_controller_api import TestCaseBulkControllerApi

        bulk_api = TestCaseBulkControllerApi(self._client.api_client)

        bulk_dto = TestCaseBulkIssueDto(issues=issue_dtos, selection=selection)
        await bulk_api.issue_add1(bulk_dto)

    async def remove_issues_from_test_case(self, test_case_id: int, issues: list[str]) -> None:
        """Remove issue links from a test case.

        Args:
            test_case_id: The test case ID.
            issues: List of issue keys to remove.
        """
        if not issues:
            return

        # 1. Fetch current issues to get their IDs
        current_case = await self.get_test_case(test_case_id)
        if not current_case.issues:
            return

        # 2. Find IDs of issues to remove
        issues_to_remove_ids = []
        issues_set = set(issues)

        for issue in current_case.issues:
            if issue.name and issue.name in issues_set and issue.id:
                issues_to_remove_ids.append(issue.id)

        if not issues_to_remove_ids:
            return

        # 3. Call Bulk API with IDs
        selection = TestCaseTreeSelectionDto(project_id=self._project_id, leafs_include=[test_case_id])

        from src.client.generated.api.test_case_bulk_controller_api import TestCaseBulkControllerApi
        from src.client.generated.models.test_case_bulk_entity_ids_dto import TestCaseBulkEntityIdsDto

        bulk_api = TestCaseBulkControllerApi(self._client.api_client)

        bulk_dto = TestCaseBulkEntityIdsDto(ids=issues_to_remove_ids, selection=selection)
        await bulk_api.issue_remove1(bulk_dto)

    MAX_ISSUE_KEY_LENGTH = 50
    ISSUE_KEY_PATTERN = re.compile(r"^[A-Z0-9]+-\d+$", re.IGNORECASE)

    async def _build_issue_dtos(
        self,
        issues: list[str],
        integration_id: int | None = None,
        integration_name: str | None = None,
    ) -> list[IssueDto]:
        """Convert issue keys to IssueDto objects with resolved integration IDs.

        Validation:
        - Checks issue key format (e.g., PROJ-123).
        - Resolves integration ID using IntegrationService.
        - AC#6: Auto-selects when only one integration exists.
        - AC#7: Errors when multiple integrations exist and none specified.
        """
        if not issues:
            return []

        # 1. Validate Issue Keys
        invalid_keys = []
        for key in issues:
            if not key or len(key) > self.MAX_ISSUE_KEY_LENGTH:
                invalid_keys.append(f"{key} (too long)")
            elif not self.ISSUE_KEY_PATTERN.match(key):
                invalid_keys.append(f"{key} (invalid format, expected PROJECT-123)")

        if invalid_keys:
            raise AllureValidationError(
                "Invalid issue keys provided:\n"
                + "\n".join(f"- {k}" for k in invalid_keys)
                + "\n\nHint: Issue keys must follow the format 'PROJECT-123' (alphanumeric prefix, hyphen, number)."
            )

        # 2. Resolve Integration using IntegrationService
        from src.services.integration_service import IntegrationService

        integration_service = IntegrationService(self._client)
        target_integration_id = await integration_service.resolve_integration_for_issues(
            integration_id=integration_id,
            integration_name=integration_name,
        )

        # 3. Build DTOs
        dtos = []
        for key in issues:
            dto = IssueDto(name=key.upper(), integration_id=target_integration_id)  # Normalize to uppercase
            dtos.append(dto)

        return dtos

    async def _prepare_field_updates(  # noqa: C901
        self, current_case: TestCaseDto, data: TestCaseUpdate
    ) -> tuple[dict[str, object], bool]:
        """Prepare patch arguments for simple fields, tags, and custom fields."""
        patch_kwargs: dict[str, object] = {}
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

        # test_layer_id is handled centrally in update_test_case logic due to name resolution complexity
        # and validation requirements. We skip it here to avoid duplication.

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

                has_changes = True

        # Custom Fields are handled via dedicated endpoint in update_test_case
        # so we DO NOT add them to patch_kwargs here.

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
        self, test_case_id: int, steps: list[dict[str, object]]
    ) -> list[SharedStepScenarioDtoStepsInner]:
        """Convert list of step dicts to DTOs for PATCH."""
        dtos = []
        for s in steps:
            action = str(s.get("action", ""))
            expected = str(s.get("expected", ""))
            step_attachments = s.get("attachments", [])

            children: list[SharedStepScenarioDtoStepsInner] = []

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
                    actual_instance=StepWithExpected(
                        type="BodyStepDto",
                        body=action,
                        expected_result=expected or None,
                        steps=children,
                    )
                )
            )
        return dtos

    # ==========================================
    # Validation Methods
    # ==========================================

    def _validate_project_id(self, project_id: int | None) -> None:
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

    def _validate_steps(self, steps: list[dict[str, object]] | None) -> None:  # noqa: C901
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

    def _validate_custom_fields(self, custom_fields: dict[str, str | list[str]] | None) -> None:
        """Validate custom fields dictionary structure."""
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
            if not isinstance(value, (str, list)):
                raise AllureValidationError(
                    f"Custom field value for '{key}' must be a string or list of strings, got {type(value).__name__}"
                )
            if isinstance(value, list):
                for i, v in enumerate(value):
                    if not isinstance(v, str):
                        raise AllureValidationError(
                            f"Custom field '{key}' item {i} must be a string, got {type(v).__name__}"
                        )
            if not key.strip():
                raise AllureValidationError("Custom field key cannot be empty")

    def _validate_test_layer_id(self, test_layer_id: int | None) -> None:
        """Validate test layer ID format."""
        if test_layer_id is None:
            return
        if not isinstance(test_layer_id, int) or test_layer_id < 0:
            raise AllureValidationError("Test layer ID must be a positive integer or 0 (to unset)")

    def _format_available_layers(self, layers: list[TestLayerDto]) -> str:
        display_lines: list[str] = []
        for layer in layers[:10]:
            display_lines.append(f"ID: {layer.id}, Name: {layer.name}")
        if not display_lines:
            display_lines.append("(none)")
        return "\n".join(display_lines)

    async def _validate_test_layer_exists(self, test_layer_id: int, project_id: int) -> None:
        try:
            await self._test_layer_service.get_test_layer(test_layer_id)
        except AllureNotFoundError as e:
            layers = await self._test_layer_service.list_test_layers(page=0, size=100)
            available_layers = self._format_available_layers(layers)
            raise AllureValidationError(
                "\n".join(
                    [
                        f"Warning: Test layer ID {test_layer_id} does not exist in project {project_id}.",
                        "Test case update was not performed.",
                        "Available test layers (first 10):",
                        available_layers,
                        "Use list_test_layers(page=..., size=...) to see more.",
                        "To proceed without a test layer, omit test_layer_id.",
                    ]
                )
            ) from e
        except AllureAPIError as e:
            raise AllureValidationError(
                f"Unable to validate test layer ID {test_layer_id} for project {project_id}: {e}",
                suggestions=["Use list_test_layers to find valid IDs", "Check API connectivity and permissions"],
            ) from e

    async def _validate_test_layer(
        self,
        *,
        test_layer_id: int | None,
        test_layer_name: str | None,
    ) -> int | None:
        if test_layer_id is not None and test_layer_name is not None:
            raise AllureValidationError(
                "Provide only one of test_layer_id or test_layer_name (they are mutually exclusive)."
            )

        if test_layer_id is not None:
            self._validate_test_layer_id(test_layer_id)
            if test_layer_id == 0:
                return 0

            try:
                await self._test_layer_service.get_test_layer(test_layer_id)
            except AllureNotFoundError as e:
                layers = await self._test_layer_service.list_test_layers(page=0, size=100)
                available_layers = self._format_available_layers(layers)
                raise AllureValidationError(
                    "\n".join(
                        [
                            f"Warning: Test layer ID {test_layer_id} does not exist in project {self._project_id}.",
                            "Test case creation was not performed.",
                            "Available test layers (first 10):",
                            available_layers,
                            "Use list_test_layers(page=..., size=...) to see more.",
                            "To proceed without a test layer, omit test_layer_id/test_layer_name.",
                        ]
                    )
                ) from e
            except AllureAPIError as e:
                raise AllureValidationError(
                    f"Unable to validate test layer ID {test_layer_id} for project {self._project_id}: {e}",
                    suggestions=["Use list_test_layers to find valid IDs", "Check API connectivity and permissions"],
                ) from e
            return test_layer_id

        if test_layer_name is not None:
            layers = await self._test_layer_service.list_test_layers(page=0, size=100)
            matches = [layer for layer in layers if layer.name == test_layer_name]
            if len(matches) == 0:
                available_layers = self._format_available_layers(layers)
                raise AllureValidationError(
                    "\n".join(
                        [
                            f"Warning: Test layer name '{test_layer_name}' not found.",
                            "Test case creation was not performed.",
                            "Available test layers (first 10):",
                            available_layers,
                            "Use list_test_layers(page=..., size=...) to see more.",
                            "To proceed without a test layer, omit test_layer_id/test_layer_name.",
                        ]
                    )
                )
            if len(matches) > 1:
                match_lines = "\n".join([f"ID: {layer.id}, Name: {layer.name}" for layer in matches])
                raise AllureValidationError(
                    "\n".join(
                        [
                            f"Warning: Multiple test layers match name '{test_layer_name}'.",
                            "Test case creation was not performed.",
                            match_lines,
                            "Use test_layer_id to disambiguate.",
                        ]
                    )
                )
            return matches[0].id

        return None

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

    async def _get_resolved_custom_fields(self, project_id: int) -> dict[str, ResolvedCustomFieldInfo]:
        """Get or fetch custom field name-to-info mapping for a project."""
        if project_id in self._cf_cache:
            return self._cf_cache[project_id]
        return await self._fetch_resolved_custom_fields(project_id)

    async def refresh_resolved_custom_fields(self, project_id: int) -> dict[str, ResolvedCustomFieldInfo]:
        """Refresh cached custom field name-to-info mapping for a project."""
        if project_id in self._cf_cache:
            del self._cf_cache[project_id]
        return await self._fetch_resolved_custom_fields(project_id)

    async def _fetch_resolved_custom_fields(self, project_id: int) -> dict[str, ResolvedCustomFieldInfo]:
        # Use the client wrapper method for consistent error handling and response processing
        cfs = await self._client.get_custom_fields_with_values(project_id)
        logger.debug("Fetched %d custom fields for project %d", len(cfs), project_id)
        mapping: dict[str, ResolvedCustomFieldInfo] = {}
        for cf_with_values in cfs:
            if cf_with_values.custom_field and cf_with_values.custom_field.custom_field:
                inner_cf = cf_with_values.custom_field.custom_field
                if inner_cf.name and inner_cf.id:
                    values_list: list[str] = []
                    values_map: dict[str, int | None] = {}
                    if cf_with_values.values:
                        for v in cf_with_values.values:
                            if v.name:
                                values_list.append(v.name)
                                values_map[v.name] = v.id

                    project_cf_id = (
                        cf_with_values.custom_field.id
                        if cf_with_values.custom_field and cf_with_values.custom_field.id is not None
                        else inner_cf.id
                    )
                    if project_cf_id is None:
                        continue
                    mapping[inner_cf.name] = {
                        "id": inner_cf.id,
                        "project_cf_id": project_cf_id,
                        "required": bool(cf_with_values.custom_field.required)
                        if cf_with_values.custom_field
                        else False,
                        "single_select": bool(cf_with_values.custom_field.single_select)
                        if cf_with_values.custom_field
                        else None,
                        "values": values_list,
                        "values_map": values_map,
                    }
        self._cf_cache[project_id] = mapping
        return mapping

    def _normalize_custom_field_values_map(
        self,
        values: dict[str, str | list[str]],
        *,
        drop_empty: bool,
    ) -> dict[str, list[str]]:
        normalized: dict[str, list[str]] = {}
        for key, value in values.items():
            if value == "" or value == [] or value == "[]":
                if not drop_empty:
                    normalized[key] = []
                continue

            if isinstance(value, list):
                items = list(value)
            else:
                items = [value]

            items.sort()
            normalized[key] = items

        return normalized

    async def _build_custom_field_dtos(  # noqa: C901
        self, project_id: int, custom_fields: dict[str, str | list[str]]
    ) -> list[CustomFieldValueWithCfDto]:
        """Build DTOs for dedicated custom field endpoint with aggregated validation."""
        resolved_dtos: list[CustomFieldValueWithCfDto] = []
        project_cfs = await self._get_resolved_custom_fields(project_id)

        missing_fields: list[str] = []
        invalid_values: list[str] = []
        required_missing: list[str] = []
        single_select_errors: list[str] = []

        # Check for required fields (on update, we only check if they are being cleared)
        for cf_name, info in project_cfs.items():
            if info["required"] and cf_name in custom_fields:
                val = custom_fields[cf_name]
                if val == "" or val == [] or val == "[]":
                    required_missing.append(cf_name)

        for key, value in custom_fields.items():
            cf_info = project_cfs.get(key)
            if cf_info is None:
                missing_fields.append(key)
                continue

            cf_id = cf_info["project_cf_id"]  # Use project-scoped ID
            allowed_values = cf_info["values"]
            values_map = cf_info["values_map"]
            is_single_select = cf_info["single_select"]

            # Handle clearing logic: "[]" or empty string/list
            if value == "[]" or value == "" or value == []:
                continue

            # Normalize value to list
            input_values = [value] if isinstance(value, str) else value

            if is_single_select is True and len(input_values) > 1:
                single_select_errors.append(f"'{key}': multiple values provided for single-select field")
                continue

            final_values: list[CustomFieldValueDto] = []

            if allowed_values:
                invalid_for_field = False
                for v in input_values:
                    if v not in allowed_values:
                        invalid_values.append(f"'{key}': '{v}' (Allowed: {', '.join(allowed_values)})")
                        invalid_for_field = True
                        continue

                    vid = values_map.get(v)
                    if vid:
                        final_values.append(CustomFieldValueDto(id=vid))
                    else:
                        final_values.append(CustomFieldValueDto(name=v))
                if invalid_for_field:
                    continue
            else:
                for v in input_values:
                    vid = values_map.get(v)
                    if vid:
                        final_values.append(CustomFieldValueDto(id=vid))
                    else:
                        final_values.append(CustomFieldValueDto(name=v))

            for _ in final_values:
                resolved_dtos.append(
                    CustomFieldValueWithCfDto(custom_field=CustomFieldDto(id=cf_id), id=_.id, name=_.name)
                )

        logger.debug("Resolved CF DTOs for update: %s", [d.to_dict() for d in resolved_dtos])

        # Build aggregated error message
        errors: list[str] = []
        if missing_fields:
            errors.append(f"Fields not found: {', '.join(missing_fields)}")
        if invalid_values:
            errors.append(f"Invalid values: {'; '.join(invalid_values)}")
        if required_missing:
            suggestions = []
            for field_name in required_missing:
                field_info = project_cfs.get(field_name)
                if field_info is None:
                    continue
                allowed = field_info["values"]
                if allowed:
                    suggestions.append(f"- {field_name}: {', '.join(allowed)}")
            guidance = ["Required fields cannot be cleared: " + ", ".join(required_missing)]
            guidance.append("Use get_custom_fields to review valid values.")
            if suggestions:
                guidance.append("Allowed values:")
                guidance.extend(suggestions)
            errors.append("\n".join(guidance))
        if single_select_errors:
            errors.append(f"Single-select violations: {'; '.join(single_select_errors)}")

        if errors:
            raise AllureValidationError(
                "\n".join(errors) + "\n\nUsage Hint: Use get_custom_fields to see available fields and values."
            )

        return resolved_dtos

    async def _build_custom_field_dtos_legacy(
        self, project_id: int, custom_fields: dict[str, str | list[str]]
    ) -> list[CustomFieldValueWithCfDto]:
        """Build flat DTOs for mixed update patch endpoint."""
        dtos: list[CustomFieldValueWithCfDto] = []
        structured = await self._build_custom_field_dtos(project_id, custom_fields)

        project_cfs = await self._get_resolved_custom_fields(project_id)

        for s_dto in structured:
            custom_field = s_dto.custom_field
            if custom_field is None or custom_field.id is None:
                continue
            fname = next((k for k, v in project_cfs.items() if v["project_cf_id"] == custom_field.id), None)
            fid = project_cfs[fname]["id"] if fname else custom_field.id

            # Clear indicator for merging logic in update_test_case
            if s_dto.id is None and s_dto.name is None:
                dtos.append(
                    CustomFieldValueWithCfDto(custom_field=CustomFieldDto(id=fid, name=fname), id=None, name=None)
                )
            else:
                dtos.append(
                    CustomFieldValueWithCfDto(
                        custom_field=CustomFieldDto(id=fid, name=fname), id=s_dto.id, name=s_dto.name
                    )
                )
        return dtos

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
        steps: list[dict[str, object]] | None,
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
            step_attachments = cast(list[dict[str, str]], s.get("attachments", []))

            current_parent_id: int | None = None
            last_child_id: int | None = None

            # Action Step (body step)
            if action:
                step_dto = self._build_scenario_step_dto(test_case_id=test_case_id, body=action)
                response = await self._client.create_scenario_step(
                    test_case_id=test_case_id,
                    step=step_dto,
                    after_id=last_step_id,
                    with_expected_result=bool(expected),
                )
                current_parent_id = response.created_step_id
                last_step_id = current_parent_id

                # If expected result logic matches HAR:
                # 1. We called create with withExpectedResult=True
                # 2. We get response with scenario mapping
                # 3. We find expectedResultId for our step
                # 4. We add the expected result text as a child of that expectedResultId
                if (
                    expected
                    and current_parent_id is not None
                    and response.scenario
                    and response.scenario.scenario_steps
                ):
                    # Find our step in the scenario to get expectedResultId
                    step_info = response.scenario.scenario_steps.get(str(current_parent_id))
                    if step_info and step_info.expected_result_id:
                        await self._client.create_scenario_step(
                            test_case_id=test_case_id,
                            step=self._build_scenario_step_dto(
                                test_case_id=test_case_id,
                                body=expected,
                                parent_id=step_info.expected_result_id,
                            ),
                            after_id=None,
                        )

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
            expected_result = getattr(instance, "expected_result", None)
            step_dto = self._build_scenario_step_dto(test_case_id=test_case_id, body=instance.body, parent_id=parent_id)
            resp = await self._client.create_scenario_step(
                test_case_id=test_case_id,
                step=step_dto,
                after_id=after_id,
                with_expected_result=bool(expected_result),
            )
            created_id = resp.created_step_id

            if expected_result and created_id is not None and resp.scenario and resp.scenario.scenario_steps:
                step_info = resp.scenario.scenario_steps.get(str(created_id))
                if step_info and step_info.expected_result_id:
                    await self._client.create_scenario_step(
                        test_case_id=test_case_id,
                        step=self._build_scenario_step_dto(
                            test_case_id=test_case_id,
                            body=expected_result,
                            parent_id=step_info.expected_result_id,
                        ),
                        after_id=None,
                    )

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

        elif isinstance(instance, SharedStepStepDto):
            step_dto = self._build_scenario_step_dto(
                test_case_id=test_case_id, shared_step_id=instance.shared_step_id, parent_id=parent_id
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
