"""Service for managing Launches in Allure TestOps."""

import asyncio
import base64
import binascii
import ipaddress
import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal, cast
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
from src.client.generated.models.shared_step_scenario_dto_steps_inner import SharedStepScenarioDtoStepsInner
from src.client.generated.models.test_case_scenario_v2_dto import TestCaseScenarioV2Dto
from src.client.generated.models.test_fixture_result_v2_dto import TestFixtureResultV2Dto
from src.client.generated.models.test_result_attachment_row_dto import TestResultAttachmentRowDto
from src.client.generated.models.test_result_attachment_step_dto import TestResultAttachmentStepDto
from src.client.generated.models.test_result_attachment_step_dto_all_of_attachment import (
    TestResultAttachmentStepDtoAllOfAttachment,
)
from src.client.generated.models.test_result_bulk_rerun_dto import TestResultBulkRerunDto
from src.client.generated.models.test_result_create_v2_dto import TestResultCreateV2Dto
from src.client.generated.models.test_result_dto import TestResultDto
from src.client.generated.models.test_result_flat_dto import TestResultFlatDto
from src.client.generated.models.test_result_patch_dto import TestResultPatchDto
from src.client.generated.models.test_result_row_dto import TestResultRowDto
from src.client.generated.models.test_result_scenario_dto import TestResultScenarioDto
from src.client.generated.models.test_result_scenario_step_dto import TestResultScenarioStepDto
from src.client.generated.models.test_result_scenario_v2_dto import TestResultScenarioV2Dto
from src.client.generated.models.test_result_scenario_v2_dto_steps_inner import TestResultScenarioV2DtoStepsInner
from src.client.generated.models.test_status import TestStatus
from src.client.generated.models.upload_attachment_dto import UploadAttachmentDto
from src.client.generated.models.upload_parameter_dto import UploadParameterDto
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
MAX_LAUNCH_RESULT_UPLOAD_BATCH_SIZE = 1000
MAX_LAUNCH_RESULT_UPLOAD_CONCURRENCY = 20
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
    """Submitted manual result summary for newly created launch-managed results."""

    test_session_id: int
    result_ids: list[int]
    submitted_count: int


@dataclass
class LaunchResultUploadResult:
    """Summary of a bulk result upload to one launch."""

    launch_id: int
    requested_count: int
    uploaded_count: int
    result_ids: list[int]
    failures: list["LaunchResultUploadFailure"]


@dataclass
class LaunchResultUploadFailure:
    """One result that TestOps did not accept during a batch upload."""

    index: int
    message: str


@dataclass
class AttachmentUploadResult:
    """Attachment upload confirmation."""

    target_kind: Literal["test_result", "test_step"]
    target_id: int
    file_names: list[str]
    status_code: int


@dataclass
class _ResolvedManualStepAttachmentTarget:
    """Resolved manual-step attachment slot for one test result."""

    attachment_id: int
    step_index: int
    name: str | None = None


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

    async def add_results(self, launch_id: int, results: list[dict[str, Any]]) -> LaunchResultUploadResult:
        """Upload externally produced results to a launch concurrently.

        MCP callers need only a launch ID and friendly result dictionaries; the service
        maps each one to the native TestOps result DTO and submits the batch concurrently.
        """
        self._validate_project_id(self._project_id)
        self._validate_launch_id(launch_id)
        if not isinstance(results, list) or not results:
            raise AllureValidationError("results must be a non-empty list")
        if len(results) > MAX_LAUNCH_RESULT_UPLOAD_BATCH_SIZE:
            raise AllureValidationError(f"results must contain at most {MAX_LAUNCH_RESULT_UPLOAD_BATCH_SIZE} items")

        # Validate and normalize every item before creating remote results.
        upload_results = [self._build_upload_test_result(result, index=index) for index, result in enumerate(results)]
        await self.get_launch(launch_id)
        semaphore = asyncio.Semaphore(MAX_LAUNCH_RESULT_UPLOAD_CONCURRENCY)

        async def create_one(index: int, result: dict[str, Any], upload_result: UploadTestResultDto) -> TestResultDto:
            async with semaphore:
                return await self._create_manual_launch_result(
                    {
                        **result,
                        "launch_id": launch_id,
                        "name": upload_result.name,
                        "full_name": upload_result.full_name,
                        "status": upload_result.status.value.lower() if upload_result.status is not None else None,
                    },
                    index=index,
                )

        outcomes = await asyncio.gather(
            *(
                create_one(index, result, upload_result)
                for index, (result, upload_result) in enumerate(zip(results, upload_results, strict=True))
            ),
            return_exceptions=True,
        )
        result_ids: list[int] = []
        failures: list[LaunchResultUploadFailure] = []
        for index, outcome in enumerate(outcomes):
            if isinstance(outcome, asyncio.CancelledError):
                raise outcome
            if isinstance(outcome, BaseException):
                failures.append(
                    LaunchResultUploadFailure(
                        index=index,
                        message=str(outcome) or type(outcome).__name__,
                    )
                )
            elif isinstance(outcome.id, int):
                result_ids.append(outcome.id)
            else:
                failures.append(
                    LaunchResultUploadFailure(
                        index=index,
                        message="TestOps created a result without an ID",
                    )
                )

        return LaunchResultUploadResult(
            launch_id=launch_id,
            requested_count=len(upload_results),
            uploaded_count=len(result_ids),
            result_ids=result_ids,
            failures=failures,
        )

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

    async def resolve_launch_test_result_for_test_case(
        self,
        launch_id: int,
        *,
        test_case_id: int,
        status: str | None | Literal["any"] = "any",
    ) -> LaunchTestResultListItem:
        """Resolve one visible manual launch result for a specific test case."""
        self._validate_project_id(self._project_id)
        self._validate_launch_id(launch_id)
        self._validate_positive_id(test_case_id, "Test Case ID")
        expected_status = self._normalize_launch_result_status_filter(status)
        matches: list[LaunchTestResultListItem] = []
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
            for item in response.content or []:
                if item.manual is not True or item.test_case_id != test_case_id:
                    continue
                item_status = item.status.value if isinstance(item.status, TestStatus) else None
                if expected_status != "any" and item_status != expected_status:
                    continue
                matches.append(self._to_launch_test_result_item(item))
            current_page += 1

        if not matches:
            status_label = expected_status if expected_status != "any" else "any"
            raise AllureNotFoundError(
                f"No visible manual launch result found for launch ID {launch_id}, "
                f"test case ID {test_case_id}, status {status_label!r}"
            )
        if len(matches) > 1:
            matching_ids = ", ".join(str(match.result_id) for match in matches if isinstance(match.result_id, int))
            raise AllureValidationError(
                f"Expected exactly one visible manual launch result for launch ID {launch_id}, "
                f"test case ID {test_case_id}, status {expected_status!r}, "
                f"but found {len(matches)}: {matching_ids}"
            )
        return matches[0]

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
        """Submit manual execution payloads to existing or explicit launch contexts.

        When ``results[*].result_id`` is provided, the existing launch result is resolved
        in place via the test-result run controller. When explicit ``launch_id`` and
        ``test_case_id`` are provided without ``result_id``, the legacy create-new-result
        flow is used as a fallback.
        """
        self._validate_positive_id(test_session_id, "Test Session ID")
        if not isinstance(results, list) or not results:
            raise AllureValidationError("results must be a non-empty list")

        submitted_result_ids: list[int] = []
        for index, result in enumerate(results):
            if isinstance(result, dict) and result.get("result_id") is not None:
                resolved = await self._resolve_manual_launch_result(result, index=index)
                if isinstance(resolved.id, int):
                    submitted_result_ids.append(resolved.id)
                continue

            created = await self._create_manual_launch_result(result, index=index)
            if isinstance(created.id, int):
                submitted_result_ids.append(created.id)

        return ManualTestSubmissionResult(
            test_session_id=test_session_id,
            result_ids=submitted_result_ids,
            submitted_count=len(results),
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
            uploaded_rows = await self._client.create_test_result_attachments(test_result_id, [file_entry])
        except AllureNotFoundError as exc:
            raise AllureNotFoundError(
                f"Test result ID {test_result_id} not found",
                status_code=exc.status_code,
                response_body=exc.response_body,
            ) from exc

        uploaded_names = [row.name for row in uploaded_rows if isinstance(row.name, str) and row.name.strip()]
        return AttachmentUploadResult(
            target_kind="test_result",
            target_id=test_result_id,
            file_names=uploaded_names or [file_entry[0]],
            status_code=200,
        )

    async def add_test_step_attachment(
        self,
        *,
        test_result_id: int,
        attachment: dict[str, str],
        attachment_id: int | None = None,
        step_name: str | None = None,
        step_index: int | None = None,
        fixture_result_id: int | None = None,
        fixture_name: str | None = None,
        fixture_type: Literal["before", "after"] | None = None,
    ) -> AttachmentUploadResult:
        """Upload one attachment to a manual attachment step or explicit fixture fallback."""
        self._validate_positive_id(test_result_id, "Test Result ID")
        has_manual_selector = attachment_id is not None or step_name is not None or step_index is not None
        has_fixture_selector = fixture_result_id is not None or fixture_name is not None or fixture_type is not None
        if has_manual_selector and has_fixture_selector:
            raise AllureValidationError(
                "Specify either manual step selectors (attachment_id, step_name, step_index) "
                "or fixture selectors (fixture_result_id, fixture_name, fixture_type), not both."
            )

        attachment_name, _content_type = self._normalize_attachment_metadata(attachment)
        file_entry = await self._prepare_attachment_file(attachment)

        if has_fixture_selector:
            target_fixture_id = fixture_result_id or await self._resolve_fixture_result_id(
                test_result_id=test_result_id,
                fixture_name=fixture_name,
                fixture_type=fixture_type,
            )
            self._validate_positive_id(target_fixture_id, "Fixture Result ID")

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

        try:
            test_result = await self._get_test_result_or_raise(test_result_id)
            uploaded_rows = await self._client.create_test_result_attachments(test_result_id, [file_entry])
            uploaded_row = self._select_uploaded_attachment_row(uploaded_rows)
            patch_scenario = await self._build_manual_step_attachment_patch_scenario(
                test_result=test_result,
                attachment_row=uploaded_row,
                attachment_id=attachment_id,
                step_name=step_name,
                step_index=step_index,
            )
            await self._client.patch_test_result(
                test_result_id,
                TestResultPatchDto(
                    name=test_result.name or attachment_name,
                    full_name=test_result.full_name,
                    scenario=patch_scenario,
                ),
            )
        except AllureNotFoundError as exc:
            raise AllureNotFoundError(
                f"Test result ID {test_result_id} not found"
                if exc.status_code == 404 and "test result" in str(exc).lower()
                else str(exc),
                status_code=exc.status_code,
                response_body=exc.response_body,
            ) from exc

        return AttachmentUploadResult(
            target_kind="test_step",
            target_id=uploaded_row.id or test_result_id,
            file_names=[uploaded_row.name or file_entry[0]],
            status_code=200,
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
    def _validate_positive_id(value: object, label: str) -> None:
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
            allowed = ", ".join(status.value.lower() for status in UploadTestStatus)
            raise AllureValidationError(f"Invalid {field_name}: {value!r}. Allowed values: {allowed}") from exc

    @staticmethod
    def _normalize_test_status(value: object, *, field_name: str) -> TestStatus | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise AllureValidationError(f"{field_name} must be a string")

        normalized = value.strip().lower()
        if not normalized:
            raise AllureValidationError(f"{field_name} cannot be empty")

        try:
            return TestStatus(normalized)
        except ValueError as exc:
            allowed = ", ".join(status.value for status in TestStatus)
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
    def _resolve_duration(
        *,
        start: int | None,
        stop: int | None,
        value: object,
        field_name: str,
    ) -> int | None:
        if value is None:
            if start is not None and stop is not None:
                return stop - start
            return None
        if not isinstance(value, int):
            raise AllureValidationError(f"{field_name} must be an integer duration")
        if value < 0:
            raise AllureValidationError(f"{field_name} must be a non-negative integer duration")
        return value

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

    @staticmethod
    def _normalize_launch_result_status_filter(status: str | None | Literal["any"]) -> str | None | Literal["any"]:
        if status == "any":
            return "any"
        if status is None:
            return None
        if not isinstance(status, str):
            raise AllureValidationError("status filter must be a string, null, or 'any'")

        normalized = status.strip().lower()
        if not normalized:
            raise AllureValidationError("status filter cannot be empty")
        try:
            return TestStatus(normalized).value
        except ValueError as exc:
            allowed = ", ".join(status_value.value for status_value in TestStatus)
            raise AllureValidationError(
                f"Invalid status filter: {status!r}. Allowed values: {allowed}, null, any"
            ) from exc

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

    async def _create_manual_launch_result(self, result: dict[str, Any], *, index: int) -> TestResultDto:
        source_result, launch_id, test_case_id = await self._resolve_manual_result_context(result, index=index)
        result_name, result_full_name = self._resolve_manual_result_names(
            result,
            index=index,
            source_result=source_result,
        )
        status = (
            self._normalize_test_status(result.get("status"), field_name=f"results[{index}].status")
            or TestStatus.UNKNOWN
        )
        start = self._normalize_timestamp(result.get("start"), field_name=f"results[{index}].start")
        stop = self._normalize_timestamp(result.get("stop"), field_name=f"results[{index}].stop")
        self._validate_time_window(start=start, stop=stop, field_prefix=f"results[{index}]")

        try:
            created = await self._client.create_test_result(
                TestResultCreateV2Dto(
                    launch_id=launch_id,
                    test_case_id=test_case_id,
                    name=result_name,
                    full_name=result_full_name,
                    status=status,
                    manual=True,
                    external=False,
                    start=start,
                    stop=stop,
                    duration=self._resolve_duration(
                        start=start,
                        stop=stop,
                        value=result.get("duration"),
                        field_name=f"results[{index}].duration",
                    ),
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
                )
            )
        except AllureNotFoundError as exc:
            raise AllureNotFoundError(
                f"Result context for results[{index}] no longer exists",
                status_code=exc.status_code,
                response_body=exc.response_body,
            ) from exc

        created_id = created.id
        if not isinstance(created_id, int) or created_id <= 0:
            raise AllureAPIError("Created manual result is missing an ID")

        scenario = self._build_manual_result_scenario_patch(result, index=index)
        if scenario is not None:
            created = await self._client.patch_test_result(
                created_id,
                TestResultPatchDto(
                    name=result_name,
                    full_name=result_full_name,
                    scenario=scenario,
                ),
            )

        return created

    async def _resolve_manual_launch_result(self, result: dict[str, Any], *, index: int) -> TestResultRowDto:
        if not isinstance(result, dict):
            raise AllureValidationError(f"results[{index}] must be a dictionary")

        raw_result_id = result.get("result_id")
        self._validate_positive_id(raw_result_id, f"results[{index}].result_id")
        result_id = cast(int, raw_result_id)
        source_result = await self._get_test_result_or_raise(result_id)
        if source_result.manual is not True:
            raise AllureValidationError(
                f"results[{index}].result_id must reference a manual launch result to resolve in place"
            )

        try:
            return await self._client.resolve_test_result(
                result_id,
                self._build_manual_result_resolve_payload(result, index=index),
            )
        except AllureNotFoundError as exc:
            raise AllureNotFoundError(
                f"Result context for results[{index}] no longer exists",
                status_code=exc.status_code,
                response_body=exc.response_body,
            ) from exc

    async def _resolve_manual_result_context(
        self,
        result: dict[str, Any],
        *,
        index: int,
    ) -> tuple[TestResultDto | None, int, int]:
        if not isinstance(result, dict):
            raise AllureValidationError(f"results[{index}] must be a dictionary")

        raw_result_id = result.get("result_id")
        if raw_result_id is not None:
            self._validate_positive_id(raw_result_id, f"results[{index}].result_id")
            source_result = await self._get_test_result_or_raise(raw_result_id)
            launch_id = source_result.launch_id
            test_case_id = source_result.test_case_id
            if not isinstance(launch_id, int) or launch_id <= 0:
                raise AllureAPIError(f"Result ID {raw_result_id} is missing launch context")
            if not isinstance(test_case_id, int) or test_case_id <= 0:
                raise AllureAPIError(f"Result ID {raw_result_id} is missing test-case context")
            return source_result, launch_id, test_case_id

        launch_id = result.get("launch_id")
        test_case_id = result.get("test_case_id")
        if launch_id is None:
            raise AllureValidationError(
                f"results[{index}].result_id is required for launch-managed manual submission "
                "unless launch_id is provided explicitly"
            )
        if test_case_id is None:
            raise AllureValidationError(f"results[{index}].test_case_id is required")
        self._validate_positive_id(launch_id, f"results[{index}].launch_id")
        self._validate_positive_id(test_case_id, f"results[{index}].test_case_id")
        return None, launch_id, test_case_id

    def _resolve_manual_result_names(
        self,
        result: dict[str, Any],
        *,
        index: int,
        source_result: TestResultDto | None,
    ) -> tuple[str, str]:
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
        default_name = source_result.name if source_result is not None else None
        default_full_name = source_result.full_name if source_result is not None else None

        resolved_name = result_name or default_name or result_full_name or default_full_name
        resolved_full_name = result_full_name or default_full_name or resolved_name
        if resolved_name is None or resolved_full_name is None:
            raise AllureValidationError(
                f"results[{index}].name or results[{index}].full_name is required when result context "
                "cannot provide identity"
            )
        return resolved_name, resolved_full_name

    def _build_manual_result_scenario_patch(
        self,
        result: dict[str, Any],
        *,
        index: int,
    ) -> TestResultScenarioDto | None:
        raw_steps = result.get("steps")
        if raw_steps is None:
            return None
        if not isinstance(raw_steps, list):
            raise AllureValidationError(f"results[{index}].steps must be a list")

        return TestResultScenarioDto(
            steps=[
                self._build_manual_result_patch_step(step, result_index=index, step_index=step_index)
                for step_index, step in enumerate(raw_steps)
            ]
        )

    def _build_manual_result_patch_step(
        self,
        step: dict[str, Any],
        *,
        result_index: int,
        step_index: int,
    ) -> TestResultScenarioStepDto:
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

        nested_steps = step.get("steps")
        patch_nested_steps = None
        if nested_steps is not None:
            if not isinstance(nested_steps, list):
                raise AllureValidationError(f"results[{result_index}].steps[{step_index}].steps must be a list")
            patch_nested_steps = [
                self._build_manual_result_patch_step(
                    child,
                    result_index=result_index,
                    step_index=child_index,
                )
                for child_index, child in enumerate(nested_steps)
            ]

        name = self._normalize_text(
            step.get("name"),
            field_name=f"results[{result_index}].steps[{step_index}].name",
            allow_empty=True,
        )
        message = self._normalize_text(
            step.get("message"),
            field_name=f"results[{result_index}].steps[{step_index}].message",
            allow_empty=True,
        )
        trace = self._normalize_text(
            step.get("trace"),
            field_name=f"results[{result_index}].steps[{step_index}].trace",
            allow_empty=True,
        )
        status = self._normalize_test_status(
            step.get("status"),
            field_name=f"results[{result_index}].steps[{step_index}].status",
        )

        if normalized_type == "body":
            body_text = self._normalize_text(
                step.get("body"),
                field_name=f"results[{result_index}].steps[{step_index}].body",
                allow_empty=True,
            )
            return TestResultScenarioStepDto(
                name=name or body_text,
                message=message,
                trace=trace,
                start=start,
                stop=stop,
                status=status,
                steps=patch_nested_steps,
            )

        if normalized_type == "expected":
            body_text = self._normalize_text(
                step.get("body"),
                field_name=f"results[{result_index}].steps[{step_index}].body",
                allow_empty=True,
            )
            return TestResultScenarioStepDto(
                name=name or "Expected Result",
                expected_result=body_text,
                message=message,
                start=start,
                stop=stop,
                status=status,
                steps=patch_nested_steps,
            )

        if normalized_type == "attachment":
            attachment_meta = step.get("attachment")
            if not isinstance(attachment_meta, dict):
                raise AllureValidationError(
                    f"results[{result_index}].steps[{step_index}].attachment is required for attachment steps"
                )
            attachment_name = self._normalize_text(
                attachment_meta.get("name"),
                field_name=f"results[{result_index}].steps[{step_index}].attachment.name",
            )
            return TestResultScenarioStepDto(
                name=name or attachment_name,
                message=message,
                start=start,
                stop=stop,
                status=status,
                steps=patch_nested_steps,
            )

        raise AllureValidationError(
            f"results[{result_index}].steps[{step_index}].type must be one of: body, expected, attachment"
        )

    def _build_manual_result_resolve_payload(
        self,
        result: dict[str, Any],
        *,
        index: int,
    ) -> dict[str, object]:
        status = (
            self._normalize_test_status(result.get("status"), field_name=f"results[{index}].status")
            or TestStatus.UNKNOWN
        )
        start = self._normalize_timestamp(result.get("start"), field_name=f"results[{index}].start")
        stop = self._normalize_timestamp(result.get("stop"), field_name=f"results[{index}].stop")
        self._validate_time_window(start=start, stop=stop, field_prefix=f"results[{index}]")
        duration = self._resolve_duration(
            start=start,
            stop=stop,
            value=result.get("duration"),
            field_name=f"results[{index}].duration",
        )

        payload: dict[str, object] = {
            "status": status.value,
        }
        if start is not None:
            payload["start"] = start
        if stop is not None:
            payload["stop"] = stop
        if duration is not None:
            payload["duration"] = duration

        message = self._normalize_text(
            result.get("message"),
            field_name=f"results[{index}].message",
            allow_empty=True,
        )
        if message is not None:
            payload["message"] = message

        trace = self._normalize_text(
            result.get("trace"),
            field_name=f"results[{index}].trace",
            allow_empty=True,
        )
        if trace is not None:
            payload["trace"] = trace

        execution = self._build_manual_result_execution_payload(
            result,
            index=index,
            status=status,
            start=start,
            stop=stop,
            duration=duration,
        )
        if execution is not None:
            payload["execution"] = execution

        return payload

    def _build_manual_result_execution_payload(
        self,
        result: dict[str, Any],
        *,
        index: int,
        status: TestStatus,
        start: int | None,
        stop: int | None,
        duration: int | None,
    ) -> dict[str, object] | None:
        raw_steps = result.get("steps")
        if raw_steps is None:
            return None
        if not isinstance(raw_steps, list):
            raise AllureValidationError(f"results[{index}].steps must be a list")

        execution: dict[str, object] = {
            "status": status.value,
            "steps": [
                self._build_manual_result_resolve_step(step, result_index=index, step_index=step_index)
                for step_index, step in enumerate(raw_steps)
            ],
        }
        if start is not None:
            execution["start"] = start
        if stop is not None:
            execution["stop"] = stop
        if duration is not None:
            execution["duration"] = duration
        return execution

    def _build_manual_result_resolve_step(
        self,
        step: dict[str, Any],
        *,
        result_index: int,
        step_index: int,
    ) -> dict[str, object]:
        if not isinstance(step, dict):
            raise AllureValidationError(f"results[{result_index}].steps[{step_index}] must be a dictionary")

        normalized_type = self._normalize_manual_resolve_step_type(
            result_index=result_index,
            step_index=step_index,
            step=step,
        )
        payload = self._build_manual_result_resolve_step_payload(step, result_index=result_index, step_index=step_index)
        name = self._normalize_text(
            step.get("name"),
            field_name=f"results[{result_index}].steps[{step_index}].name",
            allow_empty=True,
        )

        if normalized_type == "body":
            return self._apply_manual_result_resolve_body_step(
                payload,
                step=step,
                result_index=result_index,
                step_index=step_index,
                name=name,
            )
        if normalized_type == "expected":
            return self._apply_manual_result_resolve_expected_step(
                payload,
                step=step,
                result_index=result_index,
                step_index=step_index,
                name=name,
            )
        if normalized_type == "attachment":
            return self._apply_manual_result_resolve_attachment_step(
                payload,
                step=step,
                result_index=result_index,
                step_index=step_index,
                name=name,
            )

        raise AllureValidationError(
            f"results[{result_index}].steps[{step_index}].type must be one of: body, expected, attachment"
        )

    def _normalize_manual_resolve_step_type(
        self,
        *,
        result_index: int,
        step_index: int,
        step: dict[str, Any],
    ) -> str:
        raw_type = step.get("type")
        if not isinstance(raw_type, str):
            raise AllureValidationError(f"results[{result_index}].steps[{step_index}].type is required")
        return raw_type.strip().lower()

    def _build_manual_result_resolve_step_payload(
        self,
        step: dict[str, Any],
        *,
        result_index: int,
        step_index: int,
    ) -> dict[str, object]:
        field_prefix = f"results[{result_index}].steps[{step_index}]"
        start = self._normalize_timestamp(step.get("start"), field_name=f"{field_prefix}.start")
        stop = self._normalize_timestamp(step.get("stop"), field_name=f"{field_prefix}.stop")
        self._validate_time_window(start=start, stop=stop, field_prefix=field_prefix)
        duration = self._resolve_duration(
            start=start,
            stop=stop,
            value=step.get("duration"),
            field_name=f"{field_prefix}.duration",
        )
        status = self._normalize_test_status(step.get("status"), field_name=f"{field_prefix}.status")

        payload: dict[str, object] = {}
        if start is not None:
            payload["start"] = start
        if stop is not None:
            payload["stop"] = stop
        if duration is not None:
            payload["duration"] = duration
        if status is not None:
            payload["status"] = status.value

        message = self._normalize_text(step.get("message"), field_name=f"{field_prefix}.message", allow_empty=True)
        if message is not None:
            payload["message"] = message

        trace = self._normalize_text(step.get("trace"), field_name=f"{field_prefix}.trace", allow_empty=True)
        if trace is not None:
            payload["trace"] = trace

        payload.update(
            self._build_manual_result_resolve_nested_steps(
                step,
                result_index=result_index,
                step_index=step_index,
            )
        )
        return payload

    def _build_manual_result_resolve_nested_steps(
        self,
        step: dict[str, Any],
        *,
        result_index: int,
        step_index: int,
    ) -> dict[str, object]:
        nested_steps = step.get("steps")
        if nested_steps is None:
            return {}
        if not isinstance(nested_steps, list):
            raise AllureValidationError(f"results[{result_index}].steps[{step_index}].steps must be a list")
        return {
            "steps": [
                self._build_manual_result_resolve_step(
                    child,
                    result_index=result_index,
                    step_index=child_index,
                )
                for child_index, child in enumerate(nested_steps)
            ]
        }

    def _apply_manual_result_resolve_body_step(
        self,
        payload: dict[str, object],
        *,
        step: dict[str, Any],
        result_index: int,
        step_index: int,
        name: str | None,
    ) -> dict[str, object]:
        body_text = self._normalize_text(
            step.get("body"),
            field_name=f"results[{result_index}].steps[{step_index}].body",
            allow_empty=True,
        )
        payload["type"] = "body"
        if body_text is not None:
            payload["body"] = body_text
        if name is not None:
            payload["name"] = name
        return payload

    def _apply_manual_result_resolve_expected_step(
        self,
        payload: dict[str, object],
        *,
        step: dict[str, Any],
        result_index: int,
        step_index: int,
        name: str | None,
    ) -> dict[str, object]:
        body_text = self._normalize_text(
            step.get("body"),
            field_name=f"results[{result_index}].steps[{step_index}].body",
            allow_empty=True,
        )
        payload["type"] = "expected_body"
        if body_text is not None:
            payload["body"] = body_text
        if name is not None:
            payload["name"] = name
        return payload

    def _apply_manual_result_resolve_attachment_step(
        self,
        payload: dict[str, object],
        *,
        step: dict[str, Any],
        result_index: int,
        step_index: int,
        name: str | None,
    ) -> dict[str, object]:
        attachment_meta = step.get("attachment")
        if not isinstance(attachment_meta, dict):
            raise AllureValidationError(
                f"results[{result_index}].steps[{step_index}].attachment is required for attachment steps"
            )
        attachment_name = self._normalize_text(
            attachment_meta.get("name"),
            field_name=f"results[{result_index}].steps[{step_index}].attachment.name",
        )
        content_type = self._normalize_text(
            attachment_meta.get("content_type"),
            field_name=f"results[{result_index}].steps[{step_index}].attachment.content_type",
            allow_empty=True,
        )
        payload["type"] = "attachment"
        payload["attachment"] = {
            "entity": "test_result",
            "name": attachment_name,
            **({"contentType": content_type} if content_type is not None else {}),
        }
        if name is not None:
            payload["name"] = name
        return payload

    def _build_upload_test_result(self, result: dict[str, Any], *, index: int) -> UploadTestResultDto:
        if not isinstance(result, dict):
            raise AllureValidationError(f"results[{index}] must be a dictionary")
        self._reject_unsupported_launch_upload_identity_fields(result, index=index)

        test_case_id = result.get("test_case_id")
        if test_case_id is None:
            raise AllureValidationError(f"results[{index}].test_case_id is required")
        self._validate_positive_id(test_case_id, f"results[{index}].test_case_id")
        result_name, result_full_name = self._resolve_upload_result_identity(
            result, index=index, test_case_id=test_case_id
        )

        start = self._normalize_timestamp(result.get("start"), field_name=f"results[{index}].start")
        stop = self._normalize_timestamp(result.get("stop"), field_name=f"results[{index}].stop")
        self._validate_time_window(start=start, stop=stop, field_prefix=f"results[{index}]")
        status = self._normalize_status(result.get("status"), field_name=f"results[{index}].status")
        if status is None:
            raise AllureValidationError(f"results[{index}].status is required")

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
                status=status,
                start=start,
                stop=stop,
                duration=self._resolve_duration(
                    start=start,
                    stop=stop,
                    value=result.get("duration"),
                    field_name=f"results[{index}].duration",
                ),
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
        test_case_id: int,
    ) -> tuple[str, str]:
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
        resolved_name = result_name or result_full_name or f"Test case {test_case_id}"
        resolved_full_name = result_full_name or resolved_name

        return resolved_name, resolved_full_name

    @staticmethod
    def _reject_unsupported_launch_upload_identity_fields(result: dict[str, Any], *, index: int) -> None:
        for field_name in ("uuid", "history_id"):
            if field_name in result:
                raise AllureValidationError(f"results[{index}].{field_name} is not supported for launch uploads")

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

    async def _build_manual_step_attachment_patch_scenario(
        self,
        *,
        test_result: TestResultDto,
        attachment_row: TestResultAttachmentRowDto,
        attachment_id: int | None,
        step_name: str | None,
        step_index: int | None,
    ) -> TestResultScenarioDto:
        steps = await self._build_patchable_manual_result_steps(test_result)
        target_step = self._select_manual_patch_step(
            steps,
            test_result_id=test_result.id or 0,
            attachment_id=attachment_id,
            step_name=step_name,
            step_index=step_index,
        )
        current_attachments = list(target_step.attachments or [])
        current_attachments.append(TestResultAttachmentStepDtoAllOfAttachment(actual_instance=attachment_row))
        target_step.attachments = current_attachments
        return TestResultScenarioDto(steps=steps)

    async def _build_patchable_manual_result_steps(self, test_result: TestResultDto) -> list[TestResultScenarioStepDto]:
        raw_execution = await self._get_test_result_execution_raw_or_raise(test_result.id or 0, v2=True)
        raw_steps = raw_execution.get("steps")
        execution_steps = (
            [self._patch_step_from_raw_execution_step(step) for step in raw_steps if isinstance(step, dict)]
            if isinstance(raw_steps, list)
            else []
        )

        test_case_steps: list[TestResultScenarioStepDto] = []
        if isinstance(test_result.test_case_id, int) and test_result.test_case_id > 0:
            scenario = await self._get_test_case_scenario_or_raise(test_result.test_case_id)
            test_case_steps = [self._patch_step_from_test_case_step(step) for step in scenario.steps or []]

        if execution_steps and test_case_steps:
            return self._merge_patch_steps_with_template_steps(execution_steps, test_case_steps)
        if execution_steps:
            return execution_steps
        return test_case_steps

    def _select_manual_patch_step(  # noqa: C901
        self,
        steps: list[TestResultScenarioStepDto],
        *,
        test_result_id: int,
        attachment_id: int | None,
        step_name: str | None,
        step_index: int | None,
    ) -> TestResultScenarioStepDto:
        if attachment_id is not None:
            self._validate_positive_id(attachment_id, "Attachment ID")
            matches = [
                step
                for step in steps
                if any(
                    isinstance(existing.actual_instance, TestResultAttachmentRowDto)
                    and existing.actual_instance.id == attachment_id
                    for existing in step.attachments or []
                )
            ]
            if not matches:
                raise AllureNotFoundError(
                    f"Attachment step ID {attachment_id} not found in test result ID {test_result_id}"
                )
            if len(matches) > 1:
                raise AllureValidationError("Attachment step selection is ambiguous. Provide step_name or step_index.")
            return matches[0]

        if step_index is not None:
            if not isinstance(step_index, int) or step_index < 0:
                raise AllureValidationError("step_index must be a non-negative integer")
            if step_index >= len(steps):
                raise AllureValidationError(
                    f"step_index {step_index} is out of range for test result ID {test_result_id}"
                )
            return steps[step_index]

        if step_name is not None:
            normalized_step_name = self._normalize_text(step_name, field_name="step_name")
            matches = [step for step in steps if step.name == normalized_step_name]
            if not matches:
                raise AllureNotFoundError(
                    f"No step named {normalized_step_name!r} found in test result ID {test_result_id}"
                )
            if len(matches) > 1:
                raise AllureValidationError(
                    "Attachment step selection is ambiguous. Provide attachment_id or step_index."
                )
            return matches[0]

        if not steps:
            raise AllureNotFoundError(
                f"Test result ID {test_result_id} has no manual scenario steps. "
                "Submit step data first or use explicit fixture selectors."
            )
        if len(steps) > 1:
            raise AllureValidationError(
                "Attachment step selection is ambiguous. Provide attachment_id, step_name, or step_index."
            )
        return steps[0]

    @staticmethod
    def _select_uploaded_attachment_row(rows: list[TestResultAttachmentRowDto]) -> TestResultAttachmentRowDto:
        if not rows:
            raise AllureAPIError("Attachment upload completed without returning an attachment row")
        return rows[0]

    def _patch_step_from_raw_execution_step(self, step: dict[str, Any]) -> TestResultScenarioStepDto:
        nested_raw_steps = step.get("steps")
        nested_steps = (
            [self._patch_step_from_raw_execution_step(child) for child in nested_raw_steps if isinstance(child, dict)]
            if isinstance(nested_raw_steps, list)
            else None
        )
        attachments_raw = step.get("attachments")
        attachments = (
            [
                TestResultAttachmentStepDtoAllOfAttachment(
                    actual_instance=self._coerce_test_result_attachment_row(item)
                )
                for item in attachments_raw
                if isinstance(item, dict)
            ]
            if isinstance(attachments_raw, list)
            else None
        )
        return TestResultScenarioStepDto(
            name=(
                step.get("name")
                if isinstance(step.get("name"), str)
                else step.get("body")
                if isinstance(step.get("body"), str)
                else step.get("attachment", {}).get("name")
                if isinstance(step.get("attachment"), dict) and isinstance(step.get("attachment", {}).get("name"), str)
                else None
            ),
            expected_result=step.get("expectedResult") if isinstance(step.get("expectedResult"), str) else None,
            message=step.get("message") if isinstance(step.get("message"), str) else None,
            trace=step.get("trace") if isinstance(step.get("trace"), str) else None,
            start=step.get("start") if isinstance(step.get("start"), int) else None,
            stop=step.get("stop") if isinstance(step.get("stop"), int) else None,
            status=self._normalize_test_status(step.get("status"), field_name="execution.step.status"),
            steps=nested_steps,
            attachments=attachments,
        )

    def _patch_step_from_test_case_step(self, step: SharedStepScenarioDtoStepsInner) -> TestResultScenarioStepDto:
        actual = step.actual_instance
        nested_children = getattr(actual, "steps", None)
        nested_steps = (
            [
                self._patch_step_from_test_case_step(child)
                for child in nested_children
                if isinstance(child, SharedStepScenarioDtoStepsInner)
            ]
            if isinstance(nested_children, list)
            else None
        )

        name = None
        expected_result = None
        if actual is not None:
            body = getattr(actual, "body", None)
            name = body if isinstance(body, str) and body.strip() else getattr(actual, "name", None)
            expected = getattr(actual, "expected_result", None)
            expected_result = expected if isinstance(expected, str) and expected.strip() else None

        return TestResultScenarioStepDto(
            name=name if isinstance(name, str) and name.strip() else None,
            expected_result=expected_result,
            steps=nested_steps,
        )

    def _merge_patch_steps_with_template_steps(
        self,
        runtime_steps: list[TestResultScenarioStepDto],
        template_steps: list[TestResultScenarioStepDto],
    ) -> list[TestResultScenarioStepDto]:
        merged: list[TestResultScenarioStepDto] = []
        for index, runtime_step in enumerate(runtime_steps):
            template_step = template_steps[index] if index < len(template_steps) else None
            merged.append(self._merge_patch_step_with_template_step(runtime_step, template_step))

        if len(template_steps) > len(runtime_steps):
            merged.extend(template_steps[len(runtime_steps) :])
        return merged

    def _merge_patch_step_with_template_step(
        self,
        runtime_step: TestResultScenarioStepDto,
        template_step: TestResultScenarioStepDto | None,
    ) -> TestResultScenarioStepDto:
        if template_step is None:
            return runtime_step

        runtime_nested = runtime_step.steps or []
        template_nested = template_step.steps or []
        merged_nested = self._merge_patch_steps_with_template_steps(runtime_nested, template_nested)

        return TestResultScenarioStepDto(
            attachments=runtime_step.attachments,
            expected_result=runtime_step.expected_result or template_step.expected_result,
            message=runtime_step.message,
            name=runtime_step.name or template_step.name,
            start=runtime_step.start,
            status=runtime_step.status,
            steps=merged_nested or None,
            stop=runtime_step.stop,
            trace=runtime_step.trace,
        )

    @staticmethod
    def _coerce_test_result_attachment_row(data: dict[str, Any]) -> TestResultAttachmentRowDto:
        normalized = dict(data)
        entity = normalized.get("entity")
        if not isinstance(entity, str) or not entity.strip():
            normalized["entity"] = "test_result"
        return TestResultAttachmentRowDto.model_validate(normalized)

    async def _resolve_manual_step_attachment_target(
        self,
        *,
        test_result_id: int,
        attachment_id: int | None,
        step_name: str | None,
        step_index: int | None,
    ) -> _ResolvedManualStepAttachmentTarget:
        execution = await self._get_test_result_execution_or_raise(test_result_id)
        steps = execution.steps or []
        attachment_steps = self._collect_manual_step_attachment_targets(steps)

        if attachment_id is not None:
            return self._resolve_manual_step_attachment_by_id(
                test_result_id=test_result_id,
                attachment_steps=attachment_steps,
                attachment_id=attachment_id,
            )

        if step_index is not None:
            return self._resolve_manual_step_attachment_by_index(
                test_result_id=test_result_id,
                steps=steps,
                step_index=step_index,
            )

        if step_name is not None:
            return self._resolve_manual_step_attachment_by_name(
                test_result_id=test_result_id,
                attachment_steps=attachment_steps,
                step_name=step_name,
            )

        return self._resolve_manual_step_attachment_without_selector(
            test_result_id=test_result_id,
            attachment_steps=attachment_steps,
        )

    def _resolve_manual_step_attachment_by_id(
        self,
        *,
        test_result_id: int,
        attachment_steps: list[_ResolvedManualStepAttachmentTarget],
        attachment_id: int,
    ) -> _ResolvedManualStepAttachmentTarget:
        self._validate_positive_id(attachment_id, "Attachment ID")
        for target in attachment_steps:
            if target.attachment_id == attachment_id:
                return target
        raise AllureNotFoundError(f"Attachment step ID {attachment_id} not found in test result ID {test_result_id}")

    def _resolve_manual_step_attachment_by_index(
        self,
        *,
        test_result_id: int,
        steps: list[TestResultScenarioV2DtoStepsInner],
        step_index: int,
    ) -> _ResolvedManualStepAttachmentTarget:
        if not isinstance(step_index, int) or step_index < 0:
            raise AllureValidationError("step_index must be a non-negative integer")
        if step_index >= len(steps):
            raise AllureValidationError(f"step_index {step_index} is out of range for test result ID {test_result_id}")

        selected_target = self._manual_step_attachment_target_from_step(steps[step_index], step_index=step_index)
        if selected_target is None:
            raise AllureValidationError(
                f"Step at index {step_index} is not an attachment step in test result ID {test_result_id}"
            )
        return selected_target

    def _resolve_manual_step_attachment_by_name(
        self,
        *,
        test_result_id: int,
        attachment_steps: list[_ResolvedManualStepAttachmentTarget],
        step_name: str,
    ) -> _ResolvedManualStepAttachmentTarget:
        normalized_step_name = self._normalize_text(step_name, field_name="step_name")
        matches = [target for target in attachment_steps if target.name == normalized_step_name]
        if not matches:
            raise AllureNotFoundError(
                f"No attachment step named {normalized_step_name!r} found in test result ID {test_result_id}"
            )
        if len(matches) > 1:
            raise AllureValidationError("Attachment step selection is ambiguous. Provide attachment_id or step_index.")
        return matches[0]

    @staticmethod
    def _resolve_manual_step_attachment_without_selector(
        *,
        test_result_id: int,
        attachment_steps: list[_ResolvedManualStepAttachmentTarget],
    ) -> _ResolvedManualStepAttachmentTarget:
        if not attachment_steps:
            raise AllureNotFoundError(
                f"Test result ID {test_result_id} has no attachment steps. "
                "Submit a manual result with an attachment step or use explicit fixture selectors."
            )
        if len(attachment_steps) > 1:
            raise AllureValidationError(
                "Attachment step selection is ambiguous. Provide attachment_id, step_name, or step_index."
            )
        return attachment_steps[0]

    @staticmethod
    def _collect_manual_step_attachment_targets(
        steps: list[TestResultScenarioV2DtoStepsInner],
    ) -> list[_ResolvedManualStepAttachmentTarget]:
        targets: list[_ResolvedManualStepAttachmentTarget] = []
        for index, step in enumerate(steps):
            target = LaunchService._manual_step_attachment_target_from_step(step, step_index=index)
            if target is not None:
                targets.append(target)
        return targets

    @staticmethod
    def _manual_step_attachment_target_from_step(
        step: TestResultScenarioV2DtoStepsInner,
        *,
        step_index: int,
    ) -> _ResolvedManualStepAttachmentTarget | None:
        actual_step = step.actual_instance
        if not isinstance(actual_step, TestResultAttachmentStepDto):
            return None

        attachment_id = actual_step.attachment_id
        if not isinstance(attachment_id, int) or attachment_id <= 0:
            return None

        attachment_name = None
        attachment = actual_step.attachment.actual_instance if actual_step.attachment is not None else None
        if attachment is not None:
            name = getattr(attachment, "name", None)
            attachment_name = name if isinstance(name, str) and name.strip() else None

        return _ResolvedManualStepAttachmentTarget(
            attachment_id=attachment_id,
            step_index=step_index,
            name=attachment_name,
        )

    async def _get_test_result_fixtures_or_raise(self, test_result_id: int) -> list[TestFixtureResultV2Dto]:
        try:
            return await self._client.get_test_result_fixtures(test_result_id)
        except AllureNotFoundError as exc:
            raise AllureNotFoundError(
                f"Test result ID {test_result_id} not found",
                status_code=exc.status_code,
                response_body=exc.response_body,
            ) from exc

    async def _get_test_result_or_raise(self, test_result_id: int) -> TestResultDto:
        try:
            return await self._client.get_test_result(test_result_id)
        except AllureNotFoundError as exc:
            raise AllureNotFoundError(
                f"Test result ID {test_result_id} not found",
                status_code=exc.status_code,
                response_body=exc.response_body,
            ) from exc

    async def _get_test_result_execution_or_raise(self, test_result_id: int) -> TestResultScenarioV2Dto:
        try:
            return await self._client.get_test_result_execution(test_result_id)
        except AllureNotFoundError as exc:
            raise AllureNotFoundError(
                f"Test result ID {test_result_id} not found",
                status_code=exc.status_code,
                response_body=exc.response_body,
            ) from exc

    async def _get_test_result_execution_raw_or_raise(
        self,
        test_result_id: int,
        *,
        v2: bool = False,
    ) -> dict[str, object]:
        try:
            return await self._client.get_test_result_execution_raw(test_result_id, v2=v2)
        except AllureNotFoundError as exc:
            raise AllureNotFoundError(
                f"Test result ID {test_result_id} not found",
                status_code=exc.status_code,
                response_body=exc.response_body,
            ) from exc

    async def _get_test_case_scenario_or_raise(self, test_case_id: int) -> TestCaseScenarioV2Dto:
        try:
            return await self._client.get_test_case_scenario(test_case_id)
        except AllureNotFoundError as exc:
            raise AllureNotFoundError(
                f"Test case ID {test_case_id} not found",
                status_code=exc.status_code,
                response_body=exc.response_body,
            ) from exc

    async def _prepare_attachment_file(self, attachment: dict[str, str]) -> tuple[str, bytes]:
        name, _content_type = self._normalize_attachment_metadata(attachment)

        content = await self._retrieve_attachment_content(attachment)
        if len(content) > MAX_ATTACHMENT_SIZE:
            raise AllureValidationError(
                f"Attachment size {len(content)} bytes exceeds limit of {MAX_ATTACHMENT_SIZE} bytes"
            )

        return (name, content)

    @staticmethod
    def _normalize_attachment_metadata(attachment: dict[str, str]) -> tuple[str, str]:
        if not isinstance(attachment, dict):
            raise AllureValidationError("attachment must be a dictionary")

        name = LaunchService._normalize_text(attachment.get("name"), field_name="attachment.name")
        content_type = LaunchService._normalize_text(
            attachment.get("content_type"),
            field_name="attachment.content_type",
        )
        if name is None:
            raise AllureValidationError("attachment.name is required")
        if content_type is None:
            raise AllureValidationError("attachment.content_type is required")
        if content_type not in ALLOWED_MIME_TYPES:
            raise AllureValidationError(f"Content-Type '{content_type}' is not allowed or supported.")

        return name, content_type

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
