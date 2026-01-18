from dataclasses import dataclass

from src.client import AllureClient, PageTestCaseDto, TestCaseDto
from src.client.exceptions import AllureValidationError


@dataclass
class TestCaseListResult:
    """Result of listing test cases."""

    items: list[TestCaseDto]
    total: int
    page: int
    size: int
    total_pages: int


class SearchService:
    """Service for search and discovery operations."""

    def __init__(self, client: AllureClient) -> None:
        self._client = client

    async def list_test_cases(
        self,
        project_id: int,
        page: int = 0,
        size: int = 20,
        name_filter: str | None = None,
        tags: list[str] | None = None,
        status: str | None = None,
    ) -> TestCaseListResult:
        """List test cases in a project with pagination.

        Args:
            project_id: Project ID.
            page: Zero-based page index.
            size: Page size.
            name_filter: Optional search query for test case name.
            tags: Optional list of tags to filter.
            status: Optional test case status filter.

        Returns:
            TestCaseListResult with items and pagination metadata.
        """
        self._validate_project_id(project_id)
        self._validate_pagination(page, size)

        response = await self._client.list_test_cases(
            project_id=project_id,
            page=page,
            size=size,
            search=name_filter,
            tags=tags,
            status=status,
        )

        return self._build_result(response)

    def _build_result(self, response: PageTestCaseDto) -> TestCaseListResult:
        items = response.content or []
        return TestCaseListResult(
            items=items,
            total=response.total_elements or 0,
            page=response.number or 0,
            size=response.size or 0,
            total_pages=response.total_pages or 0,
        )

    def _validate_project_id(self, project_id: int) -> None:
        if not isinstance(project_id, int):
            raise AllureValidationError(f"Project ID must be an integer, got {type(project_id).__name__}")
        if project_id <= 0:
            raise AllureValidationError("Project ID is required and must be positive")

    def _validate_pagination(self, page: int, size: int) -> None:
        if not isinstance(page, int) or page < 0:
            raise AllureValidationError("Page must be a non-negative integer")
        if not isinstance(size, int) or size <= 0:
            raise AllureValidationError("Size must be a positive integer")
        if size > 100:
            raise AllureValidationError("Size must be 100 or less")
