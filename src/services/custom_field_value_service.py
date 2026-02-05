"""Service for managing Custom Field Values in Allure TestOps."""

import logging

from pydantic import ValidationError as PydanticValidationError

from src.client import AllureClient
from src.client.exceptions import AllureAPIError, AllureNotFoundError, AllureValidationError
from src.client.generated.models.custom_field_value_project_create_dto import CustomFieldValueProjectCreateDto
from src.client.generated.models.custom_field_value_project_patch_dto import CustomFieldValueProjectPatchDto
from src.client.generated.models.custom_field_value_with_cf_dto import CustomFieldValueWithCfDto
from src.client.generated.models.id_only_dto import IdOnlyDto
from src.client.generated.models.page_custom_field_value_with_tc_count_dto import PageCustomFieldValueWithTcCountDto
from src.services.test_case_service import ResolvedCustomFieldInfo, TestCaseService
from src.utils.schema_hint import generate_schema_hint

logger = logging.getLogger(__name__)

MAX_NAME_LENGTH = 255


class CustomFieldValueService:
    """Service for CRUD operations on custom field values."""

    def __init__(self, client: AllureClient) -> None:
        self._client = client
        self._project_id = client.get_project()
        self._test_case_service = TestCaseService(client=client)

    async def list_custom_field_values(
        self,
        *,
        project_id: int | None = None,
        custom_field_id: int | None = None,
        custom_field_name: str | None = None,
        query: str | None = None,
        var_global: bool | None = None,
        test_case_search: str | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: list[str] | None = None,
    ) -> PageCustomFieldValueWithTcCountDto:
        """List custom field values for a project-scoped custom field."""
        resolved_project_id = self._resolve_project_id(project_id)
        resolved_custom_field_id = await self._resolve_custom_field_id(
            resolved_project_id,
            custom_field_id=custom_field_id,
            custom_field_name=custom_field_name,
        )

        return await self._client.list_custom_field_values(
            project_id=resolved_project_id,
            custom_field_id=resolved_custom_field_id,
            query=query,
            var_global=var_global,
            test_case_search=test_case_search,
            page=page,
            size=size,
            sort=sort,
        )

    async def create_custom_field_value(
        self,
        *,
        project_id: int | None = None,
        custom_field_id: int | None = None,
        custom_field_name: str | None = None,
        name: str,
    ) -> CustomFieldValueWithCfDto:
        """Create a new custom field value for the given field."""
        resolved_project_id = self._resolve_project_id(project_id)
        resolved_custom_field_id = await self._resolve_custom_field_id(
            resolved_project_id,
            custom_field_id=custom_field_id,
            custom_field_name=custom_field_name,
        )
        self._validate_name(name)

        try:
            dto = CustomFieldValueProjectCreateDto(
                custom_field=IdOnlyDto(id=resolved_custom_field_id),
                name=name,
                project_id=resolved_project_id,
            )
        except PydanticValidationError as exc:
            hint = generate_schema_hint(CustomFieldValueProjectCreateDto)
            raise AllureValidationError(f"Invalid custom field value data: {exc}", suggestions=[hint]) from exc

        try:
            return await self._client.create_custom_field_value(resolved_project_id, dto)
        except AllureValidationError as exc:
            if exc.status_code in (400, 409, 422):
                raise AllureValidationError(
                    "Custom field value already exists or is invalid.",
                    status_code=exc.status_code,
                    response_body=exc.response_body,
                    suggestions=[
                        "Use a unique name for the custom field value",
                        "List existing values with list_custom_field_values",
                    ],
                ) from exc
            raise
        except AllureAPIError as exc:
            if exc.status_code in (400, 409, 422):
                raise AllureValidationError(
                    "Custom field value already exists or is invalid.",
                    status_code=exc.status_code,
                    response_body=exc.response_body,
                    suggestions=[
                        "Use a unique name for the custom field value",
                        "List existing values with list_custom_field_values",
                    ],
                ) from exc
            raise

    async def update_custom_field_value(
        self,
        *,
        project_id: int | None = None,
        cfv_id: int,
        custom_field_id: int | None = None,
        custom_field_name: str | None = None,
        name: str | None = None,
    ) -> None:
        """Update a custom field value (rename)."""
        resolved_project_id = self._resolve_project_id(project_id)
        await self._resolve_custom_field_id(
            resolved_project_id,
            custom_field_id=custom_field_id,
            custom_field_name=custom_field_name,
        )
        self._validate_cfv_id(cfv_id)
        if name is None:
            raise AllureValidationError("Name is required for update")
        self._validate_name(name)

        try:
            dto = CustomFieldValueProjectPatchDto(name=name)
        except PydanticValidationError as exc:
            hint = generate_schema_hint(CustomFieldValueProjectPatchDto)
            raise AllureValidationError(f"Invalid custom field value patch data: {exc}", suggestions=[hint]) from exc

        await self._client.update_custom_field_value(resolved_project_id, cfv_id, dto)

    async def delete_custom_field_value(
        self,
        *,
        project_id: int | None = None,
        cfv_id: int,
        custom_field_id: int | None = None,
        custom_field_name: str | None = None,
    ) -> bool:
        """Delete a custom field value (idempotent).

        Returns True if deletion occurred, False if the value was already removed.
        """
        resolved_project_id = self._resolve_project_id(project_id)
        await self._resolve_custom_field_id(
            resolved_project_id,
            custom_field_id=custom_field_id,
            custom_field_name=custom_field_name,
        )
        self._validate_cfv_id(cfv_id)

        try:
            await self._client.delete_custom_field_value(resolved_project_id, cfv_id)
            return True
        except AllureNotFoundError:
            logger.debug("Custom field value %s already removed", cfv_id)
            return False

    def _resolve_project_id(self, project_id: int | None) -> int:
        resolved_project_id = project_id if project_id is not None else self._project_id
        if not isinstance(resolved_project_id, int) or resolved_project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")
        return resolved_project_id

    async def _resolve_custom_field_id(
        self,
        project_id: int,
        *,
        custom_field_id: int | None,
        custom_field_name: str | None,
    ) -> int:
        if custom_field_id is not None:
            if not isinstance(custom_field_id, int) or custom_field_id == 0:
                raise AllureValidationError("Custom Field ID must be a non-zero integer")
            return custom_field_id

        if custom_field_name is None or not custom_field_name.strip():
            raise AllureValidationError("Custom field name is required when custom_field_id is not provided")

        mapping = await self._get_resolved_custom_fields(project_id)
        normalized_name = custom_field_name.strip()
        info = mapping.get(normalized_name)
        if info is None:
            suggestions = sorted(mapping.keys())
            raise AllureValidationError(
                f"Custom field '{normalized_name}' not found.",
                suggestions=suggestions if suggestions else ["Use get_custom_fields to list available fields."],
            )
        return info["project_cf_id"]

    async def _get_resolved_custom_fields(self, project_id: int) -> dict[str, ResolvedCustomFieldInfo]:
        return await self._test_case_service._get_resolved_custom_fields(project_id)

    def _validate_name(self, name: str) -> None:
        if not name or not name.strip():
            raise AllureValidationError("Name is required")
        if len(name) > MAX_NAME_LENGTH:
            raise AllureValidationError(f"Name too long (max {MAX_NAME_LENGTH})")

    def _validate_cfv_id(self, cfv_id: int) -> None:
        if not isinstance(cfv_id, int) or cfv_id <= 0:
            raise AllureValidationError("Custom Field Value ID must be a positive integer")
