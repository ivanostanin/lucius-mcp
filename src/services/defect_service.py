"""Service for managing Defects and Defect Matchers in Allure TestOps."""

import logging

from src.client import AllureClient
from src.client.exceptions import AllureNotFoundError, AllureValidationError
from src.client.generated.api import DefectControllerApi, DefectMatcherControllerApi
from src.client.generated.exceptions import ApiException
from src.client.generated.models.defect_count_row_dto import DefectCountRowDto
from src.client.generated.models.defect_create_dto import DefectCreateDto
from src.client.generated.models.defect_matcher_create_dto import (
    DefectMatcherCreateDto,
)
from src.client.generated.models.defect_matcher_dto import DefectMatcherDto
from src.client.generated.models.defect_matcher_patch_dto import DefectMatcherPatchDto
from src.client.generated.models.defect_overview_dto import DefectOverviewDto
from src.client.generated.models.defect_patch_dto import DefectPatchDto

logger = logging.getLogger(__name__)


class DefectService:
    """Service for managing Defects and Defect Matchers in Allure TestOps.

    Follows the Thin Tool / Fat Service pattern: all business logic
    for defect and defect-matcher CRUD lives here, while MCP tools
    remain thin wrappers.
    """

    def __init__(self, client: AllureClient):
        """Initialize the service.

        Args:
            client: Authenticated AllureClient.
        """
        self._client = client
        self._project_id = client.get_project()

    @property
    def _defect_api(self) -> DefectControllerApi:
        return DefectControllerApi(self._client.api_client)

    @property
    def _matcher_api(self) -> DefectMatcherControllerApi:
        return DefectMatcherControllerApi(self._client.api_client)

    # ── Defect CRUD ──────────────────────────────────────────────

    async def create_defect(
        self,
        name: str,
        description: str | None = None,
    ) -> DefectOverviewDto:
        """Create a new defect.

        Args:
            name: Defect name (required).
            description: Defect description (optional).

        Returns:
            Created DefectOverviewDto.

        Raises:
            AllureValidationError: If name is empty.
        """
        if not name or not name.strip():
            raise AllureValidationError("Defect name is required")

        dto = DefectCreateDto(
            name=name,
            project_id=self._project_id,
            description=description,
        )
        result: DefectOverviewDto = await self._defect_api.create45(defect_create_dto=dto)
        return result

    async def get_defect(self, defect_id: int) -> DefectOverviewDto:
        """Get defect details by ID.

        Args:
            defect_id: ID of the defect.

        Returns:
            DefectOverviewDto details.

        Raises:
            AllureNotFoundError: If defect not found.
        """
        try:
            result: DefectOverviewDto = await self._defect_api.find_by_id1(id=defect_id)
            return result
        except ApiException as exc:
            if exc.status == 404:
                raise AllureNotFoundError(f"Defect {defect_id} not found") from exc
            raise

    async def update_defect(
        self,
        defect_id: int,
        name: str | None = None,
        description: str | None = None,
        closed: bool | None = None,
    ) -> DefectOverviewDto:
        """Update a defect.

        Args:
            defect_id: Defect to update.
            name: New name (optional).
            description: New description (optional).
            closed: New status (True for closed, False for open).

        Returns:
            Updated DefectOverviewDto.

        Raises:
            AllureNotFoundError: If the defect does not exist.
            AllureValidationError: If no fields are provided.
        """
        if name is None and description is None and closed is None:
            raise AllureValidationError("At least one field (name, description, closed) must be provided")

        patch = DefectPatchDto(name=name, description=description, closed=closed)
        try:
            result: DefectOverviewDto = await self._defect_api.patch42(
                id=defect_id,
                defect_patch_dto=patch,
            )
            return result
        except ApiException as exc:
            if exc.status == 404:
                raise AllureNotFoundError(f"Defect {defect_id} not found") from exc
            raise
        return result

    async def delete_defect(self, defect_id: int) -> None:
        """Delete a defect.

        Args:
            defect_id: The defect to delete.

        Raises:
            AllureNotFoundError: If the defect does not exist.
        """
        try:
            await self._defect_api.delete37(id=defect_id)
        except ApiException as exc:
            if exc.status == 404:
                logger.warning(f"Defect {defect_id} not found during deletion (idempotent skip)")
                return
            raise

    async def list_defects(self) -> list[DefectCountRowDto]:
        """List all defects in the configured project.

        Returns:
            List of DefectCountRowDto objects.
        """
        page = await self._defect_api.find_all_by_project_id(
            project_id=self._project_id,
            page=0,
            size=100,
        )
        return list(page.content) if page.content else []

    # ── Defect Matcher CRUD ──────────────────────────────────────

    async def create_defect_matcher(
        self,
        defect_id: int,
        name: str,
        message_regex: str | None = None,
        trace_regex: str | None = None,
    ) -> DefectMatcherDto:
        """Create a defect matcher (automation rule).

        Args:
            defect_id: Parent defect for this matcher.
            name: Human-readable matcher name.
            message_regex: Regex to match against error messages.
            trace_regex: Regex to match against stack traces.

        Returns:
            Created DefectMatcherDto.

        Raises:
            AllureValidationError: If neither message_regex nor trace_regex is provided.
        """
        if not name or not name.strip():
            raise AllureValidationError("Defect matcher name is required")

        if not message_regex and not trace_regex:
            raise AllureValidationError("At least one of message_regex or trace_regex must be provided")

        dto = DefectMatcherCreateDto(
            defect_id=defect_id,
            name=name,
            message_regex=message_regex,
            trace_regex=trace_regex,
        )
        result: DefectMatcherDto = await self._matcher_api.create46(
            defect_matcher_create_dto=dto,
        )
        return result

    async def update_defect_matcher(
        self,
        matcher_id: int,
        name: str | None = None,
        message_regex: str | None = None,
        trace_regex: str | None = None,
    ) -> DefectMatcherDto:
        """Update a defect matcher.

        Args:
            matcher_id: The matcher to update.
            name: New name (optional).
            message_regex: New message regex (optional).
            trace_regex: New trace regex (optional).

        Returns:
            Updated DefectMatcherDto.

        Raises:
            AllureNotFoundError: If the matcher does not exist.
            AllureValidationError: If no fields are provided.
        """
        if name is None and message_regex is None and trace_regex is None:
            raise AllureValidationError("At least one field (name, message_regex, trace_regex) must be provided")

        patch = DefectMatcherPatchDto(
            name=name,
            message_regex=message_regex,
            trace_regex=trace_regex,
        )
        try:
            result: DefectMatcherDto = await self._matcher_api.patch43(
                id=matcher_id,
                defect_matcher_patch_dto=patch,
            )
        except ApiException as exc:
            if exc.status == 404:
                raise AllureNotFoundError(f"Defect matcher {matcher_id} not found") from exc
            raise
        return result

    async def delete_defect_matcher(self, matcher_id: int) -> None:
        """Delete a defect matcher.

        Args:
            matcher_id: The matcher to delete.

        Raises:
            AllureNotFoundError: If the matcher does not exist.
        """
        try:
            await self._matcher_api.delete38(id=matcher_id)
        except ApiException as exc:
            if exc.status == 404:
                logger.warning(f"Defect matcher {matcher_id} not found during deletion (idempotent skip)")
                return
            raise

    async def list_defect_matchers(self, defect_id: int) -> list[DefectMatcherDto]:
        """List all matchers for a given defect.

        Args:
            defect_id: The parent defect ID.

        Returns:
            List of DefectMatcherDto objects.
        """
        page = await self._defect_api.get_matchers(
            id=defect_id,
            page=0,
            size=100,
        )
        return list(page.content) if page.content else []
