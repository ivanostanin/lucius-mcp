"""Service for managing Launches in Allure TestOps."""

import base64
import binascii
import ipaddress
import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal
from urllib.parse import urlsplit

import httpx
from pydantic import ValidationError as PydanticValidationError

from src.client import AllureClient, FindAll29200Response, LaunchCreateDto, LaunchDto, LaunchUploadResponseDto
from src.client.exceptions import AllureAPIError, AllureNotFoundError, AllureValidationError, LaunchNotFoundError
from src.client.generated.models.aql_validate_response_dto import AqlValidateResponseDto
from src.client.generated.models.external_link_dto import ExternalLinkDto
from src.client.generated.models.external_run_start_request_dto import ExternalRunStartRequestDto
from src.client.generated.models.issue_dto import IssueDto
from src.client.generated.models.job import Job
from src.client.generated.models.job_run import JobRun
from src.client.generated.models.launch import Launch
from src.client.generated.models.launch_existing_upload_dto import LaunchExistingUploadDto
from src.client.generated.models.launch_preview_dto import LaunchPreviewDto
from src.client.generated.models.launch_tag_dto import LaunchTagDto
from src.client.generated.models.manual_session_request_dto import ManualSessionRequestDto
from src.client.generated.models.page_launch_dto import PageLaunchDto
from src.client.generated.models.page_launch_preview_dto import PageLaunchPreviewDto
from src.client.generated.models.page_test_result_flat_dto import PageTestResultFlatDto
from src.client.generated.models.session_variable import SessionVariable
from src.client.generated.models.test_fixture_result_v2_dto import TestFixtureResultV2Dto
from src.client.generated.models.test_result_bulk_rerun_dto import TestResultBulkRerunDto
from src.client.generated.models.test_result_flat_dto import TestResultFlatDto
from src.client.generated.models.test_status import TestStatus
from src.client.generated.models.upload_attachment_dto import UploadAttachmentDto
from src.client.generated.models.upload_parameter_dto import UploadParameterDto
from src.client.generated.models.upload_results_dto import UploadResultsDto
from src.client.generated.models.upload_test_fixture_result_dto_steps_inner import UploadTestFixtureResultDtoStepsInner
from src.client.generated.models.upload_test_result_attachment_step_dto import UploadTestResultAttachmentStepDto
from src.client.generated.models.upload_test_result_body_step_dto import UploadTestResultBodyStepDto
from src.client.generated.models.upload_test_result_dto import UploadTestResultDto
from src.client.generated.models.upload_test_result_expected_body_step_dto import UploadTestResultExpectedBodyStepDto
from src.client.generated.models.upload_test_status import UploadTestStatus
from src.services.attachment_service import ALLOWED_MIME_TYPES, MAX_ATTACHMENT_SIZE
from src.utils.aql import quote_aql_string
from src.utils.schema_hint import generate_schema_hint

MAX_NAME_LENGTH = 255
MAX_TAG_LENGTH = 255
ATTACHMENT_DOWNLOAD_TIMEOUT_SECONDS = 10.0
ALLOWED_ATTACHMENT_URL_SCHEMES = frozenset({"http", "https"})
BLOCKED_ATTACHMENT_HOSTNAMES = frozenset({"localhost"})
BLOCKED_ATTACHMENT_HOST_SUFFIXES = (".localhost", ".local")

type LaunchListItem = LaunchDto | LaunchPreviewDto


@dataclass
class LaunchListResult:
    """Result of listing launches."""

    items: Sequence[LaunchListItem]
    total: int
    page: int
    size: int
    total_pages: int


@dataclass
class LaunchDeleteResult:
    """Result of a launch delete operation."""

    launch_id: int
    status: Literal["archived", "already_deleted"]
    message: str
    name: str | None = None


@dataclass
class LaunchTestResultListItem:
    """Compact launch test result view for tool output."""

    result_id: int | None
    test_case_id: int | None
    name: str | None
    manual: bool | None
    status: str | None
    assignee: str | None
    tested_by: str | None


@dataclass
class LaunchTestResultListResult:
    """Paginated launch test results."""

    items: Sequence[LaunchTestResultListItem]
    total: int
    page: int
    size: int
    total_pages: int


@dataclass
class ManualRerunResult:
    """Summary of manual rerun scheduling."""

    launch_id: int
    result_ids: list[int]
    scheduled_count: int
    assignees: list[str]
    force_manual: bool


@dataclass
class ManualTestSessionResult:
    """Manual test session metadata."""

    test_session_id: int
    launch_id: int | None
    job_id: int | None
    job_run_id: int | None
    project_id: int | None
    environment: list[dict[str, str]]


@dataclass
class ManualTestSubmissionResult:
    """Submitted manual result summary."""

    test_session_id: int
    result_ids: list[int]
    submitted_count: int


@dataclass
class AttachmentUploadResult:
    """Attachment upload confirmation."""

    target_kind: Literal["test_result", "test_step"]
    target_id: int
    file_names: list[str]
    status_code: int


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
        normalized_search = search.strip() if isinstance(search, str) else search
        if normalized_search == "":
            normalized_search = None

        try:
            response = await self._client.list_launches(
                project_id=self._project_id,
                page=page,
                size=size,
                search=normalized_search,
                filter_id=filter_id,
                sort=sort,
            )
        except AllureValidationError as exc:
            if not self._should_fallback_to_aql(search=normalized_search, filter_id=filter_id, error=exc):
                raise

            # normalized_search is guaranteed non-None here: _should_fallback_to_aql
            # returns False for None/empty search, so we never reach this line otherwise.
            if normalized_search is None:  # pragma: no cover
                raise AllureValidationError("Search fallback reached with empty query") from None
            return await self.search_launches_aql(
                rql=f'name ~= "{quote_aql_string(normalized_search)}"',
                page=page,
                size=size,
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

        try:
            return await self._client.get_launch(launch_id)
        except AllureNotFoundError as exc:
            raise LaunchNotFoundError(
                launch_id=launch_id,
                status_code=exc.status_code,
                response_body=exc.response_body,
            ) from exc

    async def close_launch(self, launch_id: int) -> LaunchDto:
        """Close a launch and return updated launch details."""
        self._validate_project_id(self._project_id)
        self._validate_launch_id(launch_id)

        pre_close = await self.get_launch(launch_id)

        try:
            await self._client.close_launch(launch_id)
            closed_launch = await self._client.get_launch(launch_id)
        except AllureNotFoundError as exc:
            raise LaunchNotFoundError(
                launch_id=launch_id,
                status_code=exc.status_code,
                response_body=exc.response_body,
            ) from exc

        if closed_launch.closed is not True:
            raise AllureAPIError(
                f"Launch {launch_id} was not closed by API",
                suggestions=["Retry close_launch", "Inspect launch state via get_launch"],
            )

        close_report = self._determine_close_report_status(pre_close, closed_launch)
        closed_launch.__dict__["close_report_generation"] = close_report
        return closed_launch

    async def reopen_launch(self, launch_id: int) -> LaunchDto:
        """Reopen a launch and return updated launch details."""
        self._validate_project_id(self._project_id)
        self._validate_launch_id(launch_id)

        try:
            await self._client.reopen_launch(launch_id)
            reopened = await self._client.get_launch(launch_id)
        except AllureNotFoundError as exc:
            raise LaunchNotFoundError(
                launch_id=launch_id,
                status_code=exc.status_code,
                response_body=exc.response_body,
            ) from exc

        if reopened.closed is True:
            raise AllureAPIError(
                f"Launch {launch_id} was not reopened by API",
                suggestions=["Retry reopen_launch", "Inspect launch state via get_launch"],
            )

        return reopened

    async def upload_results_to_launch(
        self,
        launch_id: int,
        files: list[bytes | str | tuple[str, bytes]],
    ) -> LaunchUploadResponseDto:
        """Upload result files to an existing launch."""
        self._validate_project_id(self._project_id)
        self._validate_launch_id(launch_id)

        if not isinstance(files, list) or not files:
            raise AllureValidationError("files must be a non-empty list")

        upload_info = LaunchExistingUploadDto()
        return await self._client.upload_results_to_launch(launch_id=launch_id, files=files, info=upload_info)

    async def list_launch_test_results(
        self,
        launch_id: int,
        *,
        page: int = 0,
        size: int = 100,
        search: str | None = None,
        filter_id: int | None = None,
        sort: list[str] | None = None,
        manual_only: bool = False,
        failed_only: bool = False,
    ) -> LaunchTestResultListResult:
        """List launch test results with optional manual/status filtering."""
        self._validate_project_id(self._project_id)
        self._validate_launch_id(launch_id)
        self._validate_pagination(page, size)

        normalized_search = search.strip() if isinstance(search, str) else search
        if normalized_search == "":
            normalized_search = None

        try:
            if manual_only or failed_only:
                return await self._list_and_filter_all_launch_test_results(
                    launch_id=launch_id,
                    page=page,
                    size=size,
                    search=normalized_search,
                    filter_id=filter_id,
                    sort=sort,
                    manual_only=manual_only,
                    failed_only=failed_only,
                )

            response = await self._client.list_launch_test_results(
                launch_id,
                page=page,
                size=size,
                search=normalized_search,
                filter_id=filter_id,
                sort=sort,
            )
        except AllureNotFoundError as exc:
            raise AllureNotFoundError(
                f"Launch ID {launch_id} not found",
                status_code=exc.status_code,
                response_body=exc.response_body,
            ) from exc

        return self._to_launch_test_result_page(response, page=page, size=size)

    async def rerun_test_results_manually(
        self,
        launch_id: int,
        *,
        result_ids: list[int],
        assignees: list[str] | None = None,
        force_manual: bool = True,
    ) -> ManualRerunResult:
        """Schedule manual reruns for selected launch test results."""
        self._validate_project_id(self._project_id)
        self._validate_launch_id(launch_id)

        normalized_result_ids = self._validate_positive_int_list(
            result_ids,
            "Result IDs must be a non-empty list of positive integers",
        )
        if not normalized_result_ids:
            raise AllureValidationError("Result IDs must be a non-empty list of positive integers")

        await self._ensure_result_ids_belong_to_launch(launch_id, normalized_result_ids)
        normalized_assignees = self._normalize_usernames(assignees)
        selection = {"launchId": launch_id, "leafsInclude": normalized_result_ids}

        try:
            bulk_payload = TestResultBulkRerunDto(
                selection=selection,
                force_manual=force_manual,
                assignees=normalized_assignees or None,
            )
        except PydanticValidationError as exc:
            hint = generate_schema_hint(TestResultBulkRerunDto)
            raise AllureValidationError(f"Invalid rerun payload: {exc}", suggestions=[hint]) from exc

        try:
            await self._client.rerun_test_results_bulk(bulk_payload)
        except AllureNotFoundError as exc:
            raise AllureNotFoundError(
                f"Launch ID {launch_id} or one of the selected result IDs no longer exists",
                status_code=exc.status_code,
                response_body=exc.response_body,
            ) from exc

        return ManualRerunResult(
            launch_id=launch_id,
            result_ids=normalized_result_ids,
            scheduled_count=len(normalized_result_ids),
            assignees=normalized_assignees,
            force_manual=force_manual,
        )

    async def start_manual_test_session(
        self,
        launch_id: int,
        *,
        environment: list[dict[str, str]] | None = None,
    ) -> ManualTestSessionResult:
        """Start a manual test session for a launch."""
        self._validate_project_id(self._project_id)
        self._validate_launch_id(launch_id)
        session_environment = self._build_session_environment(environment)
        job_uid = f"manual-session-job-{uuid.uuid4().hex}"
        job_run_uid = f"manual-session-run-{uuid.uuid4().hex}"

        try:
            external_run_payload = ExternalRunStartRequestDto(
                project_id=self._project_id,
                launch=Launch(id=launch_id),
                job=Job(uid=job_uid),
                job_run=JobRun(uid=job_run_uid),
            )
        except PydanticValidationError as exc:
            hint = generate_schema_hint(ExternalRunStartRequestDto)
            raise AllureValidationError(f"Invalid external run payload: {exc}", suggestions=[hint]) from exc

        try:
            await self._client.start_external_run(external_run_payload)
        except AllureNotFoundError as exc:
            raise AllureNotFoundError(
                f"Launch ID {launch_id} not found",
                status_code=exc.status_code,
                response_body=exc.response_body,
            ) from exc

        try:
            payload = ManualSessionRequestDto(
                launch_id=launch_id,
                project_id=self._project_id,
                job_uid=job_uid,
                job_run_uid=job_run_uid,
                environment=session_environment or None,
            )
        except PydanticValidationError as exc:
            hint = generate_schema_hint(ManualSessionRequestDto)
            raise AllureValidationError(f"Invalid manual session payload: {exc}", suggestions=[hint]) from exc

        try:
            response = await self._client.start_manual_test_session(payload)
        except AllureNotFoundError as exc:
            raise AllureNotFoundError(
                f"Launch ID {launch_id} not found",
                status_code=exc.status_code,
                response_body=exc.response_body,
            ) from exc

        session_id = response.id
        if session_id is None:
            raise AllureAPIError("Manual session response did not include a test session ID")

        return ManualTestSessionResult(
            test_session_id=session_id,
            launch_id=response.launch_id,
            job_id=response.job_id,
            job_run_id=response.job_run_id,
            project_id=response.project_id,
            environment=[item.model_dump(exclude_none=True) for item in session_environment],
        )

    async def submit_manual_test_results(
        self,
        test_session_id: int,
        *,
        results: list[dict[str, Any]],
    ) -> ManualTestSubmissionResult:
        """Submit manual test results and nested step updates."""
        self._validate_positive_id(test_session_id, "Test Session ID")
        if not isinstance(results, list) or not results:
            raise AllureValidationError("results must be a non-empty list")

        result_dtos = [self._build_upload_test_result(result, index=i) for i, result in enumerate(results)]

        try:
            payload = UploadResultsDto(
                test_session_id=test_session_id,
                results=result_dtos,
            )
        except PydanticValidationError as exc:
            hint = generate_schema_hint(UploadResultsDto)
            raise AllureValidationError(f"Invalid manual result payload: {exc}", suggestions=[hint]) from exc

        try:
            response = await self._client.submit_manual_test_results(payload)
        except AllureNotFoundError as exc:
            raise AllureNotFoundError(
                f"Test session ID {test_session_id} not found",
                status_code=exc.status_code,
                response_body=exc.response_body,
            ) from exc

        result_ids = [result_id for result_id in response.result_ids or [] if isinstance(result_id, int)]
        return ManualTestSubmissionResult(
            test_session_id=test_session_id,
            result_ids=result_ids,
            submitted_count=len(result_dtos),
        )

    async def add_test_result_attachment(
        self,
        test_result_id: int,
        *,
        attachment: dict[str, str],
    ) -> AttachmentUploadResult:
        """Upload one attachment to a manual test result."""
        self._validate_positive_id(test_result_id, "Test Result ID")
        file_entry = await self._prepare_attachment_file(attachment)

        try:
            status_code = await self._client.add_test_result_attachment(test_result_id, [file_entry])
        except AllureNotFoundError as exc:
            raise AllureNotFoundError(
                f"Test result ID {test_result_id} not found",
                status_code=exc.status_code,
                response_body=exc.response_body,
            ) from exc

        return AttachmentUploadResult(
            target_kind="test_result",
            target_id=test_result_id,
            file_names=[file_entry[0]],
            status_code=status_code,
        )

    async def add_test_step_attachment(
        self,
        *,
        test_result_id: int,
        attachment: dict[str, str],
        fixture_result_id: int | None = None,
        fixture_name: str | None = None,
        fixture_type: Literal["before", "after"] | None = None,
    ) -> AttachmentUploadResult:
        """Upload one attachment to a fixture-backed step context."""
        self._validate_positive_id(test_result_id, "Test Result ID")
        target_fixture_id = fixture_result_id or await self._resolve_fixture_result_id(
            test_result_id=test_result_id,
            fixture_name=fixture_name,
            fixture_type=fixture_type,
        )
        self._validate_positive_id(target_fixture_id, "Fixture Result ID")
        file_entry = await self._prepare_attachment_file(attachment)

        try:
            status_code = await self._client.add_test_fixture_attachment(target_fixture_id, [file_entry])
        except AllureNotFoundError as exc:
            raise AllureNotFoundError(
                f"Fixture result ID {target_fixture_id} not found",
                status_code=exc.status_code,
                response_body=exc.response_body,
            ) from exc

        return AttachmentUploadResult(
            target_kind="test_step",
            target_id=target_fixture_id,
            file_names=[file_entry[0]],
            status_code=status_code,
        )

    async def _ensure_result_ids_belong_to_launch(self, launch_id: int, result_ids: Sequence[int]) -> None:
        available_result_ids = await self._collect_launch_result_ids(launch_id)
        missing_result_ids = [result_id for result_id in result_ids if result_id not in available_result_ids]
        if missing_result_ids:
            missing_result_ids = await self._resolve_missing_launch_result_ids(launch_id, missing_result_ids)
        if not missing_result_ids:
            return

        if len(missing_result_ids) == 1:
            raise AllureNotFoundError(f"Result ID {missing_result_ids[0]} not found in launch ID {launch_id}")

        joined_ids = ", ".join(str(result_id) for result_id in missing_result_ids)
        raise AllureNotFoundError(f"Result IDs {joined_ids} not found in launch ID {launch_id}")

    async def _resolve_missing_launch_result_ids(self, launch_id: int, result_ids: Sequence[int]) -> list[int]:
        unresolved_result_ids: list[int] = []

        for result_id in result_ids:
            try:
                result = await self._client.get_test_result(result_id)
            except AllureNotFoundError:
                unresolved_result_ids.append(result_id)
                continue

            if result.launch_id != launch_id:
                unresolved_result_ids.append(result_id)

        return unresolved_result_ids

    async def _collect_launch_result_ids(self, launch_id: int) -> set[int]:
        available_result_ids: set[int] = set()
        current_page = 0
        total_pages = 1

        while current_page < total_pages:
            response = await self._fetch_launch_results_page(
                launch_id=launch_id,
                page=current_page,
                size=100,
                search=None,
                filter_id=None,
                sort=None,
            )
            total_pages = response.total_pages or 1
            available_result_ids.update(item.id for item in response.content or [] if isinstance(item.id, int))
            current_page += 1

        return available_result_ids

    @staticmethod
    def _determine_close_report_status(pre_close: LaunchDto, closed_launch: LaunchDto) -> str:
        if pre_close.closed is True:
            return "already-closed"

        status = getattr(closed_launch, "status", None)
        if isinstance(status, str) and status.strip():
            return status

        return "scheduled"

    async def delete_launch(self, launch_id: int) -> LaunchDeleteResult:
        """Delete/archive a launch by ID with idempotent behavior."""
        self._validate_project_id(self._project_id)
        self._validate_launch_id(launch_id)

        try:
            launch = await self.get_launch(launch_id)
        except LaunchNotFoundError:
            return LaunchDeleteResult(
                launch_id=launch_id,
                status="already_deleted",
                message=f"Launch {launch_id} was already archived or doesn't exist.",
            )

        await self._client.delete_launch(launch_id)

        return LaunchDeleteResult(
            launch_id=launch_id,
            status="archived",
            name=launch.name,
            message=f"Launch {launch_id} has been archived.",
        )

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
    def _should_fallback_to_aql(search: str | None, filter_id: int | None, error: AllureValidationError) -> bool:
        if not search or filter_id is not None:
            return False

        message = str(error).lower()
        return "invalid search" in message or ("search" in message and "invalid" in message)

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
    def _validate_positive_id(value: int, label: str) -> None:
        if not isinstance(value, int):
            raise AllureValidationError(f"{label} must be an integer, got {type(value).__name__}")
        if value <= 0:
            raise AllureValidationError(f"{label} must be a positive integer")

    @staticmethod
    def _validate_positive_int_list(values: list[int] | None, message: str) -> list[int]:
        if not isinstance(values, list) or not values:
            raise AllureValidationError(message)

        normalized: list[int] = []
        for value in values:
            if not isinstance(value, int) or value <= 0:
                raise AllureValidationError(message)
            normalized.append(value)
        return normalized

    @staticmethod
    def _normalize_usernames(values: list[str] | None) -> list[str]:
        if values is None:
            return []
        if not isinstance(values, list):
            raise AllureValidationError(f"assignees must be a list, got {type(values).__name__}")

        normalized: list[str] = []
        for index, value in enumerate(values):
            if not isinstance(value, str):
                raise AllureValidationError(f"Assignee at index {index} must be a string")
            stripped = value.strip()
            if not stripped:
                raise AllureValidationError(f"Assignee at index {index} cannot be empty")
            normalized.append(stripped)
        return normalized

    @staticmethod
    def _normalize_status(value: object, *, field_name: str) -> UploadTestStatus | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise AllureValidationError(f"{field_name} must be a string")

        normalized = value.strip().upper()
        if not normalized:
            raise AllureValidationError(f"{field_name} cannot be empty")

        try:
            return UploadTestStatus(normalized)
        except ValueError as exc:
            allowed = ", ".join(status.value for status in UploadTestStatus)
            raise AllureValidationError(f"Invalid {field_name}: {value!r}. Allowed values: {allowed}") from exc

    @staticmethod
    def _normalize_timestamp(value: object, *, field_name: str) -> int | None:
        if value is None:
            return None
        if not isinstance(value, int):
            raise AllureValidationError(f"{field_name} must be an integer timestamp")
        if value < 0:
            raise AllureValidationError(f"{field_name} must be a non-negative integer timestamp")
        return value

    @classmethod
    def _validate_time_window(cls, *, start: int | None, stop: int | None, field_prefix: str) -> None:
        if start is not None and stop is not None and stop < start:
            raise AllureValidationError(f"{field_prefix} stop must be greater than or equal to start")

    @staticmethod
    def _normalize_text(value: object, *, field_name: str, allow_empty: bool = False) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise AllureValidationError(f"{field_name} must be a string")
        text = value.strip()
        if not allow_empty and not text:
            raise AllureValidationError(f"{field_name} cannot be empty")
        return text if text or allow_empty else None

    @classmethod
    def _build_session_environment(cls, environment: list[dict[str, str]] | None) -> list[SessionVariable]:
        if environment is None:
            return []
        if not isinstance(environment, list):
            raise AllureValidationError("environment must be a list of {key, value} objects")

        variables: list[SessionVariable] = []
        for index, item in enumerate(environment):
            if not isinstance(item, dict):
                raise AllureValidationError(f"Environment item at index {index} must be a dictionary")
            key = cls._normalize_text(item.get("key"), field_name=f"environment[{index}].key")
            value = cls._normalize_text(item.get("value"), field_name=f"environment[{index}].value", allow_empty=True)
            variables.append(SessionVariable(key=key, value=value or ""))
        return variables

    @classmethod
    def _to_launch_test_result_page(
        cls,
        response: PageTestResultFlatDto,
        *,
        page: int,
        size: int,
    ) -> LaunchTestResultListResult:
        items = [cls._to_launch_test_result_item(item) for item in response.content or []]
        return LaunchTestResultListResult(
            items=items,
            total=response.total_elements or len(items),
            page=response.number or page,
            size=response.size or size,
            total_pages=response.total_pages or 1,
        )

    @staticmethod
    def _to_launch_test_result_item(item: TestResultFlatDto) -> LaunchTestResultListItem:
        status_value = (
            item.status.value if isinstance(item.status, TestStatus) else str(item.status) if item.status else None
        )
        return LaunchTestResultListItem(
            result_id=item.id,
            test_case_id=item.test_case_id,
            name=item.name,
            manual=item.manual,
            status=status_value,
            assignee=item.assignee,
            tested_by=item.tested_by,
        )

    async def _list_and_filter_all_launch_test_results(
        self,
        *,
        launch_id: int,
        page: int,
        size: int,
        search: str | None,
        filter_id: int | None,
        sort: list[str] | None,
        manual_only: bool,
        failed_only: bool,
    ) -> LaunchTestResultListResult:
        collected: list[TestResultFlatDto] = []
        current_page = 0
        total_pages = 1

        while current_page < total_pages:
            response = await self._fetch_launch_results_page(
                launch_id=launch_id,
                page=current_page,
                size=100,
                search=search,
                filter_id=filter_id,
                sort=sort,
            )
            total_pages = response.total_pages or 1
            for item in response.content or []:
                if manual_only and item.manual is not True:
                    continue
                status_value = item.status.value if isinstance(item.status, TestStatus) else None
                if failed_only and status_value not in {TestStatus.FAILED.value, TestStatus.BROKEN.value}:
                    continue
                collected.append(item)
            current_page += 1

        start_index = page * size
        end_index = start_index + size
        page_items = [self._to_launch_test_result_item(item) for item in collected[start_index:end_index]]
        filtered_total = len(collected)
        filtered_total_pages = max(1, (filtered_total + size - 1) // size) if size > 0 else 1

        return LaunchTestResultListResult(
            items=page_items,
            total=filtered_total,
            page=page,
            size=size,
            total_pages=filtered_total_pages,
        )

    async def _fetch_launch_results_page(
        self,
        *,
        launch_id: int,
        page: int,
        size: int,
        search: str | None,
        filter_id: int | None,
        sort: list[str] | None,
    ) -> PageTestResultFlatDto:
        try:
            return await self._client.list_launch_test_results(
                launch_id,
                page=page,
                size=size,
                search=search,
                filter_id=filter_id,
                sort=sort,
            )
        except AllureNotFoundError as exc:
            raise AllureNotFoundError(
                f"Launch ID {launch_id} not found",
                status_code=exc.status_code,
                response_body=exc.response_body,
            ) from exc

    def _build_upload_test_result(self, result: dict[str, Any], *, index: int) -> UploadTestResultDto:
        if not isinstance(result, dict):
            raise AllureValidationError(f"results[{index}] must be a dictionary")

        test_case_id = result.get("test_case_id")
        if test_case_id is None:
            raise AllureValidationError(f"results[{index}].test_case_id is required")
        self._validate_positive_id(test_case_id, f"results[{index}].test_case_id")
        result_name, result_full_name, result_uuid, history_id = self._resolve_upload_result_identity(
            result,
            index=index,
        )

        start = self._normalize_timestamp(result.get("start"), field_name=f"results[{index}].start")
        stop = self._normalize_timestamp(result.get("stop"), field_name=f"results[{index}].stop")
        self._validate_time_window(start=start, stop=stop, field_prefix=f"results[{index}]")

        steps = result.get("steps")
        step_dtos = None
        if steps is not None:
            if not isinstance(steps, list):
                raise AllureValidationError(f"results[{index}].steps must be a list")
            step_dtos = [
                self._build_upload_step(step, result_index=index, step_index=i) for i, step in enumerate(steps)
            ]

        parameters = result.get("parameters")
        parameter_dtos = None
        if parameters is not None:
            if not isinstance(parameters, list):
                raise AllureValidationError(f"results[{index}].parameters must be a list")
            parameter_dtos = [
                UploadParameterDto(
                    name=self._normalize_text(param.get("name"), field_name=f"results[{index}].parameters[{i}].name"),
                    value=self._normalize_text(
                        param.get("value"),
                        field_name=f"results[{index}].parameters[{i}].value",
                        allow_empty=True,
                    )
                    or "",
                )
                for i, param in enumerate(parameters)
                if isinstance(param, dict)
            ]
            if len(parameter_dtos) != len(parameters):
                raise AllureValidationError(f"results[{index}].parameters must contain only dictionaries")

        try:
            return UploadTestResultDto(
                test_case_id=str(test_case_id),
                name=result_name,
                full_name=result_full_name,
                uuid=result_uuid,
                history_id=history_id,
                status=self._normalize_status(result.get("status"), field_name=f"results[{index}].status"),
                start=start,
                stop=stop,
                message=self._normalize_text(
                    result.get("message"),
                    field_name=f"results[{index}].message",
                    allow_empty=True,
                ),
                trace=self._normalize_text(
                    result.get("trace"),
                    field_name=f"results[{index}].trace",
                    allow_empty=True,
                ),
                description=self._normalize_text(
                    result.get("description"),
                    field_name=f"results[{index}].description",
                    allow_empty=True,
                ),
                precondition=self._normalize_text(
                    result.get("precondition"),
                    field_name=f"results[{index}].precondition",
                    allow_empty=True,
                ),
                expected_result=self._normalize_text(
                    result.get("expected_result"),
                    field_name=f"results[{index}].expected_result",
                    allow_empty=True,
                ),
                steps=step_dtos,
                parameters=parameter_dtos,
            )
        except PydanticValidationError as exc:
            hint = generate_schema_hint(UploadTestResultDto)
            raise AllureValidationError(
                f"Invalid test result payload at index {index}: {exc}",
                suggestions=[hint],
            ) from exc

    def _resolve_upload_result_identity(
        self,
        result: dict[str, Any],
        *,
        index: int,
    ) -> tuple[str, str, str, str]:
        result_name = self._normalize_text(
            result.get("name"),
            field_name=f"results[{index}].name",
            allow_empty=True,
        )
        result_full_name = self._normalize_text(
            result.get("full_name"),
            field_name=f"results[{index}].full_name",
            allow_empty=True,
        )
        if not result_name and not result_full_name:
            raise AllureValidationError(f"results[{index}].name is required for manual upload")

        resolved_name = result_name or result_full_name
        resolved_full_name = result_full_name or resolved_name
        if resolved_name is None or resolved_full_name is None:  # pragma: no cover - guarded above
            raise AllureAPIError("Manual upload identity resolution failed")

        result_uuid = self._normalize_text(
            result.get("uuid"),
            field_name=f"results[{index}].uuid",
            allow_empty=True,
        ) or str(uuid.uuid4())
        history_id = self._normalize_text(
            result.get("history_id"),
            field_name=f"results[{index}].history_id",
            allow_empty=True,
        ) or str(uuid.uuid4())

        return resolved_name, resolved_full_name, result_uuid, history_id

    def _build_upload_step(
        self,
        step: dict[str, Any],
        *,
        result_index: int,
        step_index: int,
    ) -> UploadTestFixtureResultDtoStepsInner:
        if not isinstance(step, dict):
            raise AllureValidationError(f"results[{result_index}].steps[{step_index}] must be a dictionary")

        raw_type = step.get("type")
        if not isinstance(raw_type, str):
            raise AllureValidationError(f"results[{result_index}].steps[{step_index}].type is required")
        normalized_type = raw_type.strip().lower()

        start = self._normalize_timestamp(
            step.get("start"),
            field_name=f"results[{result_index}].steps[{step_index}].start",
        )
        stop = self._normalize_timestamp(
            step.get("stop"),
            field_name=f"results[{result_index}].steps[{step_index}].stop",
        )
        self._validate_time_window(
            start=start,
            stop=stop,
            field_prefix=f"results[{result_index}].steps[{step_index}]",
        )
        status = self._normalize_status(
            step.get("status"),
            field_name=f"results[{result_index}].steps[{step_index}].status",
        )

        if normalized_type == "body":
            return UploadTestFixtureResultDtoStepsInner(
                UploadTestResultBodyStepDto(
                    type="UploadTestResultBodyStepDto",
                    body=self._normalize_text(
                        step.get("body"),
                        field_name=f"results[{result_index}].steps[{step_index}].body",
                        allow_empty=True,
                    ),
                    message=self._normalize_text(
                        step.get("message"),
                        field_name=f"results[{result_index}].steps[{step_index}].message",
                        allow_empty=True,
                    ),
                    trace=self._normalize_text(
                        step.get("trace"),
                        field_name=f"results[{result_index}].steps[{step_index}].trace",
                        allow_empty=True,
                    ),
                    start=start,
                    stop=stop,
                    status=status,
                )
            )

        if normalized_type == "expected":
            return UploadTestFixtureResultDtoStepsInner(
                UploadTestResultExpectedBodyStepDto(
                    type="UploadTestResultExpectedBodyStepDto",
                    body=self._normalize_text(
                        step.get("body"),
                        field_name=f"results[{result_index}].steps[{step_index}].body",
                        allow_empty=True,
                    ),
                    message=self._normalize_text(
                        step.get("message"),
                        field_name=f"results[{result_index}].steps[{step_index}].message",
                        allow_empty=True,
                    ),
                    start=start,
                    stop=stop,
                    status=status,
                )
            )

        if normalized_type == "attachment":
            attachment_meta = step.get("attachment")
            if not isinstance(attachment_meta, dict):
                raise AllureValidationError(
                    f"results[{result_index}].steps[{step_index}].attachment is required for attachment steps"
                )
            return UploadTestFixtureResultDtoStepsInner(
                UploadTestResultAttachmentStepDto(
                    type="UploadTestResultAttachmentStepDto",
                    attachment=UploadAttachmentDto(
                        name=self._normalize_text(
                            attachment_meta.get("name"),
                            field_name=f"results[{result_index}].steps[{step_index}].attachment.name",
                        ),
                        content_type=self._normalize_text(
                            attachment_meta.get("content_type"),
                            field_name=f"results[{result_index}].steps[{step_index}].attachment.content_type",
                        ),
                    ),
                    start=start,
                    stop=stop,
                    status=status,
                )
            )

        raise AllureValidationError(
            f"results[{result_index}].steps[{step_index}].type must be one of: body, expected, attachment"
        )

    async def _resolve_fixture_result_id(
        self,
        *,
        test_result_id: int,
        fixture_name: str | None,
        fixture_type: Literal["before", "after"] | None,
    ) -> int:
        fixtures = await self._get_test_result_fixtures_or_raise(test_result_id)
        matching = fixtures

        if fixture_name is not None:
            normalized_name = self._normalize_text(fixture_name, field_name="fixture_name")
            matching = [fixture for fixture in matching if fixture.name == normalized_name]

        if fixture_type is not None:
            normalized_type = fixture_type.strip().lower()
            if normalized_type not in {"before", "after"}:
                raise AllureValidationError("fixture_type must be 'before' or 'after'")
            matching = [fixture for fixture in matching if fixture.type and fixture.type.value == normalized_type]

        matching_ids = [fixture.id for fixture in matching if isinstance(fixture.id, int)]
        if not matching_ids:
            raise AllureNotFoundError(f"No matching fixture result found for test result ID {test_result_id}")
        if len(matching_ids) > 1:
            raise AllureValidationError(
                "Fixture selection is ambiguous. Provide fixture_result_id or narrow the selection "
                "with fixture_name/fixture_type."
            )
        return matching_ids[0]

    async def _get_test_result_fixtures_or_raise(self, test_result_id: int) -> list[TestFixtureResultV2Dto]:
        try:
            return await self._client.get_test_result_fixtures(test_result_id)
        except AllureNotFoundError as exc:
            raise AllureNotFoundError(
                f"Test result ID {test_result_id} not found",
                status_code=exc.status_code,
                response_body=exc.response_body,
            ) from exc

    async def _prepare_attachment_file(self, attachment: dict[str, str]) -> tuple[str, bytes]:
        if not isinstance(attachment, dict):
            raise AllureValidationError("attachment must be a dictionary")

        name = self._normalize_text(attachment.get("name"), field_name="attachment.name")
        content_type = self._normalize_text(attachment.get("content_type"), field_name="attachment.content_type")
        if content_type not in ALLOWED_MIME_TYPES:
            raise AllureValidationError(f"Content-Type '{content_type}' is not allowed or supported.")
        if name is None:
            raise AllureValidationError("attachment.name is required")

        content = await self._retrieve_attachment_content(attachment)
        if len(content) > MAX_ATTACHMENT_SIZE:
            raise AllureValidationError(
                f"Attachment size {len(content)} bytes exceeds limit of {MAX_ATTACHMENT_SIZE} bytes"
            )

        return (name, content)

    async def _retrieve_attachment_content(self, attachment: dict[str, str]) -> bytes:
        content_b64 = attachment.get("content")
        url = attachment.get("url")

        if content_b64:
            if url:
                raise AllureValidationError("Cannot specify both 'content' and 'url' for attachment")
            return self._decode_base64_attachment_content(content_b64)

        if url:
            validated_url = self._validate_attachment_url(url)
            return await self._download_attachment_from_url(validated_url)

        raise AllureValidationError("Attachment must have either 'content' or 'url'")

    @staticmethod
    def _decode_base64_attachment_content(content_b64: str) -> bytes:
        try:
            return base64.b64decode(content_b64)
        except binascii.Error as exc:
            raise AllureValidationError("Invalid base64 content") from exc

    async def _download_attachment_from_url(self, validated_url: str) -> bytes:
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "GET",
                    validated_url,
                    follow_redirects=False,
                    timeout=ATTACHMENT_DOWNLOAD_TIMEOUT_SECONDS,
                ) as response:
                    self._validate_attachment_download_response(response)
                    return await self._read_downloaded_attachment_content(response)
        except httpx.RequestError as exc:
            raise AllureValidationError(f"Failed to download attachment from {validated_url}: {exc!s}") from exc
        except httpx.HTTPStatusError as exc:
            raise AllureValidationError(
                f"Failed to download attachment from {validated_url}: HTTP {exc.response.status_code}"
            ) from exc

    @staticmethod
    def _validate_attachment_download_response(response: httpx.Response) -> None:
        if response.is_redirect:
            raise AllureValidationError("Attachment URL redirects are not allowed. Provide a direct downloadable URL.")

        response.raise_for_status()
        content_length = response.headers.get("Content-Length")
        if content_length is None:
            return

        try:
            content_length_value = int(content_length)
        except ValueError:
            return

        if content_length_value > MAX_ATTACHMENT_SIZE:
            raise AllureValidationError(
                f"Attachment size {content_length_value} bytes exceeds limit of {MAX_ATTACHMENT_SIZE} bytes"
            )

    @staticmethod
    async def _read_downloaded_attachment_content(response: httpx.Response) -> bytes:
        downloaded = bytearray()
        async for chunk in response.aiter_bytes():
            downloaded.extend(chunk)
            if len(downloaded) > MAX_ATTACHMENT_SIZE:
                raise AllureValidationError(f"Attachment size exceeds limit of {MAX_ATTACHMENT_SIZE} bytes")

        return bytes(downloaded)

    def _validate_attachment_url(self, url: object) -> str:
        normalized_url = self._normalize_text(url, field_name="attachment.url")
        if normalized_url is None:
            raise AllureValidationError("attachment.url is required")

        parsed = urlsplit(normalized_url)
        if parsed.scheme not in ALLOWED_ATTACHMENT_URL_SCHEMES:
            raise AllureValidationError("Attachment URL must use http or https")
        if not parsed.hostname:
            raise AllureValidationError("Attachment URL must include a hostname")

        hostname = parsed.hostname.lower()
        if hostname in BLOCKED_ATTACHMENT_HOSTNAMES or any(
            hostname.endswith(suffix) for suffix in BLOCKED_ATTACHMENT_HOST_SUFFIXES
        ):
            raise AllureValidationError("Attachment URL must not target localhost or local network hostnames")

        try:
            ip_value = ipaddress.ip_address(hostname)
        except ValueError:
            return normalized_url

        if (
            ip_value.is_private
            or ip_value.is_loopback
            or ip_value.is_link_local
            or ip_value.is_multicast
            or ip_value.is_reserved
            or ip_value.is_unspecified
        ):
            raise AllureValidationError("Attachment URL must not target private, loopback, or reserved IP ranges")

        return normalized_url

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
