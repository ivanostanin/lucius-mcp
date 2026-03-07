import logging

from src.client import AllureClient
from src.client.exceptions import AllureNotFoundError, AllureValidationError

logger = logging.getLogger(__name__)


class CustomFieldService:
    """Service for project-level custom field cleanup operations."""

    def __init__(self, client: AllureClient) -> None:
        self._client = client
        self._project_id = client.get_project()

    async def cleanup_unused(self, page_size: int = 100) -> int:
        """Remove custom fields that are unused by any test case in this project."""
        if not isinstance(self._project_id, int) or self._project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")
        if not isinstance(page_size, int) or page_size <= 0:
            raise AllureValidationError("page_size must be a positive integer")

        project_field_ids = await self._list_project_field_ids(page_size=page_size)

        deleted_count = 0
        for field_id in project_field_ids:
            if await self._is_field_in_use(field_id):
                continue

            if await self._remove_field_from_project(field_id):
                deleted_count += 1

        return deleted_count

    async def _list_project_field_ids(self, page_size: int) -> list[int]:
        field_ids: list[int] = []
        page = 0

        while True:
            fields = await self._client.list_project_custom_fields(
                project_id=self._project_id,
                page=page,
                size=page_size,
            )
            if not fields:
                break

            for field in fields:
                if field.custom_field is None or field.custom_field.id is None:
                    continue
                field_ids.append(field.custom_field.id)

            if len(fields) < page_size:
                break
            page += 1

        return sorted(set(field_ids))

    async def _is_field_in_use(self, field_id: int) -> bool:
        usage_stats = await self._client.count_test_cases_in_projects(
            project_ids=[self._project_id],
            custom_field_id=field_id,
            deleted=False,
        )

        for stat in usage_stats:
            if stat.id == self._project_id:
                return (stat.test_case_count or 0) > 0
        return False

    async def _remove_field_from_project(self, field_id: int) -> bool:
        try:
            await self._client.remove_custom_field_from_project(
                custom_field_id=field_id,
                project_id=self._project_id,
            )
            return True
        except AllureNotFoundError:
            logger.debug("Custom field %s was already removed from project %s.", field_id, self._project_id)
            return False
