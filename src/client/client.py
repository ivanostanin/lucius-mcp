"""Async HTTP client for Allure TestOps API.

This module provides a high-level wrapper around the auto-generated Allure TestOps
client, adding features like token management, automatic refresh, and
standardized error handling.
"""

import time
from typing import Any

import httpx
from pydantic import SecretStr

from src.utils.config import settings
from src.utils.logger import get_logger

from .exceptions import (
    AllureAPIError,
    AllureAuthError,
    AllureNotFoundError,
    AllureRateLimitError,
    AllureValidationError,
)
from .generated.api.test_case_attachment_controller_api import TestCaseAttachmentControllerApi
from .generated.api.test_case_controller_api import TestCaseControllerApi
from .generated.api.test_case_overview_controller_api import TestCaseOverviewControllerApi
from .generated.api.test_case_scenario_controller_api import TestCaseScenarioControllerApi
from .generated.api_client import ApiClient
from .generated.configuration import Configuration
from .generated.exceptions import (
    ApiException,
)
from .generated.models.attachment_step_dto import AttachmentStepDto
from .generated.models.body_step_dto import BodyStepDto
from .generated.models.custom_field_value_with_cf_dto import CustomFieldValueWithCfDto
from .generated.models.scenario_step_create_dto import ScenarioStepCreateDto
from .generated.models.scenario_step_created_response_dto import ScenarioStepCreatedResponseDto
from .generated.models.shared_step_scenario_dto_steps_inner import SharedStepScenarioDtoStepsInner
from .generated.models.test_case_attachment_row_dto import TestCaseAttachmentRowDto
from .generated.models.test_case_create_v2_dto import TestCaseCreateV2Dto
from .generated.models.test_case_dto import TestCaseDto
from .generated.models.test_case_overview_dto import TestCaseOverviewDto
from .generated.models.test_case_patch_v2_dto import TestCasePatchV2Dto
from .generated.models.test_case_scenario_dto import TestCaseScenarioDto
from .generated.models.test_case_scenario_v2_dto import TestCaseScenarioV2Dto


# Subclasses to add missing fields to generated models
class TestCaseDtoWithCF(TestCaseDto):
    """Subclass to support custom_fields access."""

    custom_fields: list[CustomFieldValueWithCfDto] | None = None


class BodyStepDtoWithSteps(BodyStepDto):
    """Subclass to support nested steps."""

    steps: list[SharedStepScenarioDtoStepsInner] | None = None


class AttachmentStepDtoWithName(AttachmentStepDto):
    """Subclass to support name attribute."""

    name: str | None = None


logger = get_logger(__name__)

# Export models for convenience
__all__ = [
    "AllureClient",
    "AttachmentStepDtoWithName",
    "BodyStepDtoWithSteps",
    "ScenarioStepCreateDto",
    "ScenarioStepCreatedResponseDto",
    "SharedStepScenarioDtoStepsInner",
    "TestCaseAttachmentRowDto",
    "TestCaseCreateV2Dto",
    "TestCaseDto",
    "TestCaseDtoWithCF",
    "TestCaseOverviewDto",
    "TestCasePatchV2Dto",
    "TestCaseScenarioDto",
    "TestCaseScenarioV2Dto",
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
            token=SecretStr("your-api-token")
        ) as client:
            # client is initialized and authenticated
            pass
        ```
    """

    def __init__(
        self,
        base_url: str,
        token: SecretStr,
        timeout: float = 30.0,
    ) -> None:
        """Initialize AllureClient.

        Args:
            base_url: Allure TestOps instance base URL
            token: API token (will be exchanged for JWT Bearer token)
            timeout: Request timeout in seconds (default: 30.0)
        """
        if not base_url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid base_url scheme: {base_url}. Must start with http:// or https://")

        self._base_url = base_url.rstrip("/")
        self._token = token
        self._timeout = timeout
        self._jwt_token: str | None = None
        self._token_expires_at: float | None = None
        self._csrf_token: str | None = None

        # Generated client components
        self._api_client: ApiClient | None = None
        self._test_case_api: TestCaseControllerApi | None = None
        self._attachment_api: TestCaseAttachmentControllerApi | None = None
        self._scenario_api: TestCaseScenarioControllerApi | None = None
        self._test_case_scenario_api: TestCaseScenarioControllerApi | None = None
        self._overview_api: TestCaseOverviewControllerApi
        self._is_entered = False

    @classmethod
    def from_env(cls, timeout: float = 30.0) -> AllureClient:
        """Initialize AllureClient from environment variables.

        Expects:
            ALLURE_ENDPOINT: The base URL of the Allure TestOps instance.
            ALLURE_TOKEN: The API token for authentication.

        Returns:
            An initialized AllureClient instance.

        Raises:
            KeyError: If required environment variables are missing.
            ValueError: If settings validation fails.
        """
        if not settings.ALLURE_API_TOKEN:
            raise KeyError("ALLURE_API_TOKEN is not set in environment or config")

        return cls(
            base_url=settings.ALLURE_ENDPOINT,
            token=settings.ALLURE_API_TOKEN,
            timeout=timeout,
        )

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
            self._attachment_api = TestCaseAttachmentControllerApi(self._api_client)
            self._scenario_api = TestCaseScenarioControllerApi(self._api_client)
            self._test_case_scenario_api = TestCaseScenarioControllerApi(self._api_client)
            self._overview_api = TestCaseOverviewControllerApi(self._api_client)

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

    # ==========================================
    # Test Case operations
    # ==========================================

    async def create_test_case(self, project_id: int, data: TestCaseCreateV2Dto) -> TestCaseOverviewDto:
        """Create a new test case in the specified project.

        Args:
            project_id: Target project ID.
            data: Test case definition (name, scenario, etc.).

        Returns:
            The created test case overview.

        Raises:
            AllureNotFoundError: If project doesn't exist.
            AllureValidationError: If input data fails validation.
            AllureAuthError: If unauthorized.
            AllureAPIError: If the server returns an error.
        """
        if not self._is_entered:
            raise AllureAPIError("Client not initialized. Use 'async with AllureClient(...)'")

        await self._ensure_valid_token()
        if self._test_case_api is None:
            # This should not happen if _is_entered is True
            raise AllureAPIError("Internal error: test_case_api not initialized")

        # Ensure project_id is set in the body as required by the model
        if hasattr(data, "project_id") and not data.project_id:
            data.project_id = project_id

        try:
            # create13 is the generated method name for POST /api/testcase
            response = await self._test_case_api.create13(test_case_create_v2_dto=data, _request_timeout=self._timeout)
            # Switch view from TestCaseDto to TestCaseOverviewDto
            # Since fields are compatible (mostly optional), we can use model_dump/validate
            return TestCaseOverviewDto.model_validate(response.model_dump())
        except ApiException as e:
            self._handle_api_exception(e)
            raise  # Should not be reached

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
        if not self._is_entered:
            raise AllureAPIError("Client not initialized. Use 'async with AllureClient(...)'")

        await self._ensure_valid_token()
        if self._attachment_api is None:
            raise AllureAPIError("Internal error: attachment_api not initialized")

        try:
            return await self._attachment_api.create16(
                test_case_id=test_case_id,
                file=file_data,
                _request_timeout=self._timeout,
            )
        except ApiException as e:
            self._handle_api_exception(e)
            raise

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
        if not self._is_entered:
            raise AllureAPIError("Client not initialized. Use 'async with AllureClient(...)'")

        await self._ensure_valid_token()
        if self._scenario_api is None:
            raise AllureAPIError("Internal error: scenario_api not initialized")

        # Ensure test_case_id is set
        if step.test_case_id is None:
            step = ScenarioStepCreateDto(
                test_case_id=test_case_id,
                body=step.body,
                body_json=step.body_json,
                attachment_id=step.attachment_id,
                shared_step_id=step.shared_step_id,
                parent_id=step.parent_id,
            )

        try:
            # We use without_preload_content to skip the problematic generated
            # deserialization of NormalizedScenarioDto, which fails due to
            # ambiguous oneOf schema matching for attachments.
            response = await self._scenario_api.create15_without_preload_content(
                scenario_step_create_dto=step,
                after_id=after_id,
                with_expected_result=with_expected_result,
                _request_timeout=self._timeout,
            )

            # response is an httpx.Response object. Check for success status.
            if not 200 <= response.status_code <= 299:
                # Manually raise ApiException as the without_preload variant doesn't do it.
                raise ApiException(status=response.status_code, reason=response.reason_phrase, body=response.text)

            data = response.json()
            # Use model_construct to bypass validation of the scenario field while
            # providing the created_step_id needed by TestCaseService.
            return ScenarioStepCreatedResponseDto.model_construct(
                created_step_id=data.get("createdStepId"),
            )
        except ApiException as e:
            self._handle_api_exception(e)
            raise  # Should not be reached

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
        if not self._is_entered:
            raise AllureAPIError("Client not initialized. Use 'async with AllureClient(...)'")

        await self._ensure_valid_token()
        if self._test_case_api is None:
            raise AllureAPIError("Internal error: test_case_api not initialized")

        try:
            # Use _without_preload_content to get raw JSON for missing fields (like customFields)
            # Actually, for customFields we now use get_overview
            response = await self._test_case_api.find_one11_without_preload_content(
                id=test_case_id, _request_timeout=self._timeout
            )
            if not 200 <= response.status_code <= 299:
                raise ApiException(status=response.status_code, reason=response.reason_phrase, body=response.text)

            raw_data = response.json()
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
        except ApiException as e:
            self._handle_api_exception(e)
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
        if not self._is_entered:
            raise AllureAPIError("Client not initialized. Use 'async with AllureClient(...)'")

        await self._ensure_valid_token()
        if self._test_case_api is None:
            raise AllureAPIError("Internal error: test_case_api not initialized")

        try:
            print(f"DEBUG Payload: {data.to_json()}")
            return await self._test_case_api.patch13(
                id=test_case_id,
                test_case_patch_v2_dto=data,
                _request_timeout=self._timeout,
            )
        except ApiException as e:
            self._handle_api_exception(e)
            raise

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
        if not self._is_entered:
            raise AllureAPIError("Client not initialized. Use 'async with AllureClient(...)'")

        await self._ensure_valid_token()
        if self._test_case_scenario_api is None:
            raise AllureAPIError("Internal error: test_case_scenario_api not initialized")

        try:
            # Use _without_preload_content to bypass broken oneOf deserialization
            response = await self._test_case_scenario_api.get_normalized_scenario_without_preload_content(
                id=test_case_id, _request_timeout=self._timeout
            )

            if not 200 <= response.status_code <= 299:
                raise ApiException(status=response.status_code, reason=response.reason_phrase, body=response.text)

            raw_data = response.json()
            print(f"DEBUG Initial Raw Normalized Scenario: {raw_data}")
            return self._denormalize_to_v2_from_dict(raw_data)
        except ApiException as e:
            self._handle_api_exception(e)
            raise

    def _denormalize_to_v2_from_dict(self, raw: dict[str, Any]) -> TestCaseScenarioV2Dto:
        """Convert a raw NormalizedScenarioDto dict into a TestCaseScenarioV2Dto tree.

        This bypasses the generated from_dict which has broken oneOf deserialization.
        """
        root = raw.get("root")
        if not root:
            return TestCaseScenarioV2Dto(steps=[])

        root_children = root.get("children")
        if not root_children:
            return TestCaseScenarioV2Dto(steps=[])

        scenario_steps = raw.get("scenarioSteps", {})

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
                if attachment_id:
                    # Build AttachmentStepDtoWithName using model_construct to bypass validation
                    steps_list.append(
                        SharedStepScenarioDtoStepsInner(
                            actual_instance=AttachmentStepDtoWithName.model_construct(
                                type="AttachmentStepDto", attachment_id=attachment_id, name=step_def.get("name")
                            )
                        )
                    )
                else:
                    # It's a Body Step
                    body = step_def.get("body")
                    child_ids = step_def.get("children") or []
                    child_steps = build_steps(child_ids) if child_ids else None

                    # Build BodyStepDtoWithSteps using model_construct to bypass validation
                    steps_list.append(
                        SharedStepScenarioDtoStepsInner(
                            actual_instance=BodyStepDtoWithSteps.model_construct(
                                type="BodyStepDto",
                                body=body,
                                body_json=None,  # Skip complex rich-text
                                steps=child_steps,
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
        if not self._is_entered:
            raise AllureAPIError("Client not initialized. Use 'async with AllureClient(...)'")

        await self._ensure_valid_token()
        if self._test_case_api is None:
            raise AllureAPIError("Internal error: test_case_api not initialized")

        try:
            await self._test_case_api.delete13(id=test_case_id)
        except ApiException as e:
            self._handle_api_exception(e)
            raise  # Should not be reached
