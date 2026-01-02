"""Async HTTP client for Allure TestOps API.

This module provides a high-level wrapper around the auto-generated Allure TestOps
client, adding features like token management, automatic refresh, and
standardized error handling.
"""

import json
import time
import typing

import httpx
from pydantic import SecretStr

from src.utils.config import settings

from .exceptions import (
    AllureAPIError,
    AllureAuthError,
    AllureNotFoundError,
    AllureRateLimitError,
    AllureValidationError,
)
from .generated.api.test_case_attachment_controller_api import TestCaseAttachmentControllerApi
from .generated.api.test_case_controller_api import TestCaseControllerApi
from .generated.api_client import ApiClient
from .generated.configuration import Configuration
from .generated.exceptions import (
    ApiException,
)
from .generated.models.attachment_row import AttachmentRow
from .generated.models.test_case_create_v2_dto import TestCaseCreateV2Dto
from .generated.models.test_case_overview_dto import TestCaseOverviewDto

# Export models for convenience
__all__ = ["AllureClient", "AttachmentRow", "TestCaseCreateV2Dto", "TestCaseOverviewDto"]

type RequestFiles = (
    typing.Mapping[
        str,
        typing.IO[bytes]
        | bytes
        | str
        | tuple[str | None, typing.IO[bytes] | bytes | str]
        | tuple[str | None, typing.IO[bytes] | bytes | str]
        | tuple[str | None, typing.IO[bytes] | bytes | str, str | None]
        | tuple[str | None, typing.IO[bytes] | bytes | str, str | None, typing.Mapping[str, str]],
    ]
    | typing.Sequence[
        tuple[
            str,
            typing.IO[bytes]
            | bytes
            | str
            | tuple[str | None, typing.IO[bytes] | bytes | str]
            | tuple[str | None, typing.IO[bytes] | bytes | str, str | None]
            | tuple[str | None, typing.IO[bytes] | bytes | str, str | None, typing.Mapping[str, str]],
        ]
    ]
)
"""Complex type for files in httpx-style multipart requests."""


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

        # Generated client components
        self._api_client: ApiClient | None = None
        self._test_case_api: TestCaseControllerApi | None = None
        self._attachment_api: TestCaseAttachmentControllerApi | None = None
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

            # Re-initialize controllers
            self._test_case_api = TestCaseControllerApi(self._api_client)
            self._attachment_api = TestCaseAttachmentControllerApi(self._api_client)

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
        project_id: int,
        files: RequestFiles,
    ) -> list[AttachmentRow]:
        """Upload one or more attachments to a project.

        Args:
            project_id: Target project ID.
            files: Dictionary or list of tuples containing file data for multipart upload.

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
        if self._attachment_api is None or self._api_client is None:
            # This should not happen if _is_entered is True
            raise AllureAPIError("Internal error: attachment_api not initialized")

        # Using raw rest client for maximum compatibility with standard multipart/form-data.
        # Note: The generated client's high-level methods for file uploads are often
        # less flexible than direct pool manager requests.
        try:
            if self._api_client.rest_client.pool_manager is None:
                self._api_client.rest_client.pool_manager = self._api_client.rest_client._create_pool_manager()

            if self._api_client.rest_client.pool_manager is None:
                raise AllureAPIError("Failed to initialize pool manager")

            host = self._api_client.configuration.host
            token = self._jwt_token or (await self._get_jwt_token())

            response = await self._api_client.rest_client.pool_manager.request(
                "POST",
                f"{host}/api/attachment",
                params={"projectId": str(project_id)},
                files=files,
                headers={"Authorization": f"Bearer {token}"},
            )

            # Response might be bytes, parse if needed
            try:
                data = response.json()
            except json.JSONDecodeError:
                data = response.content

            if isinstance(data, bytes):
                data = json.loads(data)

            return [AttachmentRow.model_validate(item) for item in data]

        except ApiException as e:
            self._handle_api_exception(e)
            raise

    async def get_test_case(self, test_case_id: int) -> object:
        """Retrieve a specific test case by its ID.

        Args:
            test_case_id: The unique ID of the test case.

        Returns:
            The test case data.

        Raises:
            NotImplementedError: Currently a placeholder for future story.
        """
        raise NotImplementedError("To be implemented in Story 3.2")

    async def update_test_case(self, test_case_id: int, data: object) -> object:
        """Update an existing test case with new data.

        Args:
            test_case_id: The ID of the test case to update.
            data: The new data to apply.

        Returns:
            The updated test case overview.

        Raises:
            NotImplementedError: Currently a placeholder for future story.
        """
        raise NotImplementedError("To be implemented in Story 1.4")

    async def delete_test_case(self, test_case_id: int) -> None:
        """Permenantly delete a test case from the system.

        Args:
            test_case_id: The ID of the test case to remove.

        Raises:
            NotImplementedError: Currently a placeholder for future story.
        """
        raise NotImplementedError("To be implemented in Story 1.5")
