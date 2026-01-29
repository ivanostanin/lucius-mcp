"""Async HTTP client for Allure TestOps API.

This module provides a high-level wrapper around the auto-generated Allure TestOps
client, adding features like token management, automatic refresh, and
standardized error handling.
"""

import time
from collections.abc import Awaitable
from typing import Literal, TypeVar, cast, overload

import httpx
from pydantic import SecretStr

from src.client.exceptions import TestCaseNotFoundError
from src.utils.config import settings
from src.utils.logger import get_logger

from .exceptions import (
    AllureAPIError,
    AllureAuthError,
    AllureNotFoundError,
    AllureRateLimitError,
    AllureValidationError,
)
from .generated.api.custom_field_controller_api import CustomFieldControllerApi
from .generated.api.custom_field_project_controller_api import CustomFieldProjectControllerApi
from .generated.api.custom_field_project_controller_v2_api import CustomFieldProjectControllerV2Api
from .generated.api.custom_field_value_project_controller_api import CustomFieldValueProjectControllerApi
from .generated.api.shared_step_attachment_controller_api import SharedStepAttachmentControllerApi
from .generated.api.shared_step_controller_api import SharedStepControllerApi
from .generated.api.shared_step_scenario_controller_api import SharedStepScenarioControllerApi
from .generated.api.test_case_attachment_controller_api import TestCaseAttachmentControllerApi
from .generated.api.test_case_controller_api import TestCaseControllerApi
from .generated.api.test_case_custom_field_controller_api import TestCaseCustomFieldControllerApi
from .generated.api.test_case_overview_controller_api import TestCaseOverviewControllerApi
from .generated.api.test_case_scenario_controller_api import TestCaseScenarioControllerApi
from .generated.api.test_case_search_controller_api import TestCaseSearchControllerApi
from .generated.api_client import ApiClient
from .generated.configuration import Configuration
from .generated.exceptions import ApiException
from .generated.models.attachment_step_dto import AttachmentStepDto
from .generated.models.body_step_dto import BodyStepDto
from .generated.models.custom_field_project_with_values_dto import CustomFieldProjectWithValuesDto
from .generated.models.custom_field_value_with_cf_dto import CustomFieldValueWithCfDto
from .generated.models.page_shared_step_dto import PageSharedStepDto
from .generated.models.page_test_case_dto import PageTestCaseDto
from .generated.models.scenario_step_create_dto import ScenarioStepCreateDto
from .generated.models.scenario_step_created_response_dto import ScenarioStepCreatedResponseDto
from .generated.models.shared_step_attachment_row_dto import SharedStepAttachmentRowDto
from .generated.models.shared_step_create_dto import SharedStepCreateDto
from .generated.models.shared_step_dto import SharedStepDto
from .generated.models.shared_step_patch_dto import SharedStepPatchDto
from .generated.models.shared_step_scenario_dto_steps_inner import SharedStepScenarioDtoStepsInner
from .generated.models.shared_step_step_dto import SharedStepStepDto
from .generated.models.test_case_attachment_row_dto import TestCaseAttachmentRowDto
from .generated.models.test_case_create_v2_dto import TestCaseCreateV2Dto
from .generated.models.test_case_dto import TestCaseDto
from .generated.models.test_case_overview_dto import TestCaseOverviewDto
from .generated.models.test_case_patch_v2_dto import TestCasePatchV2Dto
from .generated.models.test_case_row_dto import TestCaseRowDto
from .generated.models.test_case_scenario_dto import TestCaseScenarioDto
from .generated.models.test_case_scenario_v2_dto import TestCaseScenarioV2Dto
from .generated.models.test_case_tree_selection_dto import TestCaseTreeSelectionDto


# Subclasses to add missing fields to generated models
class TestCaseDtoWithCF(TestCaseDto):
    """Subclass to support custom_fields access."""

    custom_fields: list[CustomFieldValueWithCfDto] | None = None


class BodyStepDtoWithSteps(BodyStepDto):
    """Subclass to support nested steps and id."""

    steps: list[SharedStepScenarioDtoStepsInner] | None = None
    id: int | None = None


class AttachmentStepDtoWithName(AttachmentStepDto):
    """Subclass to support name attribute and id."""

    name: str | None = None
    id: int | None = None


class SharedStepStepDtoWithId(SharedStepStepDto):
    """Subclass to support id attribute."""

    id: int | None = None


logger = get_logger(__name__)

T = TypeVar("T")

type ApiType = (
    TestCaseControllerApi
    | SharedStepControllerApi
    | SharedStepAttachmentControllerApi
    | TestCaseAttachmentControllerApi
    | TestCaseScenarioControllerApi
    | SharedStepScenarioControllerApi
    | TestCaseOverviewControllerApi
    | TestCaseSearchControllerApi
    | TestCaseCustomFieldControllerApi
    | CustomFieldControllerApi
    | CustomFieldProjectControllerApi
    | CustomFieldProjectControllerV2Api
    | CustomFieldValueProjectControllerApi
)

type NormalizedScenarioDict = dict[str, object]

type ScenarioStepsMap = dict[str, dict[str, object]]

type AttachmentsMap = dict[str, dict[str, object]]

# Export models for convenience
__all__ = [
    "AllureClient",
    "AttachmentStepDtoWithName",
    "BodyStepDtoWithSteps",
    "CustomFieldProjectWithValuesDto",
    "PageSharedStepDto",
    "PageTestCaseDto",
    "ScenarioStepCreateDto",
    "ScenarioStepCreatedResponseDto",
    "SharedStepAttachmentRowDto",
    "SharedStepCreateDto",
    "SharedStepDto",
    "SharedStepPatchDto",
    "SharedStepScenarioDtoStepsInner",
    "SharedStepStepDtoWithId",
    "TestCaseAttachmentRowDto",
    "TestCaseCreateV2Dto",
    "TestCaseDto",
    "TestCaseDtoWithCF",
    "TestCaseOverviewDto",
    "TestCasePatchV2Dto",
    "TestCaseRowDto",
    "TestCaseScenarioDto",
    "TestCaseScenarioV2Dto",
    "TestCaseTreeSelectionDto",
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
        self._test_case_custom_field_api: TestCaseCustomFieldControllerApi | None = None
        self._custom_field_api: CustomFieldControllerApi | None = None
        self._custom_field_project_api: CustomFieldProjectControllerApi | None = None
        self._custom_field_project_v2_api: CustomFieldProjectControllerV2Api | None = None
        self._custom_field_value_project_api: CustomFieldValueProjectControllerApi | None = None
        self._is_entered = False

    @classmethod
    def from_env(cls, project: int | None = None, timeout: float = 30.0) -> AllureClient:
        """Initialize AllureClient from environment variables.

        Expects:
            ALLURE_ENDPOINT: The base URL of the Allure TestOps instance.
            ALLURE_API_TOKEN: The API token for authentication.
            ALLURE_PROJECT_ID: The target project ID.

        Args:
            project: Optional target Allure TestOps project ID to override the one from environment variables.
            timeout: Request timeout in seconds (default: 30.0)

        Returns:
            An initialized AllureClient instance.

        Raises:
            KeyError: If required environment variables are missing.
            ValueError: If settings validation fails.
        """
        if not settings.ALLURE_ENDPOINT:
            raise KeyError("ALLURE_ENDPOINT is not set in environment or config")
        if not settings.ALLURE_API_TOKEN:
            raise KeyError("ALLURE_API_TOKEN is not set in environment or config")

        if not isinstance(settings.ALLURE_PROJECT_ID, int) or settings.ALLURE_PROJECT_ID <= 0:
            raise ValueError("ALLURE_PROJECT_ID must be a positive integer")

        if project:
            p = project
        else:
            p = settings.ALLURE_PROJECT_ID

        return cls(
            base_url=settings.ALLURE_ENDPOINT,
            token=settings.ALLURE_API_TOKEN,
            project=p,
            timeout=timeout,
        )

    def set_project(self, project: int) -> None:
        self._project = project

    def get_project(self) -> int:
        return self._project

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
            self._test_case_custom_field_api = TestCaseCustomFieldControllerApi(self._api_client)
            self._custom_field_api = CustomFieldControllerApi(self._api_client)
            self._custom_field_project_api = CustomFieldProjectControllerApi(self._api_client)
            self._custom_field_project_v2_api = CustomFieldProjectControllerV2Api(self._api_client)
            self._custom_field_value_project_api = CustomFieldValueProjectControllerApi(self._api_client)

    @property
    def api_client(self) -> ApiClient:
        """Get the underlying ApiClient instance.

        Raises:
            RuntimeError: If the client has not been initialized (entered with).
        """
        if self._api_client is None:
            raise RuntimeError("AllureClient must be used as an async context manager")
        return self._api_client

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
    ) -> TestCaseCustomFieldControllerApi: ...

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
        self, attr_name: Literal["_custom_field_value_project_api"], *, error_name: str | None = None
    ) -> CustomFieldValueProjectControllerApi: ...

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

    async def _call_api_raw(self, coro: Awaitable[httpx.Response]) -> httpx.Response:
        try:
            return await coro
        except ApiException as e:
            self._handle_api_exception(e)
            raise

    @staticmethod
    def _extract_response_data(response: httpx.Response) -> dict[str, object]:
        if not 200 <= response.status_code <= 299:
            raise ApiException(status=response.status_code, reason=response.reason_phrase, body=response.text)
        data = response.json()
        if isinstance(data, dict):
            return data
        raise ApiException(status=response.status_code, reason=response.reason_phrase, body=response.text)

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
        raw_created_step_id = data.get("createdStepId")
        created_step_id = raw_created_step_id if isinstance(raw_created_step_id, int) else None
        return ScenarioStepCreatedResponseDto.model_construct(
            created_step_id=created_step_id,
        )

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

        from src.client.generated.models.custom_field_value_dto import CustomFieldValueDto

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

    async def delete_scenario_step(self, step_id: int) -> None:
        """Delete a scenario step.

        Args:
            step_id: ID of the step to delete.

        Raises:
            AllureAPIError: If the API request fails.
        """
        scenario_api = await self._get_api("_scenario_api")
        await self._call_api(
            scenario_api.delete_by_id1(
                id=step_id,
                _request_timeout=self._timeout,
            )
        )

    async def get_test_case(self, test_case_id: int) -> TestCaseDto:
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
        # print(f"DEBUG Initial Raw Normalized Scenario: {raw_data}")
        return self._denormalize_to_v2_from_dict(raw_data)

    @staticmethod
    def _denormalize_to_v2_from_dict(raw: dict[str, object]) -> TestCaseScenarioV2Dto:
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
        def build_steps(step_ids: list[int]) -> list[SharedStepScenarioDtoStepsInner]:
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

                    # Build BodyStepDtoWithSteps
                    steps_list.append(
                        SharedStepScenarioDtoStepsInner(
                            actual_instance=BodyStepDtoWithSteps.model_construct(
                                type="BodyStepDto",
                                body=body,
                                body_json=None,  # Skip complex rich-text
                                steps=child_steps,
                                id=sid,
                            )
                        )
                    )
            return steps_list

        final_steps = build_steps(root_children)
        return TestCaseScenarioV2Dto(steps=final_steps)

    async def delete_test_case(self, test_case_id: int) -> None:
        """Permanently delete a test case from the system.

        Args:
            test_case_id: The ID of the test case to remove.

        Raises:
            AllureAPIError: If the API request fails.
        """
        test_case_api = await self._get_api("_test_case_api")
        await self._call_api(test_case_api.delete13(id=test_case_id))

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
