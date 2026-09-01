"""Async HTTP client for Allure TestOps API.

This module provides a high-level wrapper around the auto-generated Allure TestOps
client, adding features like token management, automatic refresh, and
standardized error handling.
"""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import AsyncIterator, Awaitable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from dataclasses import dataclass
from typing import Literal, TypeAlias, TypeVar, cast, overload

import httpx
from pydantic import Field, SecretStr

from src.utils.auth_resolution import resolve_auth_settings
from src.utils.logger import get_logger

from .exceptions import (
    AllureAPIError,
    AllureAuthError,
    AllureNotFoundError,
    AllureRateLimitError,
    AllureValidationError,
    TestCaseNotFoundError,
)
from .generated.api.custom_field_controller_api import CustomFieldControllerApi
from .generated.api.custom_field_project_controller_api import CustomFieldProjectControllerApi
from .generated.api.custom_field_project_controller_v2_api import CustomFieldProjectControllerV2Api
from .generated.api.custom_field_value_controller_api import CustomFieldValueControllerApi
from .generated.api.custom_field_value_project_controller_api import CustomFieldValueProjectControllerApi
from .generated.api.integration_controller_api import IntegrationControllerApi
from .generated.api.launch_controller_api import LaunchControllerApi
from .generated.api.launch_search_controller_api import LaunchSearchControllerApi
from .generated.api.project_controller_api import ProjectControllerApi
from .generated.api.shared_step_attachment_controller_api import SharedStepAttachmentControllerApi
from .generated.api.shared_step_controller_api import SharedStepControllerApi
from .generated.api.shared_step_scenario_controller_api import SharedStepScenarioControllerApi
from .generated.api.test_case_attachment_controller_api import TestCaseAttachmentControllerApi
from .generated.api.test_case_controller_api import TestCaseControllerApi
from .generated.api.test_case_overview_controller_api import TestCaseOverviewControllerApi
from .generated.api.test_case_scenario_controller_api import TestCaseScenarioControllerApi
from .generated.api.test_case_search_controller_api import TestCaseSearchControllerApi
from .generated.api.test_case_tree_bulk_controller_v2_api import TestCaseTreeBulkControllerV2Api
from .generated.api.test_case_tree_controller_v2_api import TestCaseTreeControllerV2Api
from .generated.api.test_fixture_result_attachment_controller_api import TestFixtureResultAttachmentControllerApi
from .generated.api.test_layer_controller_api import TestLayerControllerApi
from .generated.api.test_layer_schema_controller_api import TestLayerSchemaControllerApi
from .generated.api.test_result_attachment_controller_api import TestResultAttachmentControllerApi
from .generated.api.test_result_bulk_controller_api import TestResultBulkControllerApi
from .generated.api.test_result_controller_api import TestResultControllerApi
from .generated.api.test_result_custom_field_controller_api import TestResultCustomFieldControllerApi
from .generated.api.test_result_defect_controller_api import TestResultDefectControllerApi
from .generated.api.test_result_env_var_controller_api import TestResultEnvVarControllerApi
from .generated.api.test_result_fixture_controller_api import TestResultFixtureControllerApi
from .generated.api.test_result_flat_controller_api import TestResultFlatControllerApi
from .generated.api.test_result_issue_controller_api import TestResultIssueControllerApi
from .generated.api.test_result_members_controller_api import TestResultMembersControllerApi
from .generated.api.test_result_rerun_controller_api import TestResultRerunControllerApi
from .generated.api.test_result_run_controller_api import TestResultRunControllerApi
from .generated.api.test_result_test_key_controller_api import TestResultTestKeyControllerApi
from .generated.api.test_result_tree_controller_v2_api import TestResultTreeControllerV2Api
from .generated.api.tree_controller_v2_api import TreeControllerV2Api
from .generated.api.upload_controller_api import UploadControllerApi
from .generated.api.upload_test_result_controller_api import UploadTestResultControllerApi
from .generated.api_client import ApiClient
from .generated.configuration import Configuration
from .generated.exceptions import ApiException
from .generated.models.aql_validate_response_dto import AqlValidateResponseDto
from .generated.models.attachment_step_dto import AttachmentStepDto
from .generated.models.body_step_dto import BodyStepDto
from .generated.models.custom_field_project_dto import CustomFieldProjectDto
from .generated.models.custom_field_project_with_values_dto import CustomFieldProjectWithValuesDto
from .generated.models.custom_field_value_dto import CustomFieldValueDto
from .generated.models.custom_field_value_project_create_dto import CustomFieldValueProjectCreateDto
from .generated.models.custom_field_value_project_patch_dto import CustomFieldValueProjectPatchDto
from .generated.models.custom_field_value_with_cf_dto import CustomFieldValueWithCfDto
from .generated.models.custom_field_with_values_dto import CustomFieldWithValuesDto
from .generated.models.env_var_value_dto import EnvVarValueDto
from .generated.models.external_run_response_dto import ExternalRunResponseDto
from .generated.models.external_run_start_request_dto import ExternalRunStartRequestDto
from .generated.models.find_all29200_response import FindAll29200Response
from .generated.models.id_and_name_only_dto import IdAndNameOnlyDto
from .generated.models.integration_dto import IntegrationDto
from .generated.models.issue_dto import IssueDto
from .generated.models.launch_create_dto import LaunchCreateDto
from .generated.models.launch_dto import LaunchDto
from .generated.models.launch_existing_upload_dto import LaunchExistingUploadDto
from .generated.models.launch_preview_dto import LaunchPreviewDto
from .generated.models.launch_upload_response_dto import LaunchUploadResponseDto
from .generated.models.manual_session_request_dto import ManualSessionRequestDto
from .generated.models.member_dto import MemberDto
from .generated.models.normalized_scenario_dto import NormalizedScenarioDto
from .generated.models.normalized_scenario_dto_attachments_value import NormalizedScenarioDtoAttachmentsValue
from .generated.models.page_custom_field_value_with_tc_count_dto import PageCustomFieldValueWithTcCountDto
from .generated.models.page_defect_row_dto import PageDefectRowDto
from .generated.models.page_id_and_name_only_dto import PageIdAndNameOnlyDto
from .generated.models.page_launch_dto import PageLaunchDto
from .generated.models.page_launch_preview_dto import PageLaunchPreviewDto
from .generated.models.page_shared_step_dto import PageSharedStepDto
from .generated.models.page_test_case_attachment_row_dto import PageTestCaseAttachmentRowDto
from .generated.models.page_test_case_dto import PageTestCaseDto
from .generated.models.page_test_case_row_dto import PageTestCaseRowDto
from .generated.models.page_test_case_tree_node_dto import PageTestCaseTreeNodeDto
from .generated.models.page_test_case_tree_node_dto_content_inner import PageTestCaseTreeNodeDtoContentInner
from .generated.models.page_test_fixture_result_attachment_row_dto import PageTestFixtureResultAttachmentRowDto
from .generated.models.page_test_result_attachment_row_dto import PageTestResultAttachmentRowDto
from .generated.models.page_test_result_flat_dto import PageTestResultFlatDto
from .generated.models.page_test_result_history_dto import PageTestResultHistoryDto
from .generated.models.page_tree_dto_v2 import PageTreeDtoV2
from .generated.models.project_test_case_count_dto import ProjectTestCaseCountDto
from .generated.models.resolve_request_v2_dto import ResolveRequestV2Dto
from .generated.models.scenario_step_create_dto import ScenarioStepCreateDto
from .generated.models.scenario_step_created_response_dto import ScenarioStepCreatedResponseDto
from .generated.models.scenario_step_patch_dto import ScenarioStepPatchDto
from .generated.models.shared_step_attachment_row_dto import SharedStepAttachmentRowDto
from .generated.models.shared_step_create_dto import SharedStepCreateDto
from .generated.models.shared_step_dto import SharedStepDto
from .generated.models.shared_step_patch_dto import SharedStepPatchDto
from .generated.models.shared_step_scenario_dto_steps_inner import SharedStepScenarioDtoStepsInner
from .generated.models.shared_step_step_dto import SharedStepStepDto
from .generated.models.test_case_attachment_row_dto import TestCaseAttachmentRowDto
from .generated.models.test_case_bulk_drag_and_drop_dto_v2 import TestCaseBulkDragAndDropDtoV2
from .generated.models.test_case_create_v2_dto import TestCaseCreateV2Dto
from .generated.models.test_case_dto import TestCaseDto
from .generated.models.test_case_full_tree_node_dto import TestCaseFullTreeNodeDto
from .generated.models.test_case_light_tree_node_dto import TestCaseLightTreeNodeDto
from .generated.models.test_case_overview_dto import TestCaseOverviewDto
from .generated.models.test_case_patch_v2_dto import TestCasePatchV2Dto
from .generated.models.test_case_row_dto import TestCaseRowDto
from .generated.models.test_case_scenario_dto import TestCaseScenarioDto
from .generated.models.test_case_scenario_v2_dto import TestCaseScenarioV2Dto
from .generated.models.test_case_tree_group_add_dto import TestCaseTreeGroupAddDto
from .generated.models.test_case_tree_group_rename_dto import TestCaseTreeGroupRenameDto
from .generated.models.test_case_tree_leaf_add_dto import TestCaseTreeLeafAddDto
from .generated.models.test_case_tree_leaf_dto_v2 import TestCaseTreeLeafDtoV2
from .generated.models.test_case_tree_leaf_rename_dto import TestCaseTreeLeafRenameDto
from .generated.models.test_case_tree_selection_dto_v2 import TestCaseTreeSelectionDtoV2

# Shared step attachments with entity field
from .generated.models.test_fixture_result_attachment_row_dto import (
    TestFixtureResultAttachmentRowDto,
)
from .generated.models.test_fixture_result_v2_dto import TestFixtureResultV2Dto
from .generated.models.test_key_dto import TestKeyDto
from .generated.models.test_result_attachment_patch_dto import TestResultAttachmentPatchDto
from .generated.models.test_result_attachment_row_dto import TestResultAttachmentRowDto
from .generated.models.test_result_bulk_rerun_dto import TestResultBulkRerunDto
from .generated.models.test_result_create_v2_dto import TestResultCreateV2Dto
from .generated.models.test_result_dto import TestResultDto
from .generated.models.test_result_flat_dto import TestResultFlatDto
from .generated.models.test_result_patch_dto import TestResultPatchDto
from .generated.models.test_result_rerun_dto import TestResultRerunDto
from .generated.models.test_result_row_dto import TestResultRowDto
from .generated.models.test_result_scenario_v2_dto import TestResultScenarioV2Dto
from .generated.models.test_session_response_dto import TestSessionResponseDto
from .generated.models.tree_dto_v2 import TreeDtoV2
from .generated.models.upload_fixtures_results_dto import UploadFixturesResultsDto
from .generated.models.upload_results_dto import UploadResultsDto
from .generated.models.upload_results_response_dto import UploadResultsResponseDto
from .generated.rest import RESTResponse
from .overridden.test_case_custom_fields_v2 import TestCaseCustomFieldV2ControllerApi


# Subclasses to add missing fields to generated models
class TestCaseDtoWithCF(TestCaseDto):
    """Subclass to support custom_fields and issues access."""

    custom_fields: list[CustomFieldValueWithCfDto] | None = None
    issues: list[IssueDto] | None = None


TestCaseDtoWithCF.model_rebuild()


class BodyStepDtoWithSteps(BodyStepDto):
    """Subclass to support nested steps and id."""

    steps: list[SharedStepScenarioDtoStepsInner] | None = None
    id: int | None = None


class StepWithExpected(BodyStepDto):
    """Subclass to support expected results and nested steps."""

    expected_result: str | None = Field(default=None, alias="expectedResult")
    steps: list[SharedStepScenarioDtoStepsInner] | None = None
    id: int | None = None


@dataclass(frozen=True)
class LaunchDetailResponse:
    """Exact-ID launch data, retaining base metadata and rich detail fields."""

    base: LaunchDto
    preview: LaunchPreviewDto


@dataclass(frozen=True)
class LaunchResultTreeNode:
    """Client-owned projection of one V2 launch result-tree node.

    The generated oneOf model is ambiguous.  Keeping the raw-response parsing
    and its discriminator handling here prevents raw upstream dictionaries
    from crossing the client boundary.
    """

    id: int | None
    name: str | None
    type: Literal["GROUP", "LEAF"]
    custom_field_id: int | None = None
    statistic: tuple[object, ...] | None = None
    assignee: str | None = None
    created_date: int | None = None
    duration: int | None = None
    flaky: bool | None = None
    hidden: bool | None = None
    last_modified_date: int | None = None
    layer_name: str | None = None
    manual: bool | None = None
    start: int | None = None
    status: str | None = None
    stop: int | None = None
    test_case_id: int | None = None
    tested_by: str | None = None


@dataclass(frozen=True)
class LaunchResultTreePage:
    """Typed V2 hierarchy page with only pagination metadata used by collectors."""

    content: tuple[LaunchResultTreeNode, ...]
    last: bool | None = None
    number: int | None = None
    total_pages: int | None = None


@dataclass(frozen=True)
class AttachmentContent:
    """Authenticated attachment bytes with response metadata for local delivery."""

    data: bytes
    filename: str
    content_type: str


@dataclass(frozen=True)
class AttachmentContentStream:
    """Authenticated attachment response metadata and an async byte stream."""

    response: httpx.Response
    filename: str
    content_type: str
    content_length: int | None

    def iter_bytes(self) -> AsyncIterator[bytes]:
        """Yield the response body without materializing it in memory."""
        return self.response.aiter_bytes()


class AttachmentStepDtoWithName(AttachmentStepDto):
    """Subclass to support name attribute and id."""

    name: str | None = None
    id: int | None = None


class SharedStepStepDtoWithId(SharedStepStepDto):
    """Subclass to support id attribute."""

    id: int | None = None


logger = get_logger(__name__)

T = TypeVar("T")

ApiType: TypeAlias = (
    TestCaseControllerApi
    | SharedStepControllerApi
    | SharedStepAttachmentControllerApi
    | TestCaseAttachmentControllerApi
    | TestCaseScenarioControllerApi
    | SharedStepScenarioControllerApi
    | TestCaseOverviewControllerApi
    | TestCaseSearchControllerApi
    | TestCaseCustomFieldV2ControllerApi
    | CustomFieldControllerApi
    | CustomFieldProjectControllerApi
    | CustomFieldProjectControllerV2Api
    | CustomFieldValueControllerApi
    | CustomFieldValueProjectControllerApi
    | TestLayerControllerApi
    | TestLayerSchemaControllerApi
    | LaunchControllerApi
    | LaunchSearchControllerApi
    | TestResultAttachmentControllerApi
    | TestResultControllerApi
    | TestResultCustomFieldControllerApi
    | TestResultDefectControllerApi
    | TestResultEnvVarControllerApi
    | TestResultBulkControllerApi
    | TestResultFixtureControllerApi
    | TestResultFlatControllerApi
    | TestResultTreeControllerV2Api
    | TestResultIssueControllerApi
    | TestResultMembersControllerApi
    | TestResultRerunControllerApi
    | TestResultRunControllerApi
    | TestResultTestKeyControllerApi
    | TestFixtureResultAttachmentControllerApi
    | TreeControllerV2Api
    | TestCaseTreeControllerV2Api
    | TestCaseTreeBulkControllerV2Api
    | IntegrationControllerApi
    | ProjectControllerApi
    | UploadControllerApi
    | UploadTestResultControllerApi
)

NormalizedScenarioDict: TypeAlias = dict[str, object]

ScenarioStepsMap: TypeAlias = dict[str, dict[str, object]]

AttachmentsMap: TypeAlias = dict[str, dict[str, object]]

# Export models for convenience
__all__ = [
    "AllureClient",
    "AttachmentContent",
    "AttachmentContentStream",
    "AttachmentStepDtoWithName",
    "BodyStepDtoWithSteps",
    "CustomFieldProjectWithValuesDto",
    "CustomFieldWithValuesDto",
    "FindAll29200Response",
    "LaunchCreateDto",
    "LaunchDto",
    "LaunchResultTreeNode",
    "LaunchResultTreePage",
    "LaunchUploadResponseDto",
    "PageLaunchDto",
    "PageLaunchPreviewDto",
    "PageSharedStepDto",
    "PageTestCaseDto",
    "PageTestCaseRowDto",
    "PageTestResultFlatDto",
    "ScenarioStepCreateDto",
    "ScenarioStepCreatedResponseDto",
    "ScenarioStepPatchDto",
    "SharedStepAttachmentRowDto",
    "SharedStepCreateDto",
    "SharedStepDto",
    "SharedStepPatchDto",
    "SharedStepScenarioDtoStepsInner",
    "SharedStepStepDtoWithId",
    "StepWithExpected",
    "TestCaseAttachmentRowDto",
    "TestCaseCreateV2Dto",
    "TestCaseDto",
    "TestCaseDtoWithCF",
    "TestCaseOverviewDto",
    "TestCasePatchV2Dto",
    "TestCaseRowDto",
    "TestCaseScenarioDto",
    "TestCaseScenarioV2Dto",
    "TestCaseTreeSelectionDtoV2",
    "TestFixtureResultV2Dto",
    "TestResultDto",
    "TestResultFlatDto",
]


class AllureClient:
    """Async client for Allure TestOps API.

    This client manages a session with the Allure TestOps API, handling
    initial Bearer token exchange and automatic background renewal
    before expiry.

    Example:
        ```python
        from pydantic import SecretStr
        from src.client import AllureClient

        async with AllureClient(
            base_url="https://demo.testops.cloud",
            token=SecretStr("your-api-token"),
            project=0
        ) as client:
            # client is initialized and authenticated
            pass
        ```
    """

    def __init__(
        self,
        base_url: str,
        token: SecretStr,
        project: int,
        timeout: float = 30.0,
    ) -> None:
        """Initialize AllureClient.

        Args:
            base_url: Allure TestOps instance base URL
            token: API token (will be exchanged for JWT Bearer token)
            project: Target Allure TestOps project ID
            timeout: Request timeout in seconds (default: 30.0)
        """
        if not base_url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid base_url scheme: {base_url}. Must start with http:// or https://")

        self._base_url = base_url.rstrip("/")
        self._token = token
        self._project = project
        self._timeout = timeout
        self._jwt_token: str | None = None
        self._token_expires_at: float | None = None
        self._csrf_token: str | None = None

        # Generated client components
        self._api_client: ApiClient | None = None
        self._test_case_api: TestCaseControllerApi | None = None
        self._shared_step_api: SharedStepControllerApi | None = None
        self._shared_step_attachment_api: SharedStepAttachmentControllerApi | None = None
        self._attachment_api: TestCaseAttachmentControllerApi | None = None
        self._scenario_api: TestCaseScenarioControllerApi | None = None
        self._shared_step_scenario_api: SharedStepScenarioControllerApi | None = None
        self._overview_api: TestCaseOverviewControllerApi
        self._search_api: TestCaseSearchControllerApi | None = None
        self._test_case_custom_field_api: TestCaseCustomFieldV2ControllerApi | None = None
        self._custom_field_api: CustomFieldControllerApi | None = None
        self._custom_field_project_api: CustomFieldProjectControllerApi | None = None
        self._custom_field_project_v2_api: CustomFieldProjectControllerV2Api | None = None
        self._custom_field_value_api: CustomFieldValueControllerApi | None = None
        self._custom_field_value_project_api: CustomFieldValueProjectControllerApi | None = None
        self._test_layer_api: TestLayerControllerApi | None = None
        self._test_layer_schema_api: TestLayerSchemaControllerApi | None = None
        self._launch_api: LaunchControllerApi | None = None
        self._launch_search_api: LaunchSearchControllerApi | None = None
        self._test_result_attachment_api: TestResultAttachmentControllerApi | None = None
        self._test_result_api: TestResultControllerApi | None = None
        self._test_result_custom_field_api: TestResultCustomFieldControllerApi | None = None
        self._test_result_defect_api: TestResultDefectControllerApi | None = None
        self._test_result_env_var_api: TestResultEnvVarControllerApi | None = None
        self._test_result_bulk_api: TestResultBulkControllerApi | None = None
        self._test_result_fixture_api: TestResultFixtureControllerApi | None = None
        self._test_result_flat_api: TestResultFlatControllerApi | None = None
        self._test_result_tree_api: TestResultTreeControllerV2Api | None = None
        self._test_result_issue_api: TestResultIssueControllerApi | None = None
        self._test_result_members_api: TestResultMembersControllerApi | None = None
        self._test_result_rerun_api: TestResultRerunControllerApi | None = None
        self._test_result_run_api: TestResultRunControllerApi | None = None
        self._test_result_test_key_api: TestResultTestKeyControllerApi | None = None
        self._test_fixture_result_attachment_api: TestFixtureResultAttachmentControllerApi | None = None
        self._tree_api: TreeControllerV2Api | None = None
        self._test_case_tree_api: TestCaseTreeControllerV2Api | None = None
        self._test_case_tree_bulk_api: TestCaseTreeBulkControllerV2Api | None = None
        self._integration_api: IntegrationControllerApi | None = None
        self._project_api: ProjectControllerApi | None = None
        self._upload_api: UploadControllerApi | None = None
        self._upload_test_result_api: UploadTestResultControllerApi | None = None
        self._is_entered = False

    @classmethod
    def from_env(
        cls, project: int | None = None, timeout: float = 30.0, *, require_project: bool = True
    ) -> AllureClient:
        """Initialize AllureClient from environment variables.

        Expects:
            ALLURE_ENDPOINT: The base URL of the Allure TestOps instance.
            ALLURE_API_TOKEN: The API token for authentication.
            ALLURE_PROJECT_ID: The target project ID, unless ``require_project`` is false.

        Args:
            project: Optional target Allure TestOps project ID to override the one from environment variables.
            timeout: Request timeout in seconds (default: 30.0)
            require_project: Whether a default project ID is required. Set to
                ``False`` only for global discovery endpoints that do not use
                project context.

        Returns:
            An initialized AllureClient instance.

        Raises:
            KeyError: If required environment variables are missing.
            ValueError: If settings validation fails.
        """
        resolved = resolve_auth_settings(project_id=project, include_project_id=require_project)

        if not resolved.api_token:
            raise KeyError("ALLURE_API_TOKEN is not set in environment or config")
        if not resolved.endpoint:
            raise KeyError("ALLURE_ENDPOINT is not set in environment or config")
        if require_project and (not isinstance(resolved.project_id, int) or resolved.project_id <= 0):
            raise ValueError("Project ID is required and must be positive")

        return cls(
            base_url=resolved.endpoint,
            token=resolved.api_token,
            project=resolved.project_id or 0,
            timeout=timeout,
        )

    def set_project(self, project: int) -> None:
        self._project = project

    def get_project(self) -> int:
        return self._project

    def get_base_url(self) -> str:
        return self._base_url

    async def _get_jwt_token(self) -> str:
        """Exchange API token for a JWT Bearer token.

        Uses a one-off httpx request to the auth endpoint since the
        generated client is designed for use after authentication.

        Returns:
            The raw JWT access token string.

        Raises:
            AllureAuthError: If the token exchange fails due to invalid credentials.
            AllureAPIError: If a connection or system error occurs.
        """
        # We use a temporary httpx client for the initial token exchange
        # because the generated client expects a valid access token.
        async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout) as temp_client:
            try:
                response = await temp_client.post(
                    "/api/uaa/oauth/token",
                    data={
                        "grant_type": "apitoken",
                        "scope": "openid",
                        "token": self._token.get_secret_value(),
                    },
                    headers={"Accept": "application/json"},
                    timeout=self._timeout * 2,
                )
                response.raise_for_status()
                data = response.json()
                access_token: str = data["access_token"]
                expires_in: int = data.get("expires_in", 3600)

                self._jwt_token = access_token
                # Refresh 60 seconds before expiry
                self._token_expires_at = time.time() + expires_in - 60

                # Capture CSRF token if present (standard Spring Security/Angular convention)
                self._csrf_token = response.cookies.get("XSRF-TOKEN")

                return access_token
            except httpx.HTTPStatusError as e:
                raise AllureAuthError(
                    f"Token exchange failed: {e.response.text}",
                    status_code=e.response.status_code,
                    response_body=e.response.text,
                ) from e
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                raise AllureAuthError(
                    "Token exchange failed: invalid response",
                    status_code=response.status_code,
                    response_body=response.text,
                ) from e
            except httpx.RequestError as e:
                raise AllureAPIError(f"Token exchange request error: {e}") from e

    async def _ensure_valid_token(self) -> None:
        """Ensure the session has a valid JWT token.

        Checks the token expiration and triggers a refresh if it's missing
        or about to expire (within 60 seconds). Also initializes or updates
        the internal ApiClient and controllers.
        """
        if self._token_expires_at is None or time.time() >= self._token_expires_at:
            new_token = await self._get_jwt_token()

            # Initialize or update ApiClient
            if self._api_client is None:
                config = Configuration(host=self._base_url, access_token=new_token, retries=3)
                self._api_client = ApiClient(configuration=config)
                # Set custom timeout on the underlying REST client if possible
                # The generated client typically uses default timeout or per-request
            else:
                self._api_client.configuration.access_token = new_token

            if self._api_client:
                # Ensure Authorization header is set as generated client might not pick it up automatically
                self._api_client.default_headers["Authorization"] = f"Bearer {new_token}"

            # Inject CSRF token if available
            if self._csrf_token and self._api_client:
                # Cookie for standard session checks
                self._api_client.cookie = f"XSRF-TOKEN={self._csrf_token}"
                # Header for CSRF protection
                self._api_client.default_headers["X-XSRF-TOKEN"] = self._csrf_token

            # Re-initialize controllers
            self._test_case_api = TestCaseControllerApi(self._api_client)
            self._shared_step_api = SharedStepControllerApi(self._api_client)
            self._shared_step_attachment_api = SharedStepAttachmentControllerApi(self._api_client)
            self._attachment_api = TestCaseAttachmentControllerApi(self._api_client)
            self._scenario_api = TestCaseScenarioControllerApi(self._api_client)
            self._shared_step_scenario_api = SharedStepScenarioControllerApi(self._api_client)
            self._overview_api = TestCaseOverviewControllerApi(self._api_client)
            self._search_api = TestCaseSearchControllerApi(self._api_client)
            self._test_case_custom_field_api = TestCaseCustomFieldV2ControllerApi(self._api_client)
            self._custom_field_api = CustomFieldControllerApi(self._api_client)
            self._custom_field_project_api = CustomFieldProjectControllerApi(self._api_client)
            self._custom_field_project_v2_api = CustomFieldProjectControllerV2Api(self._api_client)
            self._custom_field_value_api = CustomFieldValueControllerApi(self._api_client)
            self._custom_field_value_project_api = CustomFieldValueProjectControllerApi(self._api_client)
            self._test_layer_api = TestLayerControllerApi(self._api_client)
            self._test_layer_schema_api = TestLayerSchemaControllerApi(self._api_client)
            self._launch_api = LaunchControllerApi(self._api_client)
            self._launch_search_api = LaunchSearchControllerApi(self._api_client)
            self._test_result_attachment_api = TestResultAttachmentControllerApi(self._api_client)
            self._test_result_api = TestResultControllerApi(self._api_client)
            self._test_result_custom_field_api = TestResultCustomFieldControllerApi(self._api_client)
            self._test_result_defect_api = TestResultDefectControllerApi(self._api_client)
            self._test_result_env_var_api = TestResultEnvVarControllerApi(self._api_client)
            self._test_result_bulk_api = TestResultBulkControllerApi(self._api_client)
            self._test_result_fixture_api = TestResultFixtureControllerApi(self._api_client)
            self._test_result_flat_api = TestResultFlatControllerApi(self._api_client)
            self._test_result_tree_api = TestResultTreeControllerV2Api(self._api_client)
            self._test_result_issue_api = TestResultIssueControllerApi(self._api_client)
            self._test_result_members_api = TestResultMembersControllerApi(self._api_client)
            self._test_result_rerun_api = TestResultRerunControllerApi(self._api_client)
            self._test_result_run_api = TestResultRunControllerApi(self._api_client)
            self._test_result_test_key_api = TestResultTestKeyControllerApi(self._api_client)
            self._test_fixture_result_attachment_api = TestFixtureResultAttachmentControllerApi(self._api_client)
            self._tree_api = TreeControllerV2Api(self._api_client)
            self._test_case_tree_api = TestCaseTreeControllerV2Api(self._api_client)
            self._test_case_tree_bulk_api = TestCaseTreeBulkControllerV2Api(self._api_client)
            self._integration_api = IntegrationControllerApi(self._api_client)
            self._project_api = ProjectControllerApi(self._api_client)
            self._upload_api = UploadControllerApi(self._api_client)
            self._upload_test_result_api = UploadTestResultControllerApi(self._api_client)

    @property
    def api_client(self) -> ApiClient:
        """Get the underlying ApiClient instance.

        Raises:
            RuntimeError: If the client has not been initialized (entered with).
        """
        if self._api_client is None:
            raise RuntimeError("AllureClient must be used as an async context manager")
        return self._api_client

    async def get_integrations(self) -> list[IntegrationDto]:
        """Fetch all integrations."""
        # Ensure we have a valid client
        if self._integration_api is None:
            raise RuntimeError("AllureClient must be used as an async context manager")

        try:
            # Fetch first page with reasonable size
            page = await self._integration_api.get_integrations(page=0, size=100)
            return page.content or []
        except Exception:
            # Log warning or re-raise depending on strictness.
            # For now return empty list to act as fallback.
            return []

    async def get_project_available_integrations(self, project_id: int) -> list[IntegrationDto]:
        """Fetch integrations available for a specific project."""
        if self._integration_api is None:
            raise RuntimeError("AllureClient must be used as an async context manager")

        try:
            page = await self._integration_api.get_project_available_integrations(
                project_id=project_id,
                page=0,
                size=100,
            )
            return page.content or []
        except Exception:
            return []

    async def validate_project_access(self, project_id: int | None = None) -> None:
        """Verify that the authenticated token can access the target project."""
        target_project = project_id if project_id is not None else self._project
        project_api = await self._get_api("_project_api", error_name="project_api")
        await self._call_api(project_api.calculate_stats(id=target_project))

    async def __aenter__(self) -> AllureClient:
        """Initialize the client session within an async context.

        Performs token exchange and prepares all generated API controllers.

        Returns:
            Self (authenticated and ready to use).
        """
        await self._ensure_valid_token()
        if self._api_client:
            # Generate client's __aenter__ is untyped
            await self._api_client.__aenter__()  # type: ignore[no-untyped-call]
        self._is_entered = True
        return self

    async def __aexit__(self, *args: object) -> None:
        """Cleanly close the client session and underlying HTTP transport."""
        self._is_entered = False
        if self._api_client:
            # Generated client's __aexit__ is untyped
            await self._api_client.__aexit__(*args)  # type: ignore[no-untyped-call]

    def _handle_api_exception(self, e: ApiException) -> None:
        """Map generated client exceptions to lucius-mcp custom exceptions.

        Args:
            e: The raw ApiException from the generated client.

        Raises:
            AllureNotFoundError: For 404 status.
            AllureValidationError: For 400 status.
            AllureAuthError: For 401/403 status.
            AllureRateLimitError: For 429 status.
            AllureAPIError: For all other non-success statuses.
        """
        status = e.status
        body = e.body if hasattr(e, "body") else str(e)

        # Log the exception with traceback for debugging
        logger.exception("API request failed with status %s", status)

        if status == 404:
            raise AllureNotFoundError(f"Resource not found: {body}", status_code=status, response_body=body) from e
        if status == 400:
            raise AllureValidationError(f"Validation error: {body}", status_code=status, response_body=body) from e
        if status in (401, 403):
            raise AllureAuthError(f"Authentication failed: {body}", status_code=status, response_body=body) from e
        if status == 429:
            raise AllureRateLimitError("Rate limit exceeded", status_code=status, response_body=body) from e

        raise AllureAPIError(f"API request failed: {body}", status_code=status, response_body=body) from e

    def _require_entered(self) -> None:
        if not self._is_entered:
            raise AllureAPIError("Client not initialized. Use 'async with AllureClient(...)'")

    @staticmethod
    def _raise_missing_api(api_name: str) -> None:
        raise AllureAPIError(f"Internal error: {api_name} not initialized")

    @overload
    async def _get_api(
        self, attr_name: Literal["_test_case_api"], *, error_name: str | None = None
    ) -> TestCaseControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_shared_step_api"], *, error_name: str | None = None
    ) -> SharedStepControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_shared_step_attachment_api"], *, error_name: str | None = None
    ) -> SharedStepAttachmentControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_attachment_api"], *, error_name: str | None = None
    ) -> TestCaseAttachmentControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_scenario_api"], *, error_name: str | None = None
    ) -> TestCaseScenarioControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_shared_step_scenario_api"], *, error_name: str | None = None
    ) -> SharedStepScenarioControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_overview_api"], *, error_name: str | None = None
    ) -> TestCaseOverviewControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_search_api"], *, error_name: str | None = None
    ) -> TestCaseSearchControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_test_case_custom_field_api"], *, error_name: str | None = None
    ) -> TestCaseCustomFieldV2ControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_custom_field_api"], *, error_name: str | None = None
    ) -> CustomFieldControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_custom_field_project_api"], *, error_name: str | None = None
    ) -> CustomFieldProjectControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_custom_field_project_v2_api"], *, error_name: str | None = None
    ) -> CustomFieldProjectControllerV2Api: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_custom_field_value_api"], *, error_name: str | None = None
    ) -> CustomFieldValueControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_custom_field_value_project_api"], *, error_name: str | None = None
    ) -> CustomFieldValueProjectControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_launch_api"], *, error_name: str | None = None
    ) -> LaunchControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_launch_search_api"], *, error_name: str | None = None
    ) -> LaunchSearchControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_test_result_attachment_api"], *, error_name: str | None = None
    ) -> TestResultAttachmentControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_test_result_api"], *, error_name: str | None = None
    ) -> TestResultControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_test_result_custom_field_api"], *, error_name: str | None = None
    ) -> TestResultCustomFieldControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_test_result_defect_api"], *, error_name: str | None = None
    ) -> TestResultDefectControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_test_result_env_var_api"], *, error_name: str | None = None
    ) -> TestResultEnvVarControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_test_result_bulk_api"], *, error_name: str | None = None
    ) -> TestResultBulkControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_test_result_fixture_api"], *, error_name: str | None = None
    ) -> TestResultFixtureControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_test_result_flat_api"], *, error_name: str | None = None
    ) -> TestResultFlatControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_test_result_tree_api"], *, error_name: str | None = None
    ) -> TestResultTreeControllerV2Api: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_test_result_issue_api"], *, error_name: str | None = None
    ) -> TestResultIssueControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_test_result_members_api"], *, error_name: str | None = None
    ) -> TestResultMembersControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_test_result_rerun_api"], *, error_name: str | None = None
    ) -> TestResultRerunControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_test_result_run_api"], *, error_name: str | None = None
    ) -> TestResultRunControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_test_result_test_key_api"], *, error_name: str | None = None
    ) -> TestResultTestKeyControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_test_fixture_result_attachment_api"], *, error_name: str | None = None
    ) -> TestFixtureResultAttachmentControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_tree_api"], *, error_name: str | None = None
    ) -> TreeControllerV2Api: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_test_case_tree_api"], *, error_name: str | None = None
    ) -> TestCaseTreeControllerV2Api: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_test_case_tree_bulk_api"], *, error_name: str | None = None
    ) -> TestCaseTreeBulkControllerV2Api: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_project_api"], *, error_name: str | None = None
    ) -> ProjectControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_upload_api"], *, error_name: str | None = None
    ) -> UploadControllerApi: ...

    @overload
    async def _get_api(
        self, attr_name: Literal["_upload_test_result_api"], *, error_name: str | None = None
    ) -> UploadTestResultControllerApi: ...

    async def _get_api(self, attr_name: str, *, error_name: str | None = None) -> ApiType:
        self._require_entered()
        await self._ensure_valid_token()
        api = getattr(self, attr_name)
        if api is None:
            self._raise_missing_api(error_name or attr_name.lstrip("_"))
        return cast(ApiType, api)

    async def _call_api(self, coro: Awaitable[T]) -> T:
        try:
            return await coro
        except ApiException as e:
            self._handle_api_exception(e)
            raise

    async def _call_api_raw(self, coro: Awaitable[httpx.Response | RESTResponse]) -> httpx.Response | RESTResponse:
        try:
            return await coro
        except ApiException as e:
            self._handle_api_exception(e)
            raise

    @staticmethod
    def _extract_response_data(response: httpx.Response | RESTResponse) -> dict[str, object]:
        http_response = AllureClient._unwrap_http_response(response)
        if not 200 <= http_response.status_code <= 299:
            raise ApiException(
                status=http_response.status_code,
                reason=http_response.reason_phrase,
                body=http_response.text,
            )
        data = http_response.json()
        if isinstance(data, dict):
            return data
        raise ApiException(
            status=http_response.status_code,
            reason=http_response.reason_phrase,
            body=http_response.text,
        )

    @staticmethod
    def _validate_test_result_id(test_result_id: int) -> None:
        if not isinstance(test_result_id, int) or isinstance(test_result_id, bool) or test_result_id <= 0:
            raise AllureValidationError("Test Result ID must be a positive integer")

    @staticmethod
    def _validate_page_size(page: int, size: int) -> None:
        if not isinstance(page, int) or page < 0:
            raise AllureValidationError("Page must be a non-negative integer")
        if not isinstance(size, int) or size <= 0 or size > 100:
            raise AllureValidationError("Size must be between 1 and 100")

    @staticmethod
    def _unwrap_http_response(response: httpx.Response | RESTResponse) -> httpx.Response:
        return response.response if isinstance(response, RESTResponse) else response

    async def _read_attachment_content(self, coro: Awaitable[httpx.Response | RESTResponse]) -> AttachmentContent:
        """Read one authenticated attachment response while retaining safe delivery metadata."""
        response = await self._call_api_raw(coro)
        http_response = self._unwrap_http_response(response)
        if not 200 <= http_response.status_code <= 299:
            self._handle_api_exception(
                ApiException(status=http_response.status_code, reason=http_response.reason_phrase, body="")
            )
        disposition = http_response.headers.get("content-disposition", "")
        filename = "attachment"
        if "filename=" in disposition:
            filename = disposition.partition("filename=")[2].strip().strip('"') or filename
        return AttachmentContent(
            data=http_response.content,
            filename=filename,
            content_type=http_response.headers.get("content-type", "application/octet-stream"),
        )

    @asynccontextmanager
    async def _stream_attachment_content(
        self, attachment_id: int, *, resource_path: str, inline: bool = False
    ) -> AsyncIterator[AttachmentContentStream]:
        """Stream one attachment through the configured authenticated HTTP client."""
        if not isinstance(attachment_id, int) or isinstance(attachment_id, bool) or attachment_id <= 0:
            raise AllureValidationError("Attachment ID must be a positive integer")
        self._require_entered()
        await self._ensure_valid_token()
        if self._api_client is None:  # pragma: no cover - guarded by _require_entered
            raise AllureAPIError("Client not initialized. Use 'async with AllureClient(...)'")

        method, url, headers, _, _ = self._api_client.param_serialize(
            method="GET",
            resource_path=resource_path,
            path_params={"id": attachment_id},
            query_params=[("inline", inline)],
            header_params={"Accept": "*/*"},
            auth_settings=[],
        )
        rest_client = self._api_client.rest_client
        if rest_client.pool_manager is None:
            rest_client.pool_manager = rest_client._create_pool_manager()
        async with rest_client.pool_manager.stream(method, url, headers=headers, timeout=self._timeout) as response:
            if not 200 <= response.status_code <= 299:
                self._handle_api_exception(
                    ApiException(status=response.status_code, reason=response.reason_phrase, body="")
                )
            disposition = response.headers.get("content-disposition", "")
            filename = "attachment"
            if "filename=" in disposition:
                filename = disposition.partition("filename=")[2].strip().strip('"') or filename
            content_length: int | None = None
            raw_content_length = response.headers.get("content-length")
            if raw_content_length is not None:
                try:
                    content_length = int(raw_content_length)
                except ValueError:
                    pass
            yield AttachmentContentStream(
                response=response,
                filename=filename,
                content_type=response.headers.get("content-type", "application/octet-stream"),
                content_length=content_length,
            )

    @staticmethod
    def _extract_upload_result_ids(data: dict[str, object]) -> list[int]:
        result_ids = data.get("resultIds")
        if isinstance(result_ids, list):
            return [result_id for result_id in result_ids if isinstance(result_id, int)]

        results = data.get("results")
        if isinstance(results, list):
            extracted_ids: list[int] = []
            for item in results:
                if isinstance(item, dict):
                    result_id = item.get("id")
                    if isinstance(result_id, int):
                        extracted_ids.append(result_id)
            return extracted_ids

        return []

    async def _upload_multipart_files(
        self,
        *,
        method: str,
        resource_path: str,
        files: dict[str, bytes | str | tuple[str, bytes] | list[bytes | str | tuple[str, bytes]]],
        expected_status_codes: tuple[int, ...],
        accept_header: str | None = None,
    ) -> RESTResponse:
        self._require_entered()
        await self._ensure_valid_token()

        if self._api_client is None:
            raise AllureAPIError("Client not initialized. Use 'async with AllureClient(...)'")

        headers = {"Content-Type": "multipart/form-data"}
        if accept_header is not None:
            headers["Accept"] = accept_header

        request_args = self._api_client.param_serialize(
            method=method,
            resource_path=resource_path,
            header_params=headers,
            post_params=[],
            files=files,
            auth_settings=[],
        )
        call_coro = self._api_client.call_api(
            *request_args,
            _request_timeout=self._timeout,
        )
        response = await self._call_api_raw(cast(Awaitable[httpx.Response], call_coro))
        rest_response = cast(RESTResponse, response)

        if rest_response.status not in expected_status_codes:
            self._handle_api_exception(
                ApiException(
                    status=rest_response.status,
                    reason=rest_response.reason,
                    body=rest_response.response.text,
                )
            )

        return rest_response

    async def _get_test_result_execution_raw_v2(self, test_result_id: int) -> dict[str, object]:
        self._require_entered()
        await self._ensure_valid_token()

        if self._api_client is None:
            raise AllureAPIError("Client not initialized. Use 'async with AllureClient(...)'")

        request_args = self._api_client.param_serialize(
            method="GET",
            resource_path="/api/testresult/{id}/execution",
            path_params={"id": test_result_id},
            query_params=[("v2", True)],
            header_params={},
            auth_settings=[],
        )
        call_coro = self._api_client.call_api(
            *request_args,
            _request_timeout=self._timeout,
        )
        response = await self._call_api_raw(cast(Awaitable[httpx.Response], call_coro))
        return self._extract_response_data(response)

    @staticmethod
    def _patch_attachment_with_discriminator(attachment_dict: dict[str, object]) -> dict[str, object]:
        """Patch the attachment dict to ensure discriminator works.

        This handles cases where the 'entity' field might be 'TestCaseAttachmentRowDto'
        instead of 'test_case', etc.
        """
        entity = attachment_dict.get("entity")
        if not entity or not isinstance(entity, str):
            return attachment_dict

        # Map DTO class names to internal discriminator values
        mapping = {
            "TestCaseAttachmentRowDto": "test_case",
            "TestFixtureResultAttachmentRowDto": "test_fixture_result",
            "TestResultAttachmentRowDto": "test_result",
            "SharedStepAttachmentRowDto": "shared_step",
        }

        if entity in mapping:
            patched = dict(attachment_dict)
            patched["entity"] = mapping[entity]
            return patched

        return attachment_dict

    @staticmethod
    def _parse_attachment_with_discriminator(
        attachment_dict: dict[str, object],
    ) -> NormalizedScenarioDtoAttachmentsValue:
        """Parse attachment using entity field as discriminator.

        This works around the oneOf deserialization issue where all three attachment
        types match because they share the same base fields.
        """
        # Patch the dict before extraction to handle DTO class names in entity field
        attachment_dict = AllureClient._patch_attachment_with_discriminator(attachment_dict)

        entity = attachment_dict.get("entity")

        # SharedStepAttachmentRowDto doesn't have entity field, ID is direct instead of being in dict
        # If no entity field, this is likely not a normalized attachment value, skip wrapping
        if entity is None:
            # Fall back to default parsing (will likely fail but provides error detail)
            return NormalizedScenarioDtoAttachmentsValue.from_dict(attachment_dict)

        # Type for instance must cover all possible attachment types
        instance: (
            TestCaseAttachmentRowDto
            | TestFixtureResultAttachmentRowDto
            | TestResultAttachmentRowDto
            | SharedStepAttachmentRowDto
            | None
        ) = None

        if entity == "test_case":
            instance = TestCaseAttachmentRowDto.from_dict(attachment_dict)
        elif entity == "test_fixture_result":
            instance = TestFixtureResultAttachmentRowDto.from_dict(attachment_dict)
        elif entity == "test_result":
            instance = TestResultAttachmentRowDto.from_dict(attachment_dict)
        elif entity == "shared_step":
            # SharedStepAttachmentRowDto needs different handling - it's not part of the oneOf union
            # This shouldn't actually happen in practice
            instance = SharedStepAttachmentRowDto.from_dict(attachment_dict)
        else:
            # Fall back to default parsing (will likely fail but provides better error)
            return NormalizedScenarioDtoAttachmentsValue.from_dict(attachment_dict)

        if instance is None:
            raise AllureAPIError(f"Failed to parse attachment with entity={entity}")

        return NormalizedScenarioDtoAttachmentsValue(actual_instance=instance)

    @staticmethod
    def _parse_normalized_scenario_dto(data: dict[str, object]) -> NormalizedScenarioDto:
        """Custom parser for NormalizedScenarioDto that handles attachment oneOf correctly."""
        # Parse attachments using discriminator
        attachments_dict = data.get("attachments", {})
        if isinstance(attachments_dict, dict):
            parsed_attachments = {
                key: AllureClient._parse_attachment_with_discriminator(value) for key, value in attachments_dict.items()
            }
        else:
            parsed_attachments = {}

        # ⚠️ NOTE: We skip sharedStepAttachments because SharedStepAttachmentRowDto
        # doesn't use NormalizedScenarioDtoAttachmentsValue wrapper - it has a different structure
        # The OpenAPI schema is incorrect here - sharedStepAttachments should use SharedStepAttachmentRowDto directly
        # We remove it from the data dict to avoid validation errors

        # Create a modified data dict with parsed attachments
        modified_data = dict(data)
        modified_data["attachments"] = parsed_attachments
        # Remove sharedStepAttachments to bypass the invalid schema validation
        modified_data.pop("sharedStepAttachments", None)

        # Use model_validate, which will use our pre-parsed attachment objects
        return NormalizedScenarioDto.model_validate(modified_data)

    async def _create_scenario_step_via_api(
        self,
        api: TestCaseScenarioControllerApi | SharedStepScenarioControllerApi,
        step: ScenarioStepCreateDto,
        *,
        after_id: int | None = None,
        with_expected_result: bool = False,
    ) -> ScenarioStepCreatedResponseDto:
        if isinstance(api, TestCaseScenarioControllerApi):
            response = await self._call_api_raw(
                api.create15_without_preload_content(
                    scenario_step_create_dto=step,
                    after_id=after_id,
                    with_expected_result=with_expected_result,
                    _request_timeout=self._timeout,
                )
            )
        else:
            response = await self._call_api_raw(
                api.create20_without_preload_content(
                    scenario_step_create_dto=step,
                    _request_timeout=self._timeout,
                )
            )
        data = self._extract_response_data(response)

        # Custom deserialization to fix oneOf attachment issue
        if "scenario" in data and isinstance(data["scenario"], dict):
            data["scenario"] = self._parse_normalized_scenario_dto(data["scenario"])

        result = ScenarioStepCreatedResponseDto.model_validate(data)
        if result is None:
            raise AllureAPIError("Invalid response from scenario step creation")
        return result

    @overload
    async def _upload_attachment_via_api(
        self,
        api: TestCaseAttachmentControllerApi,
        *,
        test_case_id: int,
        shared_step_id: None = None,
        file_data: list[bytes | str | tuple[str, bytes]],
    ) -> list[TestCaseAttachmentRowDto]: ...

    @overload
    async def _upload_attachment_via_api(
        self,
        api: SharedStepAttachmentControllerApi,
        *,
        test_case_id: None = None,
        shared_step_id: int,
        file_data: list[bytes | str | tuple[str, bytes]],
    ) -> list[SharedStepAttachmentRowDto]: ...

    async def _upload_attachment_via_api(
        self,
        api: TestCaseAttachmentControllerApi | SharedStepAttachmentControllerApi,
        *,
        test_case_id: int | None = None,
        shared_step_id: int | None = None,
        file_data: list[bytes | str | tuple[str, bytes]],
    ) -> list[TestCaseAttachmentRowDto] | list[SharedStepAttachmentRowDto]:
        if isinstance(api, TestCaseAttachmentControllerApi):
            if test_case_id is None:
                raise AllureValidationError("test_case_id is required for test case attachment upload")
            return await self._call_api(
                api.create16(
                    test_case_id=test_case_id,
                    file=file_data,
                    _request_timeout=self._timeout,
                )
            )
        if shared_step_id is None:
            raise AllureValidationError("shared_step_id is required for shared step attachment upload")
        return await self._call_api(
            api.create21(
                shared_step_id=shared_step_id,
                file=file_data,
                _request_timeout=self._timeout,
            )
        )

    # ==========================================
    # Test Case operations
    # ==========================================

    async def create_test_case(self, data: TestCaseCreateV2Dto) -> TestCaseOverviewDto:
        """Create a new test case in the specified project.

        Args:
            data: Test case definition (name, scenario, etc.).

        Returns:
            The created test case overview.

        Raises:
            AllureNotFoundError: If project doesn't exist.
            AllureValidationError: If input data fails validation.
            AllureAuthError: If unauthorized.
            AllureAPIError: If the server returns an error.
        """
        api = await self._get_api("_test_case_api")

        # Ensure project_id is set in the body as required by the model
        if hasattr(data, "project_id") and not data.project_id:
            data.project_id = self._project
        response = await self._call_api(api.create13(test_case_create_v2_dto=data, _request_timeout=self._timeout))
        # Switch view from TestCaseDto to TestCaseOverviewDto
        # Since fields are compatible (mostly optional), we can use model_dump/validate
        return TestCaseOverviewDto.model_validate(response.model_dump())

    @staticmethod
    def _escape_rql_value(value: str) -> str:
        return value.replace("\\", "\\\\").replace('"', '\\"')

    @classmethod
    def _build_rql_filters(cls, search: str | None, status: str | None, tags: list[str] | None) -> str:
        parts: list[str] = []
        if search:
            parts.append(f'name~="{cls._escape_rql_value(search)}"')
        if status:
            parts.append(f'status="{cls._escape_rql_value(status)}"')
        if tags:
            for tag in tags:
                parts.append(f'tag="{cls._escape_rql_value(tag)}"')
        return " and ".join(parts)

    @staticmethod
    def _validate_positive_int_list(values: list[int] | None, error_message: str) -> list[int] | None:
        if values is None:
            return None

        validated: list[int] = []
        for value in values:
            if not isinstance(value, int) or value <= 0:
                raise AllureValidationError(error_message)
            validated.append(value)
        return validated

    async def list_test_cases(
        self,
        project_id: int,
        page: int = 0,
        size: int = 20,
        search: str | None = None,
        tags: list[str] | None = None,
        status: str | None = None,
    ) -> PageTestCaseDto:
        """List test cases for a project.

        Args:
            project_id: Target project ID.
            page: Zero-based page index.
            size: Page size.
            search: Optional name/description search.
            tags: Optional list of tags to filter (AQL syntax).
            status: Optional status filter for AQL query.

        Returns:
            Paginated test cases for the project.

        Raises:
            AllureNotFoundError: If project doesn't exist.
            AllureValidationError: If input data fails validation.
            AllureAuthError: If unauthorized.
            AllureAPIError: If the server returns an error.
        """
        search_api = await self._get_api("_search_api", error_name="test_case search APIs")

        if not isinstance(project_id, int) or project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")

        if not isinstance(page, int) or page < 0:
            raise AllureValidationError("Page must be a non-negative integer")
        if not isinstance(size, int) or size <= 0 or size > 100:
            raise AllureValidationError("Size must be between 1 and 100")

        rql = self._build_rql_filters(search=search, status=status, tags=tags)

        return await self._call_api(
            search_api.search1(
                project_id=project_id,
                rql=rql,
                page=page,
                size=size,
                _request_timeout=self._timeout,
            )
        )

    async def list_deleted_test_cases(
        self,
        project_id: int,
        page: int = 0,
        size: int = 20,
        sort: list[str] | None = None,
    ) -> PageTestCaseRowDto:
        """List deleted/archived test cases for a project."""
        test_case_api = await self._get_api("_test_case_api")

        if not isinstance(project_id, int) or project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")
        if not isinstance(page, int) or page < 0:
            raise AllureValidationError("Page must be a non-negative integer")
        if not isinstance(size, int) or size <= 0 or size > 100:
            raise AllureValidationError("Size must be between 1 and 100")

        return await self._call_api(
            test_case_api.find_all_deleted(
                project_id=project_id,
                page=page,
                size=size,
                sort=sort,
                _request_timeout=self._timeout,
            )
        )

    # ==========================================
    # Launch operations
    # ==========================================

    async def create_launch(self, data: LaunchCreateDto) -> LaunchDto:
        """Create a new launch in the specified project.

        Args:
            data: Launch definition (name, project_id, etc.).

        Returns:
            The created launch.

        Raises:
            AllureNotFoundError: If project doesn't exist.
            AllureValidationError: If input data fails validation.
            AllureAuthError: If unauthorized.
            AllureAPIError: If the server returns an error.
        """
        api = await self._get_api("_launch_api")

        if hasattr(data, "project_id") and not data.project_id:
            data.project_id = self._project

        return await self._call_api(api.create31(launch_create_dto=data, _request_timeout=self._timeout))

    async def list_launches(
        self,
        project_id: int,
        page: int = 0,
        size: int = 20,
        search: str | None = None,
        filter_id: int | None = None,
        sort: list[str] | None = None,
    ) -> FindAll29200Response:
        """List launches for a project.

        Args:
            project_id: Target project ID.
            page: Zero-based page index.
            size: Page size.
            search: Optional name search.
            filter_id: Optional filter ID.
            sort: Optional sort criteria.

        Returns:
            Paginated launches or launch previews.

        Raises:
            AllureNotFoundError: If project doesn't exist.
            AllureValidationError: If input data fails validation.
            AllureAuthError: If unauthorized.
            AllureAPIError: If the server returns an error.
        """
        api = await self._get_api("_launch_api", error_name="launch APIs")

        if not isinstance(project_id, int) or project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")
        if not isinstance(page, int) or page < 0:
            raise AllureValidationError("Page must be a non-negative integer")
        if not isinstance(size, int) or size <= 0 or size > 100:
            raise AllureValidationError("Size must be between 1 and 100")

        try:
            response = await self._call_api(
                api.find_all29(
                    project_id=project_id,
                    search=search,
                    filter_id=filter_id,
                    page=page,
                    size=size,
                    sort=sort,
                    _request_timeout=self._timeout,
                )
            )
            return self._normalize_launch_list(response)
        except ValueError:
            raw_response = await self._call_api_raw(
                api.find_all29_without_preload_content(
                    project_id=project_id,
                    search=search,
                    filter_id=filter_id,
                    page=page,
                    size=size,
                    sort=sort,
                    _request_timeout=self._timeout,
                )
            )
            try:
                data = self._extract_response_data(raw_response)
            except ApiException as exc:
                self._handle_api_exception(exc)
                raise
            page_data = PageLaunchDto.from_dict(data)
            if page_data is None:
                raise AllureValidationError("Unexpected launch list response from API") from None
            return FindAll29200Response(page_data)

    async def get_launch(self, launch_id: int) -> LaunchDetailResponse:
        """Retrieve a specific launch by its ID.

        Args:
            launch_id: The unique ID of the launch.

        Returns:
            Exact-ID launch data with basic metadata and rich detail fields.

        Raises:
            AllureNotFoundError: If launch doesn't exist.
            AllureValidationError: If input is invalid.
            AllureAuthError: If unauthorized.
            AllureAPIError: If the server returns an error.
        """
        api = await self._get_api("_launch_api", error_name="launch APIs")

        if not isinstance(launch_id, int) or launch_id <= 0:
            raise AllureValidationError("Launch ID must be a positive integer")

        raw_response = await self._call_api_raw(
            api.find_one23_without_preload_content(id=launch_id, _request_timeout=self._timeout)
        )
        try:
            data = self._extract_response_data(raw_response)
        except ApiException as exc:
            self._handle_api_exception(exc)
            raise

        base = LaunchDto.from_dict(data)
        if base is None:
            raise AllureValidationError("Unexpected launch detail response from API")

        preview = LaunchPreviewDto.from_dict(data)
        if preview is None:
            raise AllureValidationError("Unexpected launch detail response from API")

        await self._enrich_sparse_launch_preview(api=api, launch_id=launch_id, raw_data=data, preview=preview)
        return LaunchDetailResponse(base=base, preview=preview)

    async def get_launch_core(self, launch_id: int) -> LaunchDetailResponse:
        """Read the authoritative exact launch response without optional enrichment.

        This is intentionally separate from :meth:`get_launch`: callers that need a
        best-effort aggregate must retain a successful base response if a later
        optional endpoint fails.
        """
        api = await self._get_api("_launch_api", error_name="launch APIs")
        if not isinstance(launch_id, int) or launch_id <= 0:
            raise AllureValidationError("Launch ID must be a positive integer")
        raw_response = await self._call_api_raw(
            api.find_one23_without_preload_content(id=launch_id, _request_timeout=self._timeout)
        )
        try:
            data = self._extract_response_data(raw_response)
        except ApiException as exc:
            self._handle_api_exception(exc)
            raise
        base = LaunchDto.from_dict(data)
        preview = LaunchPreviewDto.from_dict(data)
        if base is None or preview is None:
            raise AllureValidationError("Unexpected launch detail response from API")
        return LaunchDetailResponse(base=base, preview=preview)

    async def get_launch_execution_section(
        self,
        section: str,
        launch_id: int,
        *,
        page: int | None = None,
        size: int | None = None,
        tree_id: int | None = None,
    ) -> object:
        """Read one documented launch execution surface through the generated client."""
        api = await self._get_api("_launch_api", error_name="launch APIs")
        methods = {
            "duration": "get_duration",
            "progress": "get_progress",
            "assignees": "get_assignees",
            "testers": "get_testers",
            "variables": "get_variables",
            "defects": "get_defects2",
            "member_stats": "get_member_stats",
            "muted_results": "get_muted_test_results",
            "retries": "get_retries",
            "unresolved_results": "get_unresolved_test_results",
            "tree_widget": "get_widget_tree",
            "statistic": "get_statistic",
            "environment": "get_environment",
            "jobs": "get_jobs1",
        }
        method_name = methods.get(section)
        if method_name is None:
            raise AllureValidationError(f"Unknown launch execution section: {section}")
        kwargs: dict[str, object] = {"id": launch_id, "_request_timeout": self._timeout}
        if page is not None:
            kwargs["page"] = page
        if size is not None:
            kwargs["size"] = size
        if tree_id is not None:
            kwargs["tree_id"] = tree_id
        return await self._call_api(getattr(api, method_name)(**kwargs))

    async def get_launch_result_view(
        self, section: str, launch_id: int, *, page: int | None = None, size: int | None = None
    ) -> object:
        """Read a compact launch-scoped result view without fetching result details."""
        api = await self._get_api("_test_result_api", error_name="test result APIs")
        methods = {
            "core_test_result_index": "find_all4",
            "result_defect_tree": "defects",
            "result_timeline": "timeline",
        }
        method_name = methods.get(section)
        if method_name is None:
            raise AllureValidationError(f"Unknown launch result view: {section}")
        kwargs: dict[str, object] = {"launch_id": launch_id, "_request_timeout": self._timeout}
        if page is not None:
            kwargs["page"] = page
        if size is not None:
            kwargs["size"] = size
        return await self._call_api(getattr(api, method_name)(**kwargs))

    async def get_launch_result_tree_page(
        self, launch_id: int, tree_id: int, *, path: list[int] | None, page: int, size: int
    ) -> LaunchResultTreePage:
        """Read a hierarchy page and discriminate its ambiguous oneOf nodes by ``type``.

        The generated oneOf has no discriminator mapping, so using the raw response
        here prevents that generator ambiguity from leaking into services.
        """
        api = await self._get_api("_test_result_tree_api", error_name="test result tree APIs")
        response = await self._call_api_raw(
            api.get_tree_entities_without_preload_content(
                launch_id=launch_id, tree_id=tree_id, path=path, page=page, size=size, _request_timeout=self._timeout
            )
        )
        try:
            payload = self._extract_response_data(response)
        except ApiException as exc:
            self._handle_api_exception(exc)
            raise
        content = payload.get("content") if isinstance(payload, dict) else None
        if not isinstance(payload, dict) or not isinstance(content, list):
            raise AllureValidationError("Unexpected launch result tree response from API")
        nodes: list[LaunchResultTreeNode] = []
        for node in content:
            if not isinstance(node, dict) or node.get("type") not in {"group", "GROUP", "leaf", "LEAF"}:
                raise AllureValidationError("Unexpected launch result tree node type from API")
            nodes.append(self._project_launch_result_tree_node(node))
        last = payload.get("last")
        number = payload.get("number")
        total_pages = payload.get("totalPages")
        return LaunchResultTreePage(
            content=tuple(nodes),
            last=last if isinstance(last, bool) else None,
            number=number if isinstance(number, int) else None,
            total_pages=total_pages if isinstance(total_pages, int) else None,
        )

    @staticmethod
    def _project_launch_result_tree_node(payload: dict[str, object]) -> LaunchResultTreeNode:
        """Map the raw oneOf payload into a stable client-owned hierarchy node."""

        node_type = payload["type"]
        normalized_type: Literal["GROUP", "LEAF"] = "GROUP" if node_type in {"group", "GROUP"} else "LEAF"

        def integer(name: str) -> int | None:
            value = payload.get(name)
            return value if isinstance(value, int) and not isinstance(value, bool) else None

        def text(name: str) -> str | None:
            value = payload.get(name)
            return value if isinstance(value, str) else None

        def boolean(name: str) -> bool | None:
            value = payload.get(name)
            return value if isinstance(value, bool) else None

        statistic = payload.get("statistic")
        return LaunchResultTreeNode(
            id=integer("id"),
            name=text("name"),
            type=normalized_type,
            custom_field_id=integer("customFieldId"),
            statistic=tuple(statistic) if isinstance(statistic, list) else None,
            assignee=text("assignee"),
            created_date=integer("createdDate"),
            duration=integer("duration"),
            flaky=boolean("flaky"),
            hidden=boolean("hidden"),
            last_modified_date=integer("lastModifiedDate"),
            layer_name=text("layerName"),
            manual=boolean("manual"),
            start=integer("start"),
            status=text("status"),
            stop=integer("stop"),
            test_case_id=integer("testCaseId"),
            tested_by=text("testedBy"),
        )

    async def get_launch_base(self, launch_id: int) -> LaunchDto:
        """Retrieve sparse authoritative launch metadata for lifecycle checks."""
        api = await self._get_api("_launch_api", error_name="launch APIs")
        if not isinstance(launch_id, int) or launch_id <= 0:
            raise AllureValidationError("Launch ID must be a positive integer")
        return await self._call_api(api.find_one23(id=launch_id, _request_timeout=self._timeout))

    @staticmethod
    def _normalize_launch_list(response: FindAll29200Response) -> FindAll29200Response:
        """Project ambiguous generated pages onto the stable compact list contract."""
        page = response.actual_instance
        if isinstance(page, PageLaunchDto):
            return response
        if not isinstance(page, PageLaunchPreviewDto):
            raise AllureValidationError("Unexpected launch list response from API")

        return FindAll29200Response(
            PageLaunchDto(
                content=[LaunchDto.model_validate(item.model_dump(by_alias=True)) for item in page.content or []],
                empty=page.empty,
                first=page.first,
                last=page.last,
                number=page.number,
                number_of_elements=page.number_of_elements,
                pageable=page.pageable,
                size=page.size,
                sort=page.sort,
                total_elements=page.total_elements,
                total_pages=page.total_pages,
            )
        )

    async def _enrich_sparse_launch_preview(
        self,
        *,
        api: LaunchControllerApi,
        launch_id: int,
        raw_data: dict[str, object],
        preview: LaunchPreviewDto,
    ) -> None:
        """Fill absent exact-ID detail fields from documented, bounded endpoints."""
        requests: list[tuple[str, Awaitable[object]]] = []
        if "statistic" not in raw_data:
            requests.append(("statistic", api.get_statistic(id=launch_id, _request_timeout=self._timeout)))
        if "environment" not in raw_data:
            requests.append(("environment", api.get_environment(id=launch_id, _request_timeout=self._timeout)))
        if "jobs" not in raw_data:
            requests.append(("jobs", api.get_jobs1(id=launch_id, _request_timeout=self._timeout)))

        if not requests:
            return

        results = await asyncio.gather(*(self._optional_launch_enrichment(name, request) for name, request in requests))
        for (name, _), result in zip(requests, results, strict=True):
            if name == "statistic":
                preview.statistic = result  # type: ignore[assignment]
            elif name == "environment":
                preview.environment = result  # type: ignore[assignment]
            else:
                preview.jobs = result  # type: ignore[assignment]

    async def _optional_launch_enrichment(self, endpoint: str, request: Awaitable[object]) -> object | None:
        """Return unavailable for optional 403/404 enrichment; preserve other failures."""
        try:
            return await self._call_api(request)
        except AllureNotFoundError:
            return None
        except AllureAuthError as exc:
            if exc.status_code == 403:
                return None
            raise
        except AllureAPIError as exc:
            raise AllureAPIError(
                f"Unable to enrich launch detail from {endpoint} endpoint: {exc}",
                status_code=exc.status_code,
                response_body=exc.response_body,
            ) from exc

    async def close_launch(self, launch_id: int) -> int:
        """Close a launch by its ID.

        Args:
            launch_id: The unique ID of the launch.

        Returns:
            HTTP status code from the close operation.

        Raises:
            AllureNotFoundError: If launch doesn't exist.
            AllureValidationError: If input is invalid.
            AllureAuthError: If unauthorized.
            AllureAPIError: If the server returns an error.
        """
        api = await self._get_api("_launch_api", error_name="launch APIs")

        if not isinstance(launch_id, int) or launch_id <= 0:
            raise AllureValidationError("Launch ID must be a positive integer")

        response = await self._call_api(api.close_with_http_info(id=launch_id, _request_timeout=self._timeout))
        return response.status_code

    async def reopen_launch(self, launch_id: int) -> None:
        """Reopen a launch by its ID.

        Args:
            launch_id: The unique ID of the launch.

        Raises:
            AllureNotFoundError: If launch doesn't exist.
            AllureValidationError: If input is invalid.
            AllureAuthError: If unauthorized.
            AllureAPIError: If the server returns an error.
        """
        api = await self._get_api("_launch_api", error_name="launch APIs")

        if not isinstance(launch_id, int) or launch_id <= 0:
            raise AllureValidationError("Launch ID must be a positive integer")

        await self._call_api(api.reopen(id=launch_id, _request_timeout=self._timeout))

    async def list_launch_test_results(
        self,
        launch_id: int,
        *,
        page: int = 0,
        size: int = 100,
        search: str | None = None,
        filter_id: int | None = None,
        sort: list[str] | None = None,
    ) -> PageTestResultFlatDto:
        """List launch test results using the flat launch-results endpoint."""
        api = await self._get_api("_test_result_flat_api", error_name="test result flat APIs")

        if not isinstance(launch_id, int) or launch_id <= 0:
            raise AllureValidationError("Launch ID must be a positive integer")
        if not isinstance(page, int) or page < 0:
            raise AllureValidationError("Page must be a non-negative integer")
        if not isinstance(size, int) or size <= 0 or size > 100:
            raise AllureValidationError("Size must be between 1 and 100")

        return await self._call_api(
            api.get_test_cases1(
                launch_id=launch_id,
                search=search,
                filter_id=filter_id,
                page=page,
                size=size,
                sort=sort,
                _request_timeout=self._timeout,
            )
        )

    async def get_test_result(self, test_result_id: int) -> TestResultDto:
        """Fetch one test result by ID."""
        api = await self._get_api("_test_result_api", error_name="test result APIs")

        self._validate_test_result_id(test_result_id)

        return await self._call_api(api.find_one5(id=test_result_id, _request_timeout=self._timeout))

    async def create_test_result(self, data: TestResultCreateV2Dto) -> TestResultDto:
        """Create one test result directly via the first-class test-result API."""
        api = await self._get_api("_test_result_api", error_name="test result APIs")
        return await self._call_api(api.create5(test_result_create_v2_dto=data, _request_timeout=self._timeout))

    async def patch_test_result(self, test_result_id: int, data: TestResultPatchDto) -> TestResultDto:
        """Patch one test result directly via the first-class test-result API."""
        api = await self._get_api("_test_result_api", error_name="test result APIs")

        self._validate_test_result_id(test_result_id)

        return await self._call_api(
            api.patch5(
                id=test_result_id,
                test_result_patch_dto=data,
                _request_timeout=self._timeout,
            )
        )

    async def get_test_result_execution(self, test_result_id: int) -> TestResultScenarioV2Dto:
        """Fetch execution details for one test result."""
        api = await self._get_api("_test_result_api", error_name="test result APIs")

        self._validate_test_result_id(test_result_id)

        return await self._call_api(api.find_execution(id=test_result_id, _request_timeout=self._timeout))

    async def get_test_result_execution_raw(self, test_result_id: int, *, v2: bool = False) -> dict[str, object]:
        """Fetch raw execution details for one test result without strict schema deserialization."""
        self._validate_test_result_id(test_result_id)

        if v2:
            return await self._get_test_result_execution_raw_v2(test_result_id)

        api = await self._get_api("_test_result_api", error_name="test result APIs")
        response = await self._call_api_raw(
            cast(
                Awaitable[httpx.Response],
                api.find_execution_without_preload_content(
                    id=test_result_id,
                    _request_timeout=self._timeout,
                ),
            )
        )
        return self._extract_response_data(response)

    async def get_test_result_custom_fields(self, test_result_id: int) -> list[CustomFieldWithValuesDto]:
        """Fetch custom fields with values for one exact test result."""
        api = await self._get_api("_test_result_custom_field_api", error_name="test result custom field APIs")
        self._validate_test_result_id(test_result_id)
        return await self._call_api(
            api.get_custom_fields_with_values1(test_result_id=test_result_id, _request_timeout=self._timeout)
        )

    async def get_test_result_defects(
        self, test_result_id: int, *, page: int = 0, size: int = 100, sort: list[str] | None = None
    ) -> PageDefectRowDto:
        """Fetch one page of defects linked to an exact test result."""
        api = await self._get_api("_test_result_defect_api", error_name="test result defect APIs")
        self._validate_test_result_id(test_result_id)
        self._validate_page_size(page, size)
        return await self._call_api(
            api.get_defects(
                test_result_id=test_result_id,
                page=page,
                size=size,
                sort=sort,
                _request_timeout=self._timeout,
            )
        )

    async def get_test_result_environment(self, test_result_id: int) -> list[EnvVarValueDto]:
        """Fetch environment values for one exact test result."""
        api = await self._get_api("_test_result_env_var_api", error_name="test result environment APIs")
        self._validate_test_result_id(test_result_id)
        return await self._call_api(
            api.get_env_var_values(test_result_id=test_result_id, _request_timeout=self._timeout)
        )

    async def get_test_result_issues(self, test_result_id: int) -> list[IssueDto]:
        """Fetch issues linked to one exact test result."""
        api = await self._get_api("_test_result_issue_api", error_name="test result issue APIs")
        self._validate_test_result_id(test_result_id)
        return await self._call_api(api.get_issues(test_result_id=test_result_id, _request_timeout=self._timeout))

    async def get_test_result_members(self, test_result_id: int) -> list[MemberDto]:
        """Fetch members assigned to one exact test result."""
        api = await self._get_api("_test_result_members_api", error_name="test result member APIs")
        self._validate_test_result_id(test_result_id)
        return await self._call_api(api.get_members(test_result_id=test_result_id, _request_timeout=self._timeout))

    async def get_test_result_test_keys(self, test_result_id: int) -> list[TestKeyDto]:
        """Fetch test keys linked to one exact test result."""
        api = await self._get_api("_test_result_test_key_api", error_name="test result test key APIs")
        self._validate_test_result_id(test_result_id)
        return await self._call_api(api.get_keys(test_result_id=test_result_id, _request_timeout=self._timeout))

    async def get_test_result_history(
        self, test_result_id: int, *, page: int = 0, size: int = 100, sort: list[str] | None = None
    ) -> PageTestResultHistoryDto:
        """Fetch one page of history references for an exact test result."""
        api = await self._get_api("_test_result_api", error_name="test result APIs")
        self._validate_test_result_id(test_result_id)
        self._validate_page_size(page, size)
        return await self._call_api(
            api.find_history(id=test_result_id, page=page, size=size, sort=sort, _request_timeout=self._timeout)
        )

    async def get_test_result_retries(
        self, test_result_id: int, *, page: int = 0, size: int = 100, sort: list[str] | None = None
    ) -> PageTestResultHistoryDto:
        """Fetch one page of retry references for an exact test result."""
        api = await self._get_api("_test_result_api", error_name="test result APIs")
        self._validate_test_result_id(test_result_id)
        self._validate_page_size(page, size)
        return await self._call_api(
            api.find_retries(id=test_result_id, page=page, size=size, sort=sort, _request_timeout=self._timeout)
        )

    async def read_test_result_fixture_attachment_content(self, attachment_id: int, *, inline: bool = False) -> bytes:
        """Read content for one fixture-result attachment."""
        return (await self.read_test_result_fixture_attachment(attachment_id, inline=inline)).data

    async def read_test_result_fixture_attachment(
        self, attachment_id: int, *, inline: bool = False
    ) -> AttachmentContent:
        """Read fixture attachment bytes plus trusted upstream response metadata."""
        api = await self._get_api(
            "_test_fixture_result_attachment_api", error_name="test fixture result attachment APIs"
        )
        if not isinstance(attachment_id, int) or attachment_id <= 0:
            raise AllureValidationError("Attachment ID must be a positive integer")
        return await self._read_attachment_content(
            cast(
                Awaitable[httpx.Response],
                api.read_content1_without_preload_content(
                    id=attachment_id, inline=inline, _request_timeout=self._timeout
                ),
            )
        )

    def stream_test_result_fixture_attachment(
        self, attachment_id: int, *, inline: bool = False
    ) -> AbstractAsyncContextManager[AttachmentContentStream]:
        """Stream fixture attachment content for bounded local delivery."""
        return self._stream_attachment_content(
            attachment_id,
            resource_path="/api/testfixtureresult/attachment/{id}/content",
            inline=inline,
        )

    async def resolve_test_result(
        self,
        test_result_id: int,
        data: ResolveRequestV2Dto | dict[str, object],
    ) -> TestResultRowDto:
        """Resolve an existing test result in place."""
        await self._get_api("_test_result_run_api", error_name="test result run APIs")

        self._validate_test_result_id(test_result_id)

        if self._api_client is None:
            raise AllureAPIError("Client not initialized. Use 'async with AllureClient(...)'")

        request_body = data.to_dict() if isinstance(data, ResolveRequestV2Dto) else data
        request_args = self._api_client.param_serialize(
            method="POST",
            resource_path="/api/testresult/{id}/resolve",
            path_params={"id": test_result_id},
            query_params=[("v2", True)],
            header_params={"Content-Type": "application/json"},
            body=request_body,
            auth_settings=[],
        )
        call_coro = self._api_client.call_api(
            *request_args,
            _request_timeout=self._timeout,
        )

        response = await self._call_api_raw(cast(Awaitable[httpx.Response], call_coro))
        parsed = TestResultRowDto.from_dict(self._extract_response_data(response))
        if parsed is None:  # pragma: no cover - defensive
            raise AllureAPIError("Resolve test result response was empty")
        return parsed

    async def get_test_result_fixtures(self, test_result_id: int) -> list[TestFixtureResultV2Dto]:
        """Fetch fixture results for one test result."""
        api = await self._get_api("_test_result_fixture_api", error_name="test result fixture APIs")

        self._validate_test_result_id(test_result_id)

        return await self._call_api(api.get_fixtures(test_result_id=test_result_id, _request_timeout=self._timeout))

    async def get_test_result_fixture_attachments(
        self,
        test_result_id: int,
        *,
        page: int = 0,
        size: int = 10,
        sort: list[str] | None = None,
    ) -> PageTestFixtureResultAttachmentRowDto:
        """Fetch fixture attachments for one test result."""
        api = await self._get_api("_test_result_fixture_api", error_name="test result fixture APIs")

        self._validate_test_result_id(test_result_id)
        if not isinstance(page, int) or page < 0:
            raise AllureValidationError("Page must be a non-negative integer")
        if not isinstance(size, int) or size <= 0 or size > 100:
            raise AllureValidationError("Size must be between 1 and 100")

        return await self._call_api(
            api.get_fixtures_attachments(
                test_result_id=test_result_id,
                page=page,
                size=size,
                sort=sort,
                _request_timeout=self._timeout,
            )
        )

    async def list_test_result_attachments(
        self,
        test_result_id: int,
        *,
        page: int = 0,
        size: int = 10,
        sort: list[str] | None = None,
    ) -> PageTestResultAttachmentRowDto:
        """Fetch test-result attachments for one manual result."""
        api = await self._get_api("_test_result_attachment_api", error_name="test result attachment APIs")

        if not isinstance(test_result_id, int) or test_result_id <= 0:
            raise AllureValidationError("Test Result ID must be a positive integer")
        if not isinstance(page, int) or page < 0:
            raise AllureValidationError("Page must be a non-negative integer")
        if not isinstance(size, int) or size <= 0 or size > 100:
            raise AllureValidationError("Size must be between 1 and 100")

        response = await self._call_api_raw(
            cast(
                Awaitable[httpx.Response],
                api.find_all5_without_preload_content(
                    test_result_id=test_result_id,
                    page=page,
                    size=size,
                    sort=sort,
                    _request_timeout=self._timeout,
                ),
            )
        )
        try:
            return self._parse_test_result_attachment_page(self._extract_response_data(response))
        except ApiException as exc:
            self._handle_api_exception(exc)
            raise

    async def patch_test_result_attachment(
        self,
        attachment_id: int,
        data: TestResultAttachmentPatchDto,
    ) -> TestResultAttachmentRowDto:
        """Patch test-result attachment metadata."""
        api = await self._get_api("_test_result_attachment_api", error_name="test result attachment APIs")

        if not isinstance(attachment_id, int) or attachment_id <= 0:
            raise AllureValidationError("Attachment ID must be a positive integer")

        return await self._call_api(
            api.patch6(
                id=attachment_id,
                test_result_attachment_patch_dto=data,
                _request_timeout=self._timeout,
            )
        )

    async def read_test_result_attachment_content(self, attachment_id: int, *, inline: bool = False) -> bytes:
        """Read stored content for one test-result attachment."""
        return (await self.read_test_result_attachment(attachment_id, inline=inline)).data

    async def read_test_result_attachment(self, attachment_id: int, *, inline: bool = False) -> AttachmentContent:
        """Read result attachment bytes plus trusted upstream response metadata."""
        api = await self._get_api("_test_result_attachment_api", error_name="test result attachment APIs")

        if not isinstance(attachment_id, int) or attachment_id <= 0:
            raise AllureValidationError("Attachment ID must be a positive integer")

        return await self._read_attachment_content(
            cast(
                Awaitable[httpx.Response],
                api.read_content_without_preload_content(
                    id=attachment_id,
                    inline=inline,
                    _request_timeout=self._timeout,
                ),
            )
        )

    def stream_test_result_attachment(
        self, attachment_id: int, *, inline: bool = False
    ) -> AbstractAsyncContextManager[AttachmentContentStream]:
        """Stream result attachment content for bounded local delivery."""
        return self._stream_attachment_content(
            attachment_id,
            resource_path="/api/testresult/attachment/{id}/content",
            inline=inline,
        )

    async def rerun_test_results_bulk(self, data: TestResultBulkRerunDto) -> None:
        """Schedule manual reruns for selected test results."""
        api = await self._get_api("_test_result_bulk_api", error_name="test result bulk APIs")
        await self._call_api(api.rerun(test_result_bulk_rerun_dto=data, _request_timeout=self._timeout))

    async def rerun_test_result(self, test_result_id: int, data: TestResultRerunDto) -> IdAndNameOnlyDto:
        """Schedule a manual rerun for one test result."""
        api = await self._get_api("_test_result_rerun_api", error_name="test result rerun APIs")

        if not isinstance(test_result_id, int) or test_result_id <= 0:
            raise AllureValidationError("Test Result ID must be a positive integer")

        return await self._call_api(
            api.retry(
                test_result_id=test_result_id,
                test_result_rerun_dto=data,
                _request_timeout=self._timeout,
            )
        )

    async def start_manual_test_session(self, data: ManualSessionRequestDto) -> TestSessionResponseDto:
        """Start a manual test session for a launch."""
        api = await self._get_api("_upload_api", error_name="upload APIs")
        return await self._call_api(
            api.session_job_run(
                manual_session_request_dto=data,
                _request_timeout=self._timeout,
            )
        )

    async def start_external_run(self, data: ExternalRunStartRequestDto) -> ExternalRunResponseDto:
        """Register an external run used to bootstrap manual sessions."""
        api = await self._get_api("_upload_api", error_name="upload APIs")
        return await self._call_api(
            api.start(
                external_run_start_request_dto=data,
                _request_timeout=self._timeout,
            )
        )

    async def submit_manual_test_results(self, data: UploadResultsDto) -> UploadResultsResponseDto:
        """Submit manual test results for an existing manual session."""
        api = await self._get_api("_upload_test_result_api", error_name="upload test result APIs")
        response = await self._call_api_raw(
            cast(
                Awaitable[httpx.Response],
                api.upload_test_results_without_preload_content(
                    upload_results_dto=data,
                    _request_timeout=self._timeout,
                ),
            )
        )
        payload = self._extract_response_data(response)
        return UploadResultsResponseDto(result_ids=self._extract_upload_result_ids(payload))

    async def upload_test_fixture_results(
        self,
        test_result_id: int,
        data: UploadFixturesResultsDto,
    ) -> UploadResultsResponseDto:
        """Create or update fixture results under a test result."""
        api = await self._get_api("_upload_test_result_api", error_name="upload test result APIs")

        if not isinstance(test_result_id, int) or test_result_id <= 0:
            raise AllureValidationError("Test Result ID must be a positive integer")

        response = await self._call_api_raw(
            cast(
                Awaitable[httpx.Response],
                api.upload_test_fixture_results_without_preload_content(
                    id=test_result_id,
                    upload_fixtures_results_dto=data,
                    _request_timeout=self._timeout,
                ),
            )
        )
        payload = self._extract_response_data(response)
        return UploadResultsResponseDto(result_ids=self._extract_upload_result_ids(payload))

    async def create_test_result_attachments(
        self,
        test_result_id: int,
        files: list[bytes | str | tuple[str, bytes]],
    ) -> list[TestResultAttachmentRowDto]:
        """Upload attachments directly to a concrete test result."""
        api = await self._get_api("_test_result_attachment_api", error_name="test result attachment APIs")

        if not isinstance(test_result_id, int) or test_result_id <= 0:
            raise AllureValidationError("Test Result ID must be a positive integer")
        if not isinstance(files, list) or not files:
            raise AllureValidationError("files must be a non-empty list")

        attachments = await self._call_api(
            api.create6(
                test_result_id=test_result_id,
                file=files,
                _request_timeout=self._timeout,
            )
        )
        return [
            self._build_test_result_attachment_row(attachment.to_dict() if hasattr(attachment, "to_dict") else {})
            for attachment in attachments
        ]

    async def add_test_result_attachment(
        self,
        test_result_id: int,
        files: list[bytes | str | tuple[str, bytes]],
    ) -> int:
        """Upload attachments to a test result."""
        if not isinstance(test_result_id, int) or test_result_id <= 0:
            raise AllureValidationError("Test Result ID must be a positive integer")
        if not isinstance(files, list) or not files:
            raise AllureValidationError("files must be a non-empty list")

        response = await self._upload_multipart_files(
            method="POST",
            resource_path=f"/api/upload/test-result/{test_result_id}/attachment",
            files={"file": files},
            expected_status_codes=(200, 202),
        )
        return int(response.status)

    @staticmethod
    def _build_test_result_attachment_row(data: dict[str, object]) -> TestResultAttachmentRowDto:
        normalized = dict(data)
        if not isinstance(normalized.get("entity"), str) or not str(normalized["entity"]).strip():
            normalized["entity"] = "test_result"
        return TestResultAttachmentRowDto.model_validate(normalized)

    @staticmethod
    def _build_test_case_attachment_row(data: dict[str, object]) -> TestCaseAttachmentRowDto:
        normalized = dict(data)
        if not isinstance(normalized.get("entity"), str) or not str(normalized["entity"]).strip():
            normalized["entity"] = "test_case"
        return TestCaseAttachmentRowDto.model_validate(normalized)

    @classmethod
    def _parse_test_result_attachment_page(cls, data: dict[str, object]) -> PageTestResultAttachmentRowDto:
        content: list[TestResultAttachmentRowDto] = []
        raw_content = data.get("content")
        if isinstance(raw_content, list):
            content = [cls._build_test_result_attachment_row(item) for item in raw_content if isinstance(item, dict)]

        empty = data.get("empty")
        first = data.get("first")
        last = data.get("last")
        number = data.get("number")
        number_of_elements = data.get("numberOfElements")
        size = data.get("size")
        total_elements = data.get("totalElements")
        total_pages = data.get("totalPages")

        return PageTestResultAttachmentRowDto.model_construct(
            content=content,
            empty=empty if isinstance(empty, bool) else None,
            first=first if isinstance(first, bool) else None,
            last=last if isinstance(last, bool) else None,
            number=number if isinstance(number, int) else None,
            number_of_elements=number_of_elements if isinstance(number_of_elements, int) else len(content),
            size=size if isinstance(size, int) else None,
            total_elements=total_elements if isinstance(total_elements, int) else len(content),
            total_pages=total_pages if isinstance(total_pages, int) else None,
        )

    @classmethod
    def _parse_test_case_attachment_page(cls, data: dict[str, object]) -> PageTestCaseAttachmentRowDto:
        content: list[TestCaseAttachmentRowDto] = []
        raw_content = data.get("content")
        if isinstance(raw_content, list):
            content = [cls._build_test_case_attachment_row(item) for item in raw_content if isinstance(item, dict)]

        empty = data.get("empty")
        first = data.get("first")
        last = data.get("last")
        number = data.get("number")
        number_of_elements = data.get("numberOfElements")
        size = data.get("size")
        total_elements = data.get("totalElements")
        total_pages = data.get("totalPages")

        return PageTestCaseAttachmentRowDto.model_construct(
            content=content,
            empty=empty if isinstance(empty, bool) else None,
            first=first if isinstance(first, bool) else None,
            last=last if isinstance(last, bool) else None,
            number=number if isinstance(number, int) else None,
            number_of_elements=number_of_elements if isinstance(number_of_elements, int) else len(content),
            size=size if isinstance(size, int) else None,
            total_elements=total_elements if isinstance(total_elements, int) else len(content),
            total_pages=total_pages if isinstance(total_pages, int) else None,
        )

    async def add_test_fixture_attachment(
        self,
        fixture_result_id: int,
        files: list[bytes | str | tuple[str, bytes]],
    ) -> int:
        """Upload attachments to a test fixture result."""
        if not isinstance(fixture_result_id, int) or fixture_result_id <= 0:
            raise AllureValidationError("Fixture Result ID must be a positive integer")
        if not isinstance(files, list) or not files:
            raise AllureValidationError("files must be a non-empty list")

        response = await self._upload_multipart_files(
            method="POST",
            resource_path=f"/api/upload/test-fixture-result/{fixture_result_id}/attachment",
            files={"file": files},
            expected_status_codes=(200, 202),
        )
        return int(response.status)

    async def update_test_result_attachment_content(
        self,
        attachment_id: int,
        files: list[bytes | str | tuple[str, bytes]],
    ) -> int:
        """Replace content for an existing test-result attachment."""
        api = await self._get_api("_test_result_attachment_api", error_name="test result attachment APIs")

        if not isinstance(attachment_id, int) or attachment_id <= 0:
            raise AllureValidationError("Attachment ID must be a positive integer")
        if not isinstance(files, list) or not files:
            raise AllureValidationError("files must be a non-empty list")

        await self._call_api(
            api.update_content(
                id=attachment_id,
                file=files[0],
                _request_timeout=self._timeout,
            )
        )
        return 200

    async def upload_results_to_launch(
        self,
        launch_id: int,
        files: list[bytes | str | tuple[str, bytes]],
        info: LaunchExistingUploadDto | None = None,
    ) -> LaunchUploadResponseDto:
        """Upload result files/archives to an existing launch.

        Args:
            launch_id: The unique ID of the launch.
            files: Files to upload (paths, bytes, or named byte tuples).
            info: Optional upload metadata (`LaunchExistingUploadDto`).

        Returns:
            Upload response payload.

        Raises:
            AllureValidationError: If inputs are invalid.
            AllureAPIError: If the server returns an error.
        """
        if not isinstance(launch_id, int) or launch_id <= 0:
            raise AllureValidationError("Launch ID must be a positive integer")
        if not isinstance(files, list) or not files:
            raise AllureValidationError("files must be a non-empty list")

        info_payload = info if info is not None else LaunchExistingUploadDto()
        info_part = json.dumps(info_payload.to_dict()).encode("utf-8")
        files_map: dict[str, bytes | str | tuple[str, bytes] | list[bytes | str | tuple[str, bytes]]] = {
            "file": files,
            "info": ("info.json", info_part),
        }

        upload_paths = [
            f"/api/launch/{launch_id}/upload/file",
            f"/api/launch/{launch_id}/upload",
        ]

        last_error: ApiException | None = None

        for resource_path in upload_paths:
            try:
                rest_response = await self._upload_multipart_files(
                    method="POST",
                    resource_path=resource_path,
                    files=files_map,
                    expected_status_codes=(200, 201, 202, 204),
                    accept_header="*/*",
                )
            except AllureAPIError as exc:
                if exc.status_code is None:
                    raise
                last_error = ApiException(
                    status=exc.status_code,
                    reason="Upload failed",
                    body=exc.response_body,
                )
                continue

            status_code = rest_response.status
            if not 200 <= status_code <= 299:
                last_error = ApiException(
                    status=status_code,
                    reason=rest_response.reason,
                    body=rest_response.response.text,
                )
                continue

            data = rest_response.response.json()
            if not isinstance(data, dict):
                raise AllureAPIError("Unexpected launch upload response from API")

            result = LaunchUploadResponseDto.from_dict(data)
            if result is None:
                raise AllureAPIError("Unexpected launch upload response from API")

            return result

        if last_error is not None:
            self._handle_api_exception(last_error)
            raise last_error

        raise AllureAPIError("Launch upload failed")

    async def delete_launch(self, launch_id: int) -> None:
        """Delete a specific launch by its ID.

        Args:
            launch_id: The unique ID of the launch.

        Raises:
            AllureNotFoundError: If launch doesn't exist.
            AllureValidationError: If input is invalid.
            AllureAuthError: If unauthorized.
            AllureAPIError: If the server returns an error.
        """
        api = await self._get_api("_launch_api", error_name="launch APIs")

        if not isinstance(launch_id, int) or launch_id <= 0:
            raise AllureValidationError("Launch ID must be a positive integer")

        await self._call_api(api.delete27(id=launch_id, _request_timeout=self._timeout))

    async def search_launches_aql(
        self,
        project_id: int,
        rql: str,
        page: int = 0,
        size: int = 20,
        sort: list[str] | None = None,
    ) -> PageLaunchDto:
        """Search launches using raw AQL (Allure Query Language).

        Args:
            project_id: Target project ID.
            rql: Raw AQL query string.
            page: Zero-based page index.
            size: Page size (max 100).
            sort: Optional sort criteria (e.g., ["createdDate,DESC"]).

        Returns:
            Paginated launch results matching the AQL query.

        Raises:
            AllureValidationError: If AQL syntax is invalid or input fails validation.
            AllureNotFoundError: If project doesn't exist.
            AllureAuthError: If unauthorized.
            AllureAPIError: If the server returns an error.
        """
        api = await self._get_api("_launch_search_api", error_name="launch search APIs")

        if not isinstance(project_id, int) or project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")
        if not isinstance(rql, str) or not rql.strip():
            raise AllureValidationError("AQL query must be a non-empty string")
        if not isinstance(page, int) or page < 0:
            raise AllureValidationError("Page must be a non-negative integer")
        if not isinstance(size, int) or size <= 0 or size > 100:
            raise AllureValidationError("Size must be between 1 and 100")

        return await self._call_api(
            api.search2(
                project_id=project_id,
                rql=rql,
                page=page,
                size=size,
                sort=sort,
                _request_timeout=self._timeout,
            )
        )

    async def validate_launch_query(
        self,
        project_id: int,
        rql: str,
    ) -> AqlValidateResponseDto:
        """Validate an AQL query for launches without executing it.

        Args:
            project_id: Target project ID.
            rql: Raw AQL query string to validate.

        Returns:
            Validation response with validity and count.

        Raises:
            AllureValidationError: If input fails basic validation.
            AllureNotFoundError: If project doesn't exist.
            AllureAuthError: If unauthorized.
            AllureAPIError: If the server returns an error.
        """
        api = await self._get_api("_launch_search_api", error_name="launch search APIs")

        if not isinstance(project_id, int) or project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")
        if not isinstance(rql, str) or not rql.strip():
            raise AllureValidationError("AQL query must be a non-empty string")

        return await self._call_api(
            api.validate_query2(
                project_id=project_id,
                rql=rql,
                _request_timeout=self._timeout,
            )
        )

    async def search_test_cases_aql(
        self,
        project_id: int,
        rql: str,
        page: int = 0,
        size: int = 20,
        deleted: bool = False,
        sort: list[str] | None = None,
    ) -> PageTestCaseDto:
        """Search test cases using raw AQL (Allure Query Language).

        This method passes the AQL query directly to the Allure search endpoint,
        supporting complex queries with operators like AND, OR, NOT, and field filters.

        Args:
            project_id: Target project ID.
            rql: Raw AQL query string (e.g., 'status="failed" and tag="regression"').
            page: Zero-based page index.
            size: Page size (max 100).
            deleted: If True, include deleted test cases.
            sort: Optional sort criteria (e.g., ["id,DESC"]).

        Returns:
            Paginated test case results matching the AQL query.

        Raises:
            AllureValidationError: If AQL syntax is invalid or input fails validation.
            AllureNotFoundError: If project doesn't exist.
            AllureAuthError: If unauthorized.
            AllureAPIError: If the server returns an error.
        """
        search_api = await self._get_api("_search_api", error_name="test_case search APIs")

        if not isinstance(project_id, int) or project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")

        if not isinstance(rql, str) or not rql.strip():
            raise AllureValidationError("AQL query must be a non-empty string")

        if not isinstance(page, int) or page < 0:
            raise AllureValidationError("Page must be a non-negative integer")
        if not isinstance(size, int) or size <= 0 or size > 100:
            raise AllureValidationError("Size must be between 1 and 100")

        return await self._call_api(
            search_api.search1(
                project_id=project_id,
                rql=rql,
                deleted=deleted,
                page=page,
                size=size,
                sort=sort,
                _request_timeout=self._timeout,
            )
        )

    async def validate_test_case_query(
        self,
        project_id: int,
        rql: str,
        deleted: bool = False,
    ) -> tuple[bool, int | None]:
        """Validate an AQL query without executing it.

        Use this to check AQL syntax and get an estimated count of matching
        test cases before running an expensive search.

        Args:
            project_id: Target project ID.
            rql: Raw AQL query string to validate.
            deleted: If True, include deleted test cases in count.

        Returns:
            A tuple of (is_valid, count). If valid is True, count is the
            estimated number of matching test cases. If valid is False,
            count may be None.

        Raises:
            AllureValidationError: If input fails basic validation.
            AllureNotFoundError: If project doesn't exist.
            AllureAuthError: If unauthorized.
            AllureAPIError: If the server returns an error.
        """
        search_api = await self._get_api("_search_api", error_name="test_case search APIs")

        if not isinstance(project_id, int) or project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")

        if not isinstance(rql, str) or not rql.strip():
            raise AllureValidationError("AQL query must be a non-empty string")

        response = await self._call_api(
            search_api.validate_query1(
                project_id=project_id,
                rql=rql,
                deleted=deleted,
                _request_timeout=self._timeout,
            )
        )

        return (response.valid or False, response.count)

    async def upload_attachment(
        self,
        test_case_id: int,
        file_data: list[bytes | str | tuple[str, bytes]],
    ) -> list[TestCaseAttachmentRowDto]:
        """Upload one or more attachments to a test case.

        Args:
            test_case_id: Target test case ID.
            file_data: List of tuples containing (filename, content_bytes).

        Returns:
            List of successfully created attachment records.

        Raises:
            AllureValidationError: If file types or sizes are rejected.
            AllureAuthError: If unauthorized.
            AllureAPIError: If the server returns an error.
        """
        attachment_api = await self._get_api("_attachment_api")
        return await self._upload_attachment_via_api(
            attachment_api,
            test_case_id=test_case_id,
            file_data=file_data,
        )

    async def list_test_case_attachments(
        self,
        test_case_id: int,
        *,
        page: int = 0,
        size: int = 100,
        sort: list[str] | None = None,
    ) -> PageTestCaseAttachmentRowDto:
        """List attachments owned by one exact test case for ownership verification."""
        api = await self._get_api("_attachment_api", error_name="test case attachment APIs")
        if not isinstance(test_case_id, int) or isinstance(test_case_id, bool) or test_case_id <= 0:
            raise AllureValidationError("Test Case ID must be a positive integer")
        self._validate_page_size(page, size)
        response = await self._call_api_raw(
            cast(
                Awaitable[httpx.Response],
                api.find_all13_without_preload_content(
                    test_case_id=test_case_id,
                    page=page,
                    size=size,
                    sort=sort,
                    _request_timeout=self._timeout,
                ),
            )
        )
        try:
            return self._parse_test_case_attachment_page(self._extract_response_data(response))
        except ApiException as exc:
            self._handle_api_exception(exc)
            raise

    async def read_test_case_attachment(self, attachment_id: int, *, inline: bool = False) -> AttachmentContent:
        """Read test-case attachment bytes plus trusted upstream response metadata."""
        api = await self._get_api("_attachment_api", error_name="test case attachment APIs")
        if not isinstance(attachment_id, int) or isinstance(attachment_id, bool) or attachment_id <= 0:
            raise AllureValidationError("Attachment ID must be a positive integer")
        return await self._read_attachment_content(
            cast(
                Awaitable[httpx.Response],
                api.read_content2_without_preload_content(
                    id=attachment_id,
                    inline=inline,
                    _request_timeout=self._timeout,
                ),
            )
        )

    def stream_test_case_attachment(
        self, attachment_id: int, *, inline: bool = False
    ) -> AbstractAsyncContextManager[AttachmentContentStream]:
        """Stream test-case attachment content for bounded local delivery."""
        return self._stream_attachment_content(
            attachment_id,
            resource_path="/api/testcase/attachment/{id}/content",
            inline=inline,
        )

    async def create_scenario_step(
        self,
        test_case_id: int,
        step: ScenarioStepCreateDto,
        after_id: int | None = None,
        with_expected_result: bool = False,
    ) -> ScenarioStepCreatedResponseDto:
        """Create a scenario step for an existing test case.

        Args:
            test_case_id: The ID of the test case to add the step to.
            step: The step data to create. Must have test_case_id set.
            after_id: Optional ID of the step after which to insert the new step.
            with_expected_result: If True, creates an expected result step below.

        Returns:
            The response containing the created step ID and updated scenario.

        Raises:
            AllureNotFoundError: If test case doesn't exist.
            AllureValidationError: If input data fails validation.
            AllureAuthError: If unauthorized.
            AllureAPIError: If the server returns an error.
        """
        scenario_api = await self._get_api("_scenario_api")

        # Ensure test_case_id is set
        if step.test_case_id is None:
            step = ScenarioStepCreateDto.model_validate(
                {
                    "testCaseId": test_case_id,
                    "body": step.body,
                    "bodyJson": step.body_json,
                    "attachmentId": step.attachment_id,
                    "sharedStepId": step.shared_step_id,
                    "parentId": step.parent_id,
                }
            )

        return await self._create_scenario_step_via_api(
            scenario_api,
            step,
            after_id=after_id,
            with_expected_result=with_expected_result,
        )

    async def list_custom_field_values(
        self,
        project_id: int,
        custom_field_id: int,
        *,
        query: str | None = None,
        var_global: bool | None = None,
        test_case_search: str | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: list[str] | None = None,
    ) -> PageCustomFieldValueWithTcCountDto:
        """List custom field values for a project field.

        Args:
            project_id: Target project ID.
            custom_field_id: Target custom field ID (project-scoped).
            query: Optional search query.
            var_global: Optional global flag filter.
            test_case_search: Optional test case search filter.
            page: Zero-based page index.
            size: Page size.
            sort: Optional sort criteria.

        Returns:
            Paginated custom field values with test case counts.

        Raises:
            AllureNotFoundError: If project or custom field doesn't exist.
            AllureValidationError: If input data fails validation.
            AllureAuthError: If unauthorized.
            AllureAPIError: If the server returns an error.
        """
        api = await self._get_api("_custom_field_value_project_api")

        if not isinstance(project_id, int) or project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")
        if not isinstance(custom_field_id, int) or custom_field_id == 0:
            raise AllureValidationError("Custom Field ID must be a non-zero integer")
        if page is not None and (not isinstance(page, int) or page < 0):
            raise AllureValidationError("Page must be a non-negative integer")
        if size is not None and (not isinstance(size, int) or size <= 0 or size > 1000):
            raise AllureValidationError("Size must be between 1 and 1000")

        return await self._call_api(
            api.find_all22(
                project_id=project_id,
                custom_field_id=custom_field_id,
                query=query,
                var_global=var_global,
                test_case_search=test_case_search,
                page=page,
                size=size,
                sort=sort,
                _request_timeout=self._timeout,
            )
        )

    async def create_custom_field_value(
        self, project_id: int, data: CustomFieldValueProjectCreateDto
    ) -> CustomFieldValueWithCfDto:
        """Create a custom field value in a project.

        Args:
            project_id: Target project ID.
            data: Custom field value payload.

        Returns:
            The created custom field value DTO.

        Raises:
            AllureNotFoundError: If project doesn't exist.
            AllureValidationError: If input data fails validation.
            AllureAuthError: If unauthorized.
            AllureAPIError: If the server returns an error.
        """
        api = await self._get_api("_custom_field_value_project_api")

        if not isinstance(project_id, int) or project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")

        try:
            return await self._call_api(
                api.create26(
                    project_id=project_id,
                    custom_field_value_project_create_dto=data,
                    _request_timeout=self._timeout,
                )
            )
        except AllureAPIError as exc:
            if exc.status_code == 409:
                raise AllureValidationError(
                    "Duplicate custom field value name.",
                    status_code=exc.status_code,
                    response_body=exc.response_body,
                    suggestions=["Use a unique custom field value name"],
                ) from exc
            raise

    async def update_custom_field_value(
        self, project_id: int, cfv_id: int, data: CustomFieldValueProjectPatchDto
    ) -> None:
        """Update a custom field value in a project.

        Args:
            project_id: Target project ID.
            cfv_id: Target custom field value ID.
            data: Patch payload for the custom field value.

        Raises:
            AllureNotFoundError: If project or value doesn't exist.
            AllureValidationError: If input data fails validation.
            AllureAuthError: If unauthorized.
            AllureAPIError: If the server returns an error.
        """
        api = await self._get_api("_custom_field_value_project_api")

        if not isinstance(project_id, int) or project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")
        if not isinstance(cfv_id, int) or cfv_id <= 0:
            raise AllureValidationError("Custom Field Value ID must be a positive integer")

        await self._call_api(
            api.patch23(
                project_id=project_id,
                cfv_id=cfv_id,
                custom_field_value_project_patch_dto=data,
                _request_timeout=self._timeout,
            )
        )

    async def delete_custom_field_value(self, project_id: int, cfv_id: int) -> None:
        """Delete a custom field value in a project.

        Args:
            project_id: Target project ID.
            cfv_id: Target custom field value ID.

        Raises:
            AllureNotFoundError: If project or value doesn't exist.
            AllureValidationError: If input data fails validation.
            AllureAuthError: If unauthorized.
            AllureAPIError: If the server returns an error.
        """
        api = await self._get_api("_custom_field_value_project_api")

        if not isinstance(project_id, int) or project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")
        if not isinstance(cfv_id, int) or cfv_id <= 0:
            raise AllureValidationError("Custom Field Value ID must be a positive integer")

        await self._call_api(
            api.delete47(
                project_id=project_id,
                id=cfv_id,
                _request_timeout=self._timeout,
            )
        )

    async def get_custom_fields_with_values(self, project_id: int) -> list[CustomFieldProjectWithValuesDto]:
        """Fetch all custom fields and their allowed values for a project.

        This method uses CustomFieldProjectControllerV2Api to find all custom fields
        associated with the project and then fetches their allowed values using
        CustomFieldValueProjectControllerApi.

        Args:
            project_id: Target project ID.

        Returns:
            List of custom field DTOs with values.

        Raises:
            AllureValidationError: If project_id is invalid.
            AllureAuthError: If unauthorized.
            AllureAPIError: If the server returns an error.
        """
        if not isinstance(project_id, int) or project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")

        v2_api = await self._get_api("_custom_field_project_v2_api")
        val_api = await self._get_api("_custom_field_value_project_api")

        # 1. Get all custom fields for project
        page = await self._call_api(v2_api.find_by_project1(project_id=project_id))

        results: list[CustomFieldProjectWithValuesDto] = []

        for cf_proj in page.content or []:
            if not cf_proj.custom_field or cf_proj.custom_field.id is None:
                continue

            # 2. Get values for each field
            try:
                values_page = await self._call_api(
                    val_api.find_all22(project_id=project_id, custom_field_id=cf_proj.custom_field.id)
                )

                allowed_values = [CustomFieldValueDto(id=v.id, name=v.name) for v in values_page.content or []]

                results.append(
                    CustomFieldProjectWithValuesDto(
                        custom_field=cf_proj,  # Wait, CustomFieldProjectWithValuesDto expect CustomFieldProjectDto
                        values=allowed_values,
                    )
                )
            except AllureAPIError as e:
                # If fetching values fails for one field, log and continue
                logger.warning(f"Failed to fetch values for custom field {cf_proj.custom_field.name}: {e}")
                results.append(CustomFieldProjectWithValuesDto(custom_field=cf_proj, values=[]))

        return results

    async def get_test_case_custom_fields(
        self,
        test_case_id: int,
        project_id: int,
    ) -> list[CustomFieldProjectWithValuesDto]:
        """Fetch custom fields with values for a specific test case.

        Args:
            test_case_id: Target test case ID.
            project_id: The project ID context.

        Returns:
            List of custom field DTOs with their assigned values.
        """
        api = await self._get_api("_test_case_custom_field_api")
        return await self._call_api(
            api.get_custom_fields_with_values3(
                test_case_id=test_case_id,
                project_id=project_id,
                _request_timeout=self._timeout,
            )
        )

    async def update_cfvs_of_test_case(
        self,
        test_case_id: int,
        custom_fields: list[CustomFieldValueWithCfDto],
    ) -> None:
        """Update custom field values for a test case.

        Args:
            test_case_id: Target test case ID.
            custom_fields: List of custom field DTOs with new values.
        """
        api = await self._get_api("_test_case_custom_field_api")
        await self._call_api(
            api.update_cfvs_of_test_case(
                test_case_id=test_case_id,
                custom_field_with_values_dto=custom_fields,
                _request_timeout=self._timeout,
            )
        )

    async def delete_scenario_step(self, step_id: int) -> None:
        """Delete a scenario step.

        Args:
            step_id: ID of the step to delete.

        Raises:
            AllureAPIError: If the API request fails.
        """
        scenario_api = await self._get_api("_scenario_api")
        await self._call_api_raw(
            scenario_api.delete_by_id1_without_preload_content(
                id=step_id,
                _request_timeout=self._timeout,
            )
        )

    async def get_test_case(self, test_case_id: int) -> TestCaseDtoWithCF:
        """Retrieve a specific test case by its ID.

        Args:
            test_case_id: The unique ID of the test case.

        Returns:
            The test case data.

        Raises:
            AllureNotFoundError: If test case doesn't exist.
            AllureAuthError: If unauthorized.
            AllureAPIError: If the server returns an error.
        """
        test_case_api = await self._get_api("_test_case_api")

        try:
            # Use _without_preload_content to get raw JSON for missing fields (like customFields)
            # Actually, for customFields we now use get_overview
            response = await self._call_api_raw(
                test_case_api.find_one11_without_preload_content(id=test_case_id, _request_timeout=self._timeout)
            )
            raw_data = self._extract_response_data(response)
            # Use our subclass to support extra fields
            case = TestCaseDtoWithCF.model_validate(raw_data)

            # Fetch custom fields from overview
            try:
                overview = await self._overview_api.get_overview(
                    test_case_id=test_case_id, _request_timeout=self._timeout
                )
                if overview.custom_fields:
                    case.custom_fields = overview.custom_fields
                # Preserve an empty issue list so callers can distinguish a
                # successful overview response with no links from a failed
                # overview request, which leaves this field as None.
                case.issues = overview.issues or []
            except Exception as e:
                logger.warning(f"Failed to fetch overview for test case {test_case_id}: {e}")

            return case
        except AllureNotFoundError as e:
            raise TestCaseNotFoundError(
                test_case_id=test_case_id,
                status_code=getattr(e, "status_code", None),
                response_body=getattr(e, "response_body", None),
            ) from e
        except ApiException as e:
            try:
                self._handle_api_exception(e)
            except AllureNotFoundError as nf:
                raise TestCaseNotFoundError(
                    test_case_id=test_case_id,
                    status_code=getattr(nf, "status_code", None),
                    response_body=getattr(nf, "response_body", None),
                ) from nf
            raise

    async def update_test_case(self, test_case_id: int, data: TestCasePatchV2Dto) -> TestCaseDto:
        """Update an existing test case with new data.

        Args:
            test_case_id: The ID of the test case to update.
            data: The new data to apply.

        Returns:
            The updated test case.

        Raises:
            AllureNotFoundError: If test case doesn't exist.
            AllureValidationError: If input data fails validation.
            AllureAuthError: If unauthorized.
            AllureAPIError: If the server returns an error.
        """
        test_case_api = await self._get_api("_test_case_api")
        return await self._call_api(
            test_case_api.patch13(
                id=test_case_id,
                test_case_patch_v2_dto=data,
                _request_timeout=self._timeout,
            )
        )

    async def get_test_case_scenario(self, test_case_id: int) -> TestCaseScenarioV2Dto:
        """Retrieve the scenario (steps and attachments) for a test case.

        Args:
            test_case_id: The ID of the test case.

        Returns:
            The test case scenario including steps and attachments.

        Raises:
            AllureNotFoundError: If test case doesn't exist.
            AllureAuthError: If unauthorized.
            AllureAPIError: If the server returns an error.
        """
        scenario_api = await self._get_api("_scenario_api", error_name="test_case_scenario_api")

        response = await self._call_api_raw(
            scenario_api.get_normalized_scenario_without_preload_content(
                id=test_case_id, _request_timeout=self._timeout
            )
        )
        raw_data = self._extract_response_data(response)
        return self._denormalize_to_v2_from_dict(raw_data)

    @staticmethod
    def _denormalize_to_v2_from_dict(raw: dict[str, object]) -> TestCaseScenarioV2Dto:  # noqa: C901
        """Convert a raw NormalizedScenarioDto dict into a TestCaseScenarioV2Dto tree.

        This bypasses the generated from_dict which has broken oneOf deserialization.
        """
        raw_root = raw.get("root")
        if not isinstance(raw_root, dict):
            return TestCaseScenarioV2Dto(steps=[])

        root_children = raw_root.get("children")
        if not isinstance(root_children, list):
            return TestCaseScenarioV2Dto(steps=[])

        scenario_steps_raw = raw.get("scenarioSteps", {})
        scenario_steps = scenario_steps_raw if isinstance(scenario_steps_raw, dict) else {}
        attachments_raw = raw.get("attachments", {})
        attachments_map = attachments_raw if isinstance(attachments_raw, dict) else {}

        # Recursive helper to build steps
        def build_steps(step_ids: list[int]) -> list[SharedStepScenarioDtoStepsInner]:  # noqa: C901
            steps_list: list[SharedStepScenarioDtoStepsInner] = []
            if not step_ids:
                return steps_list

            for sid in step_ids:
                # Look up the step definition
                step_def = scenario_steps.get(str(sid))

                if not step_def:
                    continue

                # Is it an attachment?
                attachment_id = step_def.get("attachmentId")
                shared_step_id = step_def.get("sharedStepId")

                if attachment_id:
                    # Look up name in attachments map
                    # attachments map key is the attachment ID as string
                    att_info = attachments_map.get(str(attachment_id), {})
                    att_name = att_info.get("name") or step_def.get("name")

                    # Build AttachmentStepDtoWithName
                    steps_list.append(
                        SharedStepScenarioDtoStepsInner(
                            actual_instance=AttachmentStepDtoWithName.model_construct(
                                type="AttachmentStepDto",
                                attachment_id=attachment_id,
                                name=att_name,
                                id=sid,
                            )
                        )
                    )
                elif shared_step_id:
                    # It's a Shared Step Reference
                    steps_list.append(
                        SharedStepScenarioDtoStepsInner(
                            actual_instance=SharedStepStepDtoWithId.model_construct(
                                type="SharedStepStepDto",
                                shared_step_id=shared_step_id,
                                id=sid,
                            )
                        )
                    )
                else:
                    # It's a Body Step
                    body = step_def.get("body")
                    child_ids = step_def.get("children") or []
                    child_steps = build_steps(child_ids) if child_ids else None

                    # Handle expected results
                    # Expected results can be stored in two ways:
                    # 1. Directly in the step as "expectedResult"
                    # 2. As a reference via "expectedResultId" pointing to a container with children
                    expected_result = step_def.get("expectedResult")
                    expected_result_id = step_def.get("expectedResultId")

                    if expected_result_id and not expected_result:
                        # Look up the expected result container
                        expected_result_container = scenario_steps.get(str(expected_result_id))
                        if expected_result_container:
                            # The container itself might have the text
                            expected_result = expected_result_container.get("body")

                            # Or it might have children with the actual expected result text
                            if not expected_result or expected_result == "Expected Result":
                                # "Expected Result" is often a placeholder, check children
                                expected_children_ids = expected_result_container.get("children") or []
                                if expected_children_ids:
                                    # Collect text from all expected result children
                                    expected_texts = []
                                    for exp_child_id in expected_children_ids:
                                        exp_child = scenario_steps.get(str(exp_child_id))
                                        if exp_child:
                                            exp_text = exp_child.get("body")
                                            if exp_text:
                                                expected_texts.append(exp_text)
                                    if expected_texts:
                                        expected_result = "\n".join(expected_texts)

                    # Build StepWithExpected
                    steps_list.append(
                        SharedStepScenarioDtoStepsInner(
                            actual_instance=StepWithExpected.model_construct(
                                type="BodyStepDto",
                                body=body,
                                body_json=None,  # Skip complex rich-text
                                expected_result=expected_result,
                                steps=child_steps,
                                id=sid,
                            )
                        )
                    )
            return steps_list

        final_steps = build_steps(root_children)
        return TestCaseScenarioV2Dto(steps=final_steps)

    async def delete_test_case(self, test_case_id: int, force: bool | None = None) -> None:
        """Delete a test case from the system.

        Args:
            test_case_id: The ID of the test case to remove.
            force: When True, permanently remove an already archived test case.

        Raises:
            AllureAPIError: If the API request fails.
        """
        test_case_api = await self._get_api("_test_case_api")
        await self._call_api(test_case_api.delete13(id=test_case_id, force=force))

    # ==========================================
    # Test hierarchy operations
    # ==========================================

    async def list_trees(
        self,
        project_id: int,
        with_archived: bool | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: list[str] | None = None,
    ) -> PageTreeDtoV2:
        """List hierarchy trees in a project."""
        tree_api = await self._get_api("_tree_api", error_name="tree APIs")

        if not isinstance(project_id, int) or project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")
        if page is not None and (not isinstance(page, int) or page < 0):
            raise AllureValidationError("Page must be a non-negative integer")
        if size is not None and (not isinstance(size, int) or size <= 0):
            raise AllureValidationError("Size must be a positive integer")

        return await self._call_api(
            tree_api.find_all48(
                project_id=project_id,
                with_archived=with_archived,
                page=page,
                size=size,
                sort=sort,
                _request_timeout=self._timeout,
            )
        )

    async def get_tree(self, tree_id: int, with_archived: bool | None = None) -> TreeDtoV2:
        """Get tree details by ID."""
        tree_api = await self._get_api("_tree_api", error_name="tree APIs")

        if not isinstance(tree_id, int) or tree_id <= 0:
            raise AllureValidationError("Tree ID must be a positive integer")

        return await self._call_api(
            tree_api.find_one38(
                id=tree_id,
                with_archived=with_archived,
                _request_timeout=self._timeout,
            )
        )

    async def create_tree_group(
        self,
        project_id: int,
        tree_id: int,
        name: str,
        parent_node_id: int | None = None,
    ) -> TestCaseLightTreeNodeDto:
        """Create a test suite group node in a tree."""
        tree_api = await self._get_api("_test_case_tree_api", error_name="test case tree APIs")

        if not isinstance(project_id, int) or project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")
        if not isinstance(tree_id, int) or tree_id <= 0:
            raise AllureValidationError("Tree ID must be a positive integer")
        if not isinstance(name, str) or not name.strip():
            raise AllureValidationError("Suite name is required")
        if parent_node_id is not None and (not isinstance(parent_node_id, int) or parent_node_id <= 0):
            raise AllureValidationError("Parent node ID must be a positive integer")

        dto = TestCaseTreeGroupAddDto(name=name.strip())

        return await self._call_api(
            tree_api.add_group(
                project_id=project_id,
                tree_id=tree_id,
                test_case_tree_group_add_dto=dto,
                parent_node_id=parent_node_id,
                _request_timeout=self._timeout,
            )
        )

    async def upsert_tree_group(
        self,
        project_id: int,
        tree_id: int,
        name: str,
        parent_node_id: int | None = None,
    ) -> TestCaseLightTreeNodeDto:
        """Create or return existing suite group node in a tree."""
        tree_api = await self._get_api("_test_case_tree_api", error_name="test case tree APIs")

        if not isinstance(project_id, int) or project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")
        if not isinstance(tree_id, int) or tree_id <= 0:
            raise AllureValidationError("Tree ID must be a positive integer")
        if not isinstance(name, str) or not name.strip():
            raise AllureValidationError("Suite name is required")
        if parent_node_id is not None and (not isinstance(parent_node_id, int) or parent_node_id <= 0):
            raise AllureValidationError("Parent node ID must be a positive integer")

        dto = TestCaseTreeGroupAddDto(name=name.strip())

        return await self._call_api(
            tree_api.upsert(
                project_id=project_id,
                tree_id=tree_id,
                test_case_tree_group_add_dto=dto,
                parent_node_id=parent_node_id,
                _request_timeout=self._timeout,
            )
        )

    async def rename_tree_group(self, project_id: int, group_id: int, name: str) -> TestCaseLightTreeNodeDto:
        """Rename a suite group node by group ID."""
        tree_api = await self._get_api("_test_case_tree_api", error_name="test case tree APIs")

        if not isinstance(project_id, int) or project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")
        if not isinstance(group_id, int) or group_id <= 0:
            raise AllureValidationError("Group ID must be a positive integer")
        if not isinstance(name, str) or not name.strip():
            raise AllureValidationError("Suite name is required")

        dto = TestCaseTreeGroupRenameDto(name=name.strip())

        return await self._call_api(
            tree_api.rename_group(
                project_id=project_id,
                group_id=group_id,
                test_case_tree_group_rename_dto=dto,
                _request_timeout=self._timeout,
            )
        )

    async def delete_tree_group(self, project_id: int, group_id: int) -> None:
        """Delete a suite group node by group ID."""
        tree_api = await self._get_api("_test_case_tree_api", error_name="test case tree APIs")

        if not isinstance(project_id, int) or project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")
        if not isinstance(group_id, int) or group_id <= 0:
            raise AllureValidationError("Group ID must be a positive integer")

        await self._call_api(
            tree_api.delete_group(
                project_id=project_id,
                group_id=group_id,
                _request_timeout=self._timeout,
            )
        )

    async def create_tree_leaf(
        self,
        project_id: int,
        tree_id: int,
        name: str,
        node_id: int | None = None,
    ) -> TestCaseTreeLeafDtoV2:
        """Create a tree leaf node in a tree."""
        tree_api = await self._get_api("_test_case_tree_api", error_name="test case tree APIs")

        if not isinstance(project_id, int) or project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")
        if not isinstance(tree_id, int) or tree_id <= 0:
            raise AllureValidationError("Tree ID must be a positive integer")
        if not isinstance(name, str) or not name.strip():
            raise AllureValidationError("Leaf name is required")
        if node_id is not None and (not isinstance(node_id, int) or node_id <= 0):
            raise AllureValidationError("Node ID must be a positive integer")

        dto = TestCaseTreeLeafAddDto(name=name.strip())

        return await self._call_api(
            tree_api.add_leaf(
                project_id=project_id,
                tree_id=tree_id,
                test_case_tree_leaf_add_dto=dto,
                node_id=node_id,
                _request_timeout=self._timeout,
            )
        )

    async def rename_tree_leaf(self, project_id: int, leaf_id: int, name: str) -> TestCaseTreeLeafDtoV2:
        """Rename a tree leaf by leaf ID."""
        tree_api = await self._get_api("_test_case_tree_api", error_name="test case tree APIs")

        if not isinstance(project_id, int) or project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")
        if not isinstance(leaf_id, int) or leaf_id <= 0:
            raise AllureValidationError("Leaf ID must be a positive integer")
        if not isinstance(name, str) or not name.strip():
            raise AllureValidationError("Leaf name is required")

        dto = TestCaseTreeLeafRenameDto(name=name.strip())

        return await self._call_api(
            tree_api.rename_leaf(
                project_id=project_id,
                leaf_id=leaf_id,
                test_case_tree_leaf_rename_dto=dto,
                _request_timeout=self._timeout,
            )
        )

    async def get_tree_node(
        self,
        project_id: int,
        tree_id: int,
        parent_node_id: int | None = None,
        search: str | None = None,
        filter_id: int | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: list[str] | None = None,
        query: str | None = None,
        base_aql: str | None = None,
    ) -> TestCaseFullTreeNodeDto:
        """Get test case hierarchy nodes for a tree."""
        tree_api = await self._get_api("_test_case_tree_api", error_name="test case tree APIs")

        if not isinstance(project_id, int) or project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")
        if not isinstance(tree_id, int) or tree_id <= 0:
            raise AllureValidationError("Tree ID must be a positive integer")
        if parent_node_id is not None and (not isinstance(parent_node_id, int) or parent_node_id <= 0):
            raise AllureValidationError("Parent node ID must be a positive integer")
        if filter_id is not None and (not isinstance(filter_id, int) or filter_id <= 0):
            raise AllureValidationError("Filter ID must be a positive integer")
        if page is not None and (not isinstance(page, int) or page < 0):
            raise AllureValidationError("Page must be a non-negative integer")
        if size is not None and (not isinstance(size, int) or size <= 0):
            raise AllureValidationError("Size must be a positive integer")

        response = await self._call_api_raw(
            tree_api.get_tree_node_without_preload_content(
                project_id=project_id,
                tree_id=tree_id,
                parent_node_id=parent_node_id,
                search=search,
                filter_id=filter_id,
                page=page,
                size=size,
                sort=sort,
                query=query,
                base_aql=base_aql,
                _request_timeout=self._timeout,
            )
        )
        try:
            payload = self._extract_response_data(response)
        except ApiException as exc:
            self._handle_api_exception(exc)
            raise

        root = TestCaseFullTreeNodeDto(
            id=payload.get("id"),
            name=payload.get("name"),
            type=payload.get("type"),
            children=self._parse_tree_children(payload.get("children")),
        )
        return root

    def _parse_tree_children(self, children_payload: object) -> PageTestCaseTreeNodeDto | None:
        """Parse raw tree node children payload into generated DTOs safely."""
        if not isinstance(children_payload, dict):
            return None

        content_payload = children_payload.get("content")
        if not isinstance(content_payload, list):
            return PageTestCaseTreeNodeDto(
                content=[],
                total_elements=children_payload.get("totalElements"),
                total_pages=children_payload.get("totalPages"),
                size=children_payload.get("size"),
                number=children_payload.get("number"),
            )

        content: list[PageTestCaseTreeNodeDtoContentInner] = []
        for item in content_payload:
            if not isinstance(item, dict):
                continue

            item_type = item.get("type")
            if item_type == "GROUP":
                group_node = TestCaseLightTreeNodeDto(
                    id=item.get("id"),
                    name=item.get("name"),
                    type=item_type,
                    count=item.get("count"),
                    custom_field_id=item.get("customFieldId"),
                    custom_field_value_id=item.get("customFieldValueId"),
                    parent_node_id=item.get("parentNodeId"),
                )
                content.append(PageTestCaseTreeNodeDtoContentInner(actual_instance=group_node))
                continue

            if item_type == "LEAF":
                leaf_payload = dict(item)
                if "testCaseId" not in leaf_payload and isinstance(leaf_payload.get("id"), int):
                    leaf_payload["testCaseId"] = leaf_payload["id"]
                leaf_node = TestCaseTreeLeafDtoV2.from_dict(leaf_payload)
                if leaf_node is not None:
                    content.append(PageTestCaseTreeNodeDtoContentInner(actual_instance=leaf_node))

        return PageTestCaseTreeNodeDto(
            content=content,
            total_elements=children_payload.get("totalElements"),
            total_pages=children_payload.get("totalPages"),
            size=children_payload.get("size"),
            number=children_payload.get("number"),
        )

    async def assign_test_cases_to_tree_node(
        self,
        project_id: int,
        test_case_ids: list[int],
        target_node_id: int,
        tree_id: int,
    ) -> None:
        """Assign test cases to a suite node via bulk drag-and-drop."""
        bulk_api = await self._get_api("_test_case_tree_bulk_api", error_name="test case tree bulk APIs")

        if not isinstance(project_id, int) or project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")
        if not isinstance(target_node_id, int) or target_node_id <= 0:
            raise AllureValidationError("Target node ID must be a positive integer")
        if not isinstance(tree_id, int) or tree_id <= 0:
            raise AllureValidationError("Tree ID must be a positive integer")
        if not isinstance(test_case_ids, list) or not test_case_ids:
            raise AllureValidationError("At least one test case ID is required")

        normalized_ids: list[int] = []
        for case_id in test_case_ids:
            if not isinstance(case_id, int) or case_id <= 0:
                raise AllureValidationError("All test case IDs must be positive integers")
            normalized_ids.append(case_id)

        selection = TestCaseTreeSelectionDtoV2(
            project_id=project_id,
            tree_id=tree_id,
            leaves_include=normalized_ids,
            node_id=target_node_id,
        )
        drag_payload = TestCaseBulkDragAndDropDtoV2(node_id=target_node_id, selection=selection)

        await self._call_api(
            bulk_api.drag_and_drop(
                test_case_bulk_drag_and_drop_dto_v2=drag_payload,
                _request_timeout=self._timeout,
            )
        )

    async def suggest_tree_groups(
        self,
        project_id: int,
        query: str | None = None,
        tree_id: int | None = None,
        path: list[int] | None = None,
        node_ids: list[int] | None = None,
        ignore_ids: list[int] | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: list[str] | None = None,
    ) -> PageIdAndNameOnlyDto:
        """Suggest tree groups (id/name) for suite navigation and matching."""
        tree_api = await self._get_api("_test_case_tree_api", error_name="test case tree APIs")

        if not isinstance(project_id, int) or project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")
        if tree_id is not None and (not isinstance(tree_id, int) or tree_id <= 0):
            raise AllureValidationError("Tree ID must be a positive integer")
        if page is not None and (not isinstance(page, int) or page < 0):
            raise AllureValidationError("Page must be a non-negative integer")
        if size is not None and (not isinstance(size, int) or size <= 0):
            raise AllureValidationError("Size must be a positive integer")

        validated_path = self._validate_positive_int_list(path, "Path node IDs must be positive integers")
        validated_node_ids = self._validate_positive_int_list(node_ids, "Node IDs must be positive integers")
        validated_ignore_ids = self._validate_positive_int_list(ignore_ids, "Ignore IDs must be positive integers")

        return await self._call_api(
            tree_api.suggest1(
                project_id=project_id,
                query=query,
                tree_id=tree_id,
                path=validated_path,
                id=validated_node_ids,
                ignore_id=validated_ignore_ids,
                page=page,
                size=size,
                sort=sort,
                _request_timeout=self._timeout,
            )
        )

    # ==========================================
    # Shared Step operations
    # ==========================================

    async def create_shared_step(self, project_id: int, name: str) -> SharedStepDto:
        """Create a new shared step.

        Args:
            project_id: Target project ID.
            name: Name of the shared step.

        Returns:
            The created SharedStepDto.

        Raises:
            AllureNotFoundError: If project doesn't exist.
            AllureValidationError: If input data fails validation.
            AllureAuthError: If unauthorized.
            AllureAPIError: If the server returns an error.
        """
        shared_step_api = await self._get_api("_shared_step_api")
        dto = SharedStepCreateDto(name=name, project_id=project_id)
        return await self._call_api(shared_step_api.create19(dto, _request_timeout=self._timeout))

    async def list_shared_steps(
        self,
        project_id: int,
        page: int = 0,
        size: int = 100,
        search: str | None = None,
        archived: bool | None = None,
    ) -> PageSharedStepDto:
        """List shared steps in a project.

        Args:
            project_id: Target project ID.
            page: Zero-based page index.
            size: Page size.
            search: Optional search query (by name).
            archived: Optional filter by archived status.

        Returns:
            Paginated list of shared steps.
        """
        shared_step_api = await self._get_api("_shared_step_api")
        return await self._call_api(
            shared_step_api.find_all16(
                project_id,
                search,
                archived,
                page,
                size,
                None,
                _request_timeout=self._timeout,
            )
        )

    async def create_shared_step_scenario_step(
        self,
        step: ScenarioStepCreateDto,
    ) -> ScenarioStepCreatedResponseDto:
        """Create a step within a shared step scenario.

        Args:
            step: Step data (must include shared_step_id).

        Returns:
            Response containing created step ID.
        """
        shared_step_scenario_api = await self._get_api("_shared_step_scenario_api")

        if not step.shared_step_id:
            raise AllureValidationError("shared_step_id is required for shared step scenario steps")

        return await self._create_scenario_step_via_api(shared_step_scenario_api, step)

    async def patch_test_case_scenario_step(
        self,
        step_id: int,
        patch: ScenarioStepPatchDto,
    ) -> None:
        """Patch a specific scenario step within a test case."""
        scenario_api = await self._get_api("_scenario_api")
        await self._call_api_raw(
            scenario_api.patch_by_id_without_preload_content(
                id=step_id,
                scenario_step_patch_dto=patch,
                with_expected_result=False,
                _request_timeout=self._timeout,
            )
        )

    async def patch_shared_step_scenario_step(
        self,
        step_id: int,
        patch: ScenarioStepPatchDto,
    ) -> None:
        """Patch a specific scenario step within a shared step."""
        shared_step_scenario_api = await self._get_api("_shared_step_scenario_api")
        await self._call_api_raw(
            shared_step_scenario_api.patch_by_id1_without_preload_content(
                id=step_id,
                scenario_step_patch_dto=patch,
                with_expected_result=False,
                _request_timeout=self._timeout,
            )
        )

    async def upload_shared_step_attachment(
        self,
        shared_step_id: int,
        file_data: list[bytes | str | tuple[str, bytes]],
    ) -> list[SharedStepAttachmentRowDto]:
        """Upload attachment(s) to a shared step.

        Args:
            shared_step_id: Target shared step ID.
            file_data: List of files to upload.

        Returns:
            List of created attachment records.
        """
        shared_step_attachment_api = await self._get_api("_shared_step_attachment_api")
        return await self._upload_attachment_via_api(
            shared_step_attachment_api,
            shared_step_id=shared_step_id,
            file_data=file_data,
        )

    async def archive_shared_step(self, shared_step_id: int) -> None:
        """Archive a shared step.

        Args:
            shared_step_id: ID of the shared step to archive.
        """
        shared_step_api = await self._get_api("_shared_step_api")
        await self._call_api(shared_step_api.archive(id=shared_step_id, _request_timeout=self._timeout))

    async def get_shared_step(self, shared_step_id: int) -> SharedStepDto:
        """Retrieve a specific shared step by its ID.

        Args:
            shared_step_id: The unique ID of the shared step.

        Returns:
            The shared step data.

        Raises:
            AllureNotFoundError: If shared step doesn't exist.
            AllureAuthError: If unauthorized.
            AllureAPIError: If the server returns an error.
        """
        shared_step_api = await self._get_api("_shared_step_api")
        return await self._call_api(shared_step_api.find_one15(id=shared_step_id, _request_timeout=self._timeout))

    async def update_shared_step(self, shared_step_id: int, data: SharedStepPatchDto) -> SharedStepDto:
        """Update an existing shared step with new data.

        Args:
            shared_step_id: The ID of the shared step to update.
            data: The new data to apply (partial update supported).

        Returns:
            The updated shared step.

        Raises:
            AllureNotFoundError: If shared step doesn't exist.
            AllureValidationError: If input data fails validation.
            AllureAuthError: If unauthorized.
            AllureAPIError: If the server returns an error.
        """
        shared_step_api = await self._get_api("_shared_step_api")
        return await self._call_api(
            shared_step_api.patch18(
                id=shared_step_id,
                shared_step_patch_dto=data,
                _request_timeout=self._timeout,
            )
        )

    async def delete_shared_step(self, shared_step_id: int) -> None:
        """Delete a shared step from the system.

        This performs a soft delete by archiving the shared step.

        Args:
            shared_step_id: The ID of the shared step to delete.

        Raises:
            AllureNotFoundError: If shared step doesn't exist.
            AllureAPIError: If the API request fails.
        """
        shared_step_api = await self._get_api("_shared_step_api")
        # Soft delete via archive
        await self._call_api(shared_step_api.archive(id=shared_step_id, _request_timeout=self._timeout))

    async def purge_shared_step(self, shared_step_id: int) -> None:
        """Permanently delete a shared step from the system."""
        shared_step_api = await self._get_api("_shared_step_api")
        await self._call_api(shared_step_api.delete18(id=shared_step_id, _request_timeout=self._timeout))

    async def list_project_custom_fields(
        self,
        project_id: int,
        page: int = 0,
        size: int = 100,
        query: str | None = None,
        sort: list[str] | None = None,
    ) -> list[CustomFieldProjectDto]:
        """List custom fields associated with a specific project."""
        api = await self._get_api("_custom_field_project_v2_api")

        if not isinstance(project_id, int) or project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")
        if not isinstance(page, int) or page < 0:
            raise AllureValidationError("Page must be a non-negative integer")
        if not isinstance(size, int) or size <= 0 or size > 100:
            raise AllureValidationError("Size must be between 1 and 100")

        result_page = await self._call_api(
            api.find_by_project1(
                project_id=project_id,
                query=query,
                page=page,
                size=size,
                sort=sort,
                _request_timeout=self._timeout,
            )
        )
        return result_page.content or []

    async def count_test_cases_in_projects(
        self,
        project_ids: list[int],
        custom_field_id: int,
        deleted: bool | None = None,
    ) -> list[ProjectTestCaseCountDto]:
        """Count test cases in projects for a given custom field."""
        api = await self._get_api("_project_api")

        if not project_ids:
            raise AllureValidationError("At least one project ID is required")
        for project_id in project_ids:
            if not isinstance(project_id, int) or project_id <= 0:
                raise AllureValidationError("Project IDs must be positive integers")
        if not isinstance(custom_field_id, int) or custom_field_id <= 0:
            raise AllureValidationError("Custom field ID must be a positive integer")

        return await self._call_api(
            api.count_test_cases_in_projects(
                id=project_ids,
                custom_field_id=custom_field_id,
                deleted=deleted,
                _request_timeout=self._timeout,
            )
        )

    async def remove_custom_field_from_project(self, custom_field_id: int, project_id: int) -> None:
        """Remove a custom field from a project."""
        api = await self._get_api("_custom_field_project_api")

        if not isinstance(custom_field_id, int) or custom_field_id <= 0:
            raise AllureValidationError("Custom field ID must be a positive integer")
        if not isinstance(project_id, int) or project_id <= 0:
            raise AllureValidationError("Project ID must be a positive integer")

        await self._call_api(
            api.remove4(
                custom_field_id=custom_field_id,
                project_id=project_id,
                _request_timeout=self._timeout,
            )
        )

    async def update_test_case_custom_fields(
        self, test_case_id: int, custom_fields: list[CustomFieldValueWithCfDto]
    ) -> None:
        """Update custom field values of a test case using dedicated endpoint.

        Args:
            test_case_id: Target test case ID.
            custom_fields: List of custom fields with values to set/clear.
        """
        api = await self._get_api("_test_case_custom_field_api")
        await self._call_api(
            api.update_cfvs_of_test_case(
                test_case_id=test_case_id,
                custom_field_with_values_dto=custom_fields,
                _request_timeout=self._timeout,
            )
        )
