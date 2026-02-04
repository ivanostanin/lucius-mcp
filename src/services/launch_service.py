"""Service for managing Launches in Allure TestOps."""

from collections.abc import Sequence
from dataclasses import dataclass

from pydantic import ValidationError as PydanticValidationError

from src.client import AllureClient, FindAll29200Response, LaunchCreateDto, LaunchDto
from src.client.exceptions import AllureValidationError
from src.client.generated.models.aql_validate_response_dto import AqlValidateResponseDto
from src.client.generated.models.external_link_dto import ExternalLinkDto
from src.client.generated.models.issue_dto import IssueDto
from src.client.generated.models.launch_preview_dto import LaunchPreviewDto
from src.client.generated.models.launch_tag_dto import LaunchTagDto
from src.client.generated.models.page_launch_dto import PageLaunchDto
from src.client.generated.models.page_launch_preview_dto import PageLaunchPreviewDto
from src.utils.schema_hint import generate_schema_hint

MAX_NAME_LENGTH = 255
MAX_TAG_LENGTH = 255

type LaunchListItem = LaunchDto | LaunchPreviewDto


@dataclass
class LaunchListResult:
    """Result of listing launches."""

    items: Sequence[LaunchListItem]
    total: int
    page: int
    size: int
    total_pages: int


class LaunchService:
    """Service for launch create/list operations."""

    def __init__(self, client: AllureClient) -> None:
        self._client = client
        self._project_id = client.get_project()

    async def create_launch(
        self,
        name: str,
        autoclose: bool | None = None,
        external: bool | None = None,
        issues: list[dict[str, object]] | None = None,
        links: list[dict[str, str]] | None = None,
        tags: list[str] | None = None,
    ) -> LaunchDto:
        """Create a new launch.

        Args:
            name: Launch name.
            autoclose: Whether the launch auto-closes.
            external: Whether the launch is external.
            issues: Optional list of issue dictionaries.
            links: Optional list of external link dictionaries.
            tags: Optional list of launch tags.

        Returns:
            The created launch.
        """
        self._validate_project_id(self._project_id)
        self._validate_name(name)
        self._validate_tags(tags)
        self._validate_links(links)
        self._validate_issues(issues)

        try:
            issue_dtos = self._build_issue_dtos(issues)
            link_dtos = self._build_link_dtos(links)
            tag_dtos = self._build_tag_dtos(tags)

            data = LaunchCreateDto(
                name=name,
                project_id=self._project_id,
                autoclose=autoclose,
                external=external,
                issues=issue_dtos,
                links=link_dtos,
                tags=tag_dtos,
            )
        except PydanticValidationError as e:
            hint = generate_schema_hint(LaunchCreateDto)
            raise AllureValidationError(f"Invalid launch data: {e}", suggestions=[hint]) from e

        return await self._client.create_launch(data)

    async def list_launches(
        self,
        page: int = 0,
        size: int = 20,
        search: str | None = None,
        filter_id: int | None = None,
        sort: list[str] | None = None,
    ) -> LaunchListResult:
        """List launches for the configured project.

        Args:
            page: Zero-based page index.
            size: Page size.
            search: Optional name search.
            filter_id: Optional filter ID.
            sort: Optional sort criteria.

        Returns:
            LaunchListResult with items and pagination metadata.
        """
        self._validate_project_id(self._project_id)
        self._validate_pagination(page, size)

        response = await self._client.list_launches(
            project_id=self._project_id,
            page=page,
            size=size,
            search=search,
            filter_id=filter_id,
            sort=sort,
        )

        page_data = self._extract_page(response)

        items = page_data.content or []

        return LaunchListResult(
            items=items,
            total=page_data.total_elements or len(items),
            page=page_data.number or page,
            size=page_data.size or size,
            total_pages=page_data.total_pages or 1,
        )

    async def search_launches_aql(
        self,
        rql: str,
        page: int = 0,
        size: int = 20,
        sort: list[str] | None = None,
    ) -> LaunchListResult:
        """Search launches using raw AQL.

        Args:
            rql: Raw AQL query string.
            page: Zero-based page index.
            size: Page size (max 100).
            sort: Optional sort criteria.

        Returns:
            LaunchListResult with items and pagination metadata.
        """
        self._validate_project_id(self._project_id)
        if not isinstance(rql, str) or not rql.strip():
            raise AllureValidationError("AQL query must be a non-empty string")
        self._validate_pagination(page, size)

        response = await self._client.search_launches_aql(
            project_id=self._project_id,
            rql=rql,
            page=page,
            size=size,
            sort=sort,
        )

        items = response.content or []

        return LaunchListResult(
            items=items,
            total=response.total_elements or len(items),
            page=response.number or page,
            size=response.size or size,
            total_pages=response.total_pages or 1,
        )

    async def get_launch(self, launch_id: int) -> LaunchDto:
        """Retrieve a specific launch by its ID.

        Args:
            launch_id: The unique ID of the launch.

        Returns:
            The launch data.
        """
        self._validate_project_id(self._project_id)
        self._validate_launch_id(launch_id)

        return await self._client.get_launch(launch_id)

    async def validate_launch_query(self, rql: str) -> tuple[bool, int | None]:
        """Validate an AQL query for launches."""
        if not isinstance(rql, str) or not rql.strip():
            raise AllureValidationError("AQL query must be a non-empty string")

        response = await self._client.validate_launch_query(project_id=self._project_id, rql=rql)
        if not isinstance(response, AqlValidateResponseDto):
            raise AllureValidationError("Unexpected validation response from API")
        return (response.valid or False, response.count)

    @staticmethod
    def _extract_page(response: FindAll29200Response) -> PageLaunchDto | PageLaunchPreviewDto:
        actual = response.actual_instance
        if isinstance(actual, (PageLaunchDto, PageLaunchPreviewDto)):
            return actual
        raise AllureValidationError("Unexpected launch list response from API")

    def _validate_project_id(self, project_id: int | None) -> None:
        if not isinstance(project_id, int):
            raise AllureValidationError(f"Project ID must be an integer, got {type(project_id).__name__}")
        if project_id <= 0:
            raise AllureValidationError("Project ID is required and must be positive")

    @staticmethod
    def _validate_pagination(page: int, size: int) -> None:
        if not isinstance(page, int) or page < 0:
            raise AllureValidationError("Page must be a non-negative integer")
        if not isinstance(size, int) or size <= 0 or size > 100:
            raise AllureValidationError("Size must be between 1 and 100")

    @staticmethod
    def _validate_launch_id(launch_id: int) -> None:
        if not isinstance(launch_id, int):
            raise AllureValidationError(f"Launch ID must be an integer, got {type(launch_id).__name__}")
        if launch_id <= 0:
            raise AllureValidationError("Launch ID must be a positive integer")

    @staticmethod
    def _validate_name(name: str) -> None:
        if not isinstance(name, str):
            raise AllureValidationError(f"Launch name must be a string, got {type(name).__name__}")
        if not name.strip():
            raise AllureValidationError("Launch name is required")
        if len(name) > MAX_NAME_LENGTH:
            raise AllureValidationError(f"Launch name must be {MAX_NAME_LENGTH} characters or less")

    @staticmethod
    def _validate_tags(tags: list[str] | None) -> None:
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

    @staticmethod
    def _validate_links(links: list[dict[str, str]] | None) -> None:
        if links is None:
            return
        if not isinstance(links, list):
            raise AllureValidationError(f"Links must be a list, got {type(links).__name__}")
        for i, link in enumerate(links):
            if not isinstance(link, dict):
                raise AllureValidationError(f"Link at index {i} must be a dictionary")
            if not link:
                raise AllureValidationError(f"Link at index {i} cannot be empty")
            url = link.get("url")
            if url is not None and not isinstance(url, str):
                raise AllureValidationError(f"Link at index {i} 'url' must be a string")
            name = link.get("name")
            if name is not None and not isinstance(name, str):
                raise AllureValidationError(f"Link at index {i} 'name' must be a string")
            link_type = link.get("type")
            if link_type is not None and not isinstance(link_type, str):
                raise AllureValidationError(f"Link at index {i} 'type' must be a string")

    @staticmethod
    def _validate_issues(issues: list[dict[str, object]] | None) -> None:
        if issues is None:
            return
        if not isinstance(issues, list):
            raise AllureValidationError(f"Issues must be a list, got {type(issues).__name__}")
        for i, issue in enumerate(issues):
            if not isinstance(issue, dict):
                raise AllureValidationError(f"Issue at index {i} must be a dictionary")
            if not issue:
                raise AllureValidationError(f"Issue at index {i} cannot be empty")

    @staticmethod
    def _build_tag_dtos(tags: list[str] | None) -> list[LaunchTagDto] | None:
        if not tags:
            return None
        return [LaunchTagDto(name=tag) for tag in tags]

    @staticmethod
    def _build_link_dtos(links: list[dict[str, str]] | None) -> list[ExternalLinkDto] | None:
        if not links:
            return None
        return [ExternalLinkDto(**link) for link in links]

    @staticmethod
    def _build_issue_dtos(issues: list[dict[str, object]] | None) -> list[IssueDto] | None:
        if not issues:
            return None
        return [IssueDto(**issue) for issue in issues]
