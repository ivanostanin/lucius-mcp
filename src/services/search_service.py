import re
from dataclasses import dataclass

from src.client import AllureClient, PageTestCaseDto, TestCaseDto, TestCaseScenarioV2Dto
from src.client.exceptions import AllureNotFoundError, AllureValidationError, TestCaseNotFoundError


@dataclass
class TestCaseListResult:
    """Result of listing test cases."""

    items: list[TestCaseDto]
    total: int
    page: int
    size: int
    total_pages: int


@dataclass
class TestCaseDetails:
    """Full test case details including scenario."""

    test_case: TestCaseDto
    scenario: TestCaseScenarioV2Dto | None


@dataclass
class ParsedQuery:
    """Parsed search query components."""

    name_query: str | None
    tags: list[str]


class SearchQueryParser:
    """Parses search queries into structured components."""

    TAG_PATTERN = re.compile(r"tag:(\S+)", re.IGNORECASE)

    @classmethod
    def parse(cls, query: str) -> ParsedQuery:
        """Parse a search query into name and tag components.

        Args:
            query: Raw search query string.

        Returns:
            ParsedQuery with separated name and tag filters.

        Examples:
            >>> SearchQueryParser.parse("login flow")
            ParsedQuery(name_query="login flow", tags=[])

            >>> SearchQueryParser.parse("tag:smoke tag:auth")
            ParsedQuery(name_query=None, tags=["smoke", "auth"])

            >>> SearchQueryParser.parse("login tag:auth")
            ParsedQuery(name_query="login", tags=["auth"])
        """
        tags = cls.TAG_PATTERN.findall(query)
        name_query = cls.TAG_PATTERN.sub("", query).strip()

        return ParsedQuery(
            name_query=name_query if name_query else None,
            tags=[t.lower() for t in tags],
        )


class SearchService:
    """Service for search and discovery operations."""

    def __init__(
        self,
        client: AllureClient,
    ) -> None:
        self._client = client
        self._project_id = client.get_project()

    async def get_test_case_details(self, test_case_id: int) -> TestCaseDetails:
        """Retrieve a single test case with full details."""

        if not isinstance(test_case_id, int) or test_case_id <= 0:
            raise AllureValidationError("Test case ID must be a positive integer")

        try:
            test_case = await self._client.get_test_case(test_case_id)
            scenario = await self._client.get_test_case_scenario(test_case_id)
            return TestCaseDetails(test_case=test_case, scenario=scenario)
        except TestCaseNotFoundError:
            raise
        except AllureNotFoundError as e:
            raise TestCaseNotFoundError(
                test_case_id=test_case_id,
                status_code=e.status_code,
                response_body=e.response_body,
            ) from e

    async def list_test_cases(
        self,
        page: int = 0,
        size: int = 20,
        name_filter: str | None = None,
        tags: list[str] | None = None,
        status: str | None = None,
    ) -> TestCaseListResult:
        """List test cases in a project with pagination.

        Args:
            page: Zero-based page index.
            size: Page size.
            name_filter: Optional search query for test case name.
            tags: Optional list of tags to filter.
            status: Optional test case status filter.

        Returns:
            TestCaseListResult with items and pagination metadata.
        """
        self._validate_project_id(self._project_id)
        self._validate_pagination(page, size)

        response = await self._client.list_test_cases(
            project_id=self._project_id,
            page=page,
            size=size,
            search=name_filter,
            tags=tags,
            status=status,
        )

        return self._build_result(response)

    async def search_test_cases(
        self,
        query: str,
        page: int = 0,
        size: int = 20,
    ) -> TestCaseListResult:
        """Search test cases by name and/or tag query.

        Args:
            query: Search query with optional tag: filters.
            page: Zero-based page index.
            size: Page size.

        Returns:
            TestCaseListResult with items and pagination metadata.
        """
        self._validate_project_id(self._project_id)
        self._validate_pagination(page, size)

        if not isinstance(query, str) or not query.strip():
            raise AllureValidationError("Search query must be a non-empty string")

        parsed = SearchQueryParser.parse(query)
        if not parsed.name_query and not parsed.tags:
            raise AllureValidationError("Search query must include a name or tag filter")

        response = await self._client.list_test_cases(
            project_id=self._project_id,
            page=page,
            size=size,
            search=parsed.name_query,
            tags=parsed.tags or None,
            status=None,
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
