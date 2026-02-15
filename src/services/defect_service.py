"""Service for managing Defects and Defect Matchers in Allure TestOps."""

import logging
from dataclasses import dataclass

from src.client import AllureClient
from src.client.exceptions import AllureNotFoundError, AllureValidationError
from src.client.generated.api import DefectControllerApi, DefectMatcherControllerApi
from src.client.generated.exceptions import ApiException
from src.client.generated.models.defect_count_row_dto import DefectCountRowDto
from src.client.generated.models.defect_create_dto import DefectCreateDto
from src.client.generated.models.defect_issue_link_dto import DefectIssueLinkDto
from src.client.generated.models.defect_matcher_create_dto import (
    DefectMatcherCreateDto,
)
from src.client.generated.models.defect_matcher_dto import DefectMatcherDto
from src.client.generated.models.defect_matcher_patch_dto import DefectMatcherPatchDto
from src.client.generated.models.defect_overview_dto import DefectOverviewDto
from src.client.generated.models.defect_patch_dto import DefectPatchDto
from src.client.generated.models.test_case_row_dto import TestCaseRowDto
from src.services.integration_service import IntegrationService
from src.services.test_case_service import TestCaseService

logger = logging.getLogger(__name__)


@dataclass
class DefectTestCaseLinkResult:
    """Result of linking a defect to a test case via issue mapping."""

    defect_id: int
    test_case_id: int
    issue_key: str
    integration_id: int
    already_linked: bool


@dataclass
class DefectTestCaseListResult:
    """Paginated list of test cases linked to a defect."""

    items: list[TestCaseRowDto]
    total: int
    page: int
    size: int
    total_pages: int


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

    async def link_defect_to_test_case(
        self,
        defect_id: int,
        test_case_id: int,
        issue_key: str | None = None,
        integration_id: int | None = None,
        integration_name: str | None = None,
    ) -> DefectTestCaseLinkResult:
        """Link defect and test case through a shared issue mapping.

        Args:
            defect_id: Defect ID.
            test_case_id: Test case ID.
            issue_key: Issue key to map (for example, PROJ-123). If omitted,
                an existing issue mapping from the defect is reused.
            integration_id: Optional explicit integration ID.
            integration_name: Optional explicit integration name.

        Returns:
            DefectTestCaseLinkResult with mapping details and idempotency state.

        Raises:
            AllureValidationError: For invalid input or missing issue mapping.
            AllureNotFoundError: If defect/test case is not found.
        """
        self._validate_positive_id(defect_id, "Defect ID")
        self._validate_positive_id(test_case_id, "Test case ID")
        if integration_id is not None and integration_name is not None:
            raise AllureValidationError("Cannot specify both integration_id and integration_name. Use only one.")

        issue_name: str
        target_integration_id: int

        if issue_key is not None:
            issue_name = self._normalize_issue_key(issue_key)
            integration_service = IntegrationService(self._client)
            target_integration_id = await integration_service.resolve_integration_for_issues(
                integration_id=integration_id,
                integration_name=integration_name,
            )
        else:
            defect = await self.get_defect(defect_id)
            if defect.issue is None or defect.issue.name is None:
                raise AllureValidationError(
                    "Issue mapping is required. Provide issue_key or link an issue to the defect first."
                )
            issue_name = self._normalize_issue_key(defect.issue.name)

            if defect.issue.integration_id is not None:
                target_integration_id = defect.issue.integration_id
            else:
                integration_service = IntegrationService(self._client)
                target_integration_id = await integration_service.resolve_integration_for_issues(
                    integration_id=integration_id,
                    integration_name=integration_name,
                )

        try:
            await self._defect_api.link_issue(
                id=defect_id,
                defect_issue_link_dto=DefectIssueLinkDto(
                    integration_id=target_integration_id,
                    name=issue_name,
                ),
            )
        except ApiException as exc:
            if exc.status == 404:
                raise AllureNotFoundError(f"Defect {defect_id} not found") from exc
            if exc.status == 409:
                if not await self._is_defect_issue_mapping_match(
                    defect_id=defect_id,
                    issue_key=issue_name,
                    integration_id=target_integration_id,
                ):
                    raise AllureValidationError(
                        "Defect issue mapping conflict detected. "
                        "The defect is already linked to a different issue mapping."
                    ) from exc
                logger.info("Issue %s already linked to Defect %s", issue_name, defect_id)
            else:
                raise

        test_case_service = TestCaseService(self._client)
        current_case = await test_case_service.get_test_case(test_case_id)
        already_linked = any(
            issue.name
            and self._normalize_issue_key(issue.name) == issue_name
            and issue.integration_id == target_integration_id
            for issue in (current_case.issues or [])
        )

        if not already_linked:
            await test_case_service.add_issues_to_test_case(
                test_case_id,
                [issue_name],
                integration_id=target_integration_id,
            )

        return DefectTestCaseLinkResult(
            defect_id=defect_id,
            test_case_id=test_case_id,
            issue_key=issue_name,
            integration_id=target_integration_id,
            already_linked=already_linked,
        )

    async def list_defect_test_cases(
        self,
        defect_id: int,
        page: int = 0,
        size: int = 20,
    ) -> DefectTestCaseListResult:
        """List test cases linked to a defect.

        Args:
            defect_id: Defect ID.
            page: Zero-based page index.
            size: Page size (1..100).

        Returns:
            DefectTestCaseListResult with pagination metadata.
        """
        self._validate_positive_id(defect_id, "Defect ID")
        self._validate_pagination(page=page, size=size)

        try:
            response = await self._defect_api.get_test_cases2(
                id=defect_id,
                page=page,
                size=size,
            )
        except ApiException as exc:
            if exc.status == 404:
                raise AllureNotFoundError(f"Defect {defect_id} not found") from exc
            raise

        return DefectTestCaseListResult(
            items=list(response.content) if response.content else [],
            total=response.total_elements or 0,
            page=response.number or 0,
            size=response.size or 0,
            total_pages=response.total_pages or 0,
        )

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

    def _validate_positive_id(self, value: int, field_name: str) -> None:
        """Validate that an ID field is a positive integer."""
        if not isinstance(value, int) or value <= 0:
            raise AllureValidationError(f"{field_name} must be a positive integer")

    def _validate_pagination(self, page: int, size: int) -> None:
        """Validate pagination inputs."""
        if not isinstance(page, int) or page < 0:
            raise AllureValidationError("Page must be a non-negative integer")
        if not isinstance(size, int) or size <= 0:
            raise AllureValidationError("Size must be a positive integer")
        if size > 100:
            raise AllureValidationError("Size must be 100 or less")

    def _normalize_issue_key(self, issue_key: str) -> str:
        """Normalize issue key for consistent idempotent matching."""
        normalized = issue_key.strip().upper()
        if not normalized:
            raise AllureValidationError("issue_key must be a non-empty string")
        return normalized

    async def _is_defect_issue_mapping_match(
        self,
        defect_id: int,
        issue_key: str,
        integration_id: int,
    ) -> bool:
        """Check whether defect already has the exact target issue mapping."""
        defect = await self.get_defect(defect_id)
        if defect.issue is None or defect.issue.name is None:
            return False

        if self._normalize_issue_key(defect.issue.name) != issue_key:
            return False

        return defect.issue.integration_id == integration_id
