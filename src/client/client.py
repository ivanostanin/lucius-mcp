"""Async HTTP client for Allure TestOps API."""

import time
import typing

import httpx
from pydantic import SecretStr

from .exceptions import (
    AllureAPIError,
    AllureAuthError,
    AllureNotFoundError,
    AllureRateLimitError,
    AllureValidationError,
)
from .models import AttachmentRow, TestCaseCreateV2Dto, TestCaseOverviewDto

type RequestFiles = (
    typing.Mapping[
        str,
        typing.IO[bytes]
        | bytes
        | str
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


class AllureClient:
    """Async client for Allure TestOps API.

    Usage:
        async with AllureClient(base_url, token) as client:
            cases = await client.list_test_cases(project_id=123)
    """

    def __init__(
        self,
        base_url: str,
        token: SecretStr,
        timeout: float = 30.0,
    ) -> None:
        """Initialize AllureClient.

        Args:
            base_url: Allure TestOps instance base URL (e.g., https://allure.example.com)
            token: API token (will be exchanged for JWT Bearer token)
            timeout: Request timeout in seconds (default: 30.0)
        """
        self._base_url = base_url.rstrip("/")
        self._token = token
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None
        self._jwt_token: str | None = None
        self._token_expires_at: float | None = None

    async def _get_jwt_token(self) -> str:
        """Exchange API token for JWT Bearer token.

        Returns:
            JWT access token string.

        Raises:
            AllureAuthError: If token exchange fails.
        """
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
                expires_in: int = data.get("expires_in", 3600)  # Default 1 hour
                self._jwt_token = access_token
                # Refresh 60 seconds before expiry to avoid race conditions
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
        """Ensure the JWT token is valid, refreshing if expired."""
        if self._token_expires_at is None or time.time() >= self._token_expires_at:
            new_token = await self._get_jwt_token()
            if self._client:
                self._client.headers["Authorization"] = f"Bearer {new_token}"

    async def __aenter__(self) -> AllureClient:
        """Enter async context manager."""
        jwt_token = await self._get_jwt_token()
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={"Authorization": f"Bearer {jwt_token}"},
            timeout=self._timeout,
        )
        return self

    async def __aexit__(self, *args: object) -> None:
        """Exit async context manager."""
        if self._client:
            await self._client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        json: object | None = None,
        params: dict[str, str | int | float | bool | None] | None = None,
        headers: dict[str, str] | None = None,
        files: RequestFiles | None = None,
    ) -> httpx.Response:
        """Make HTTP request with error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path (relative to base_url)
            json: JSON body data
            params: Query parameters
            headers: Additional headers
            files: Files for multipart upload

        Returns:
            httpx.Response: The HTTP response

        Raises:
            AllureNotFoundError: Resource not found (404)
            AllureValidationError: Request validation failed (400)
            AllureAuthError: Authentication failed (401, 403)
            AllureRateLimitError: Rate limit exceeded (429)
            AllureAPIError: Other API errors
        """
        if not self._client:
            msg = "Client not initialized. Use 'async with AllureClient(...)' context manager."
            raise AllureAPIError(msg)

        await self._ensure_valid_token()

        try:
            response = await self._client.request(
                method,
                path,
                json=json,
                params=params,
                headers=headers,
                files=files,
            )
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            body = e.response.text

            if status == 404:
                raise AllureNotFoundError(
                    f"Resource not found: {path}",
                    status_code=status,
                    response_body=body,
                ) from e
            if status == 400:
                raise AllureValidationError(
                    f"Validation error: {body}",
                    status_code=status,
                    response_body=body,
                ) from e
            if status in (401, 403):
                raise AllureAuthError(
                    f"Authentication failed: {body}",
                    status_code=status,
                    response_body=body,
                ) from e
            if status == 429:
                raise AllureRateLimitError(
                    "Rate limit exceeded",
                    status_code=status,
                    response_body=body,
                ) from e

            raise AllureAPIError(
                f"API request failed: {body}",
                status_code=status,
                response_body=body,
            ) from e
        except httpx.RequestError as e:
            raise AllureAPIError(f"Request error: {e}") from e

    # ==========================================
    # Test Case operations (Story 1.3, 1.4, 1.5)
    # ==========================================

    async def create_test_case(self, project_id: int, data: TestCaseCreateV2Dto) -> TestCaseOverviewDto:
        """Create a new test case.

        Args:
            project_id: Project ID
            data: Test case creation data

        Returns:
            Created test case
        """
        response = await self._request(
            "POST",
            "/api/testcase",
            json=data.model_dump(mode="json", exclude_none=True, by_alias=True),
            params={"projectId": project_id},
        )
        return TestCaseOverviewDto.model_validate(response.json())

    async def upload_attachment(
        self,
        project_id: int,
        files: RequestFiles,
    ) -> list[AttachmentRow]:
        """Upload attachments to Allure TestOps.

        Args:
            project_id: Project ID
            files: Dictionary or list of tuples for multipart upload.
                   Format: {'file': ('filename', b'content', 'content_type')}

        Returns:
            List of uploaded attachments info
        """
        # Allure TestOps expects 'file' field for uploads
        response = await self._request(
            "POST",
            "/api/attachment",
            params={"projectId": project_id},
            files=files,
        )
        return [AttachmentRow.model_validate(item) for item in response.json()]

    async def get_test_case(self, test_case_id: int) -> object:
        """Retrieve a test case by ID.

        Args:
            test_case_id: Test case ID

        Returns:
            Test case data

        Note:
            Implementation in Story 3.2
        """
        raise NotImplementedError("To be implemented in Story 3.2")

    async def update_test_case(self, test_case_id: int, data: object) -> object:
        """Update an existing test case.

        Args:
            test_case_id: Test case ID
            data: Updated test case data

        Returns:
            Updated test case

        Note:
            Implementation in Story 1.4
        """
        raise NotImplementedError("To be implemented in Story 1.4")

    async def delete_test_case(self, test_case_id: int) -> None:
        """Delete a test case.

        Args:
            test_case_id: Test case ID

        Note:
            Implementation in Story 1.5
        """
        raise NotImplementedError("To be implemented in Story 1.5")

    # ==========================================
    # Shared Step operations (Story 2.1, 2.2, 2.3)
    # ==========================================

    async def create_shared_step(self, project_id: int, data: object) -> object:
        """Create a new shared step.

        Args:
            project_id: Project ID
            data: Shared step creation data

        Returns:
            Created shared step

        Note:
            Implementation in Story 2.1
        """
        raise NotImplementedError("To be implemented in Story 2.1")

    async def list_shared_steps(self, project_id: int) -> list[object]:
        """List all shared steps in a project.

        Args:
            project_id: Project ID

        Returns:
            List of shared steps

        Note:
            Implementation in Story 2.1
        """
        raise NotImplementedError("To be implemented in Story 2.1")

    async def update_shared_step(self, step_id: int, data: object) -> object:
        """Update a shared step.

        Args:
            step_id: Shared step ID
            data: Updated shared step data

        Returns:
            Updated shared step

        Note:
            Implementation in Story 2.2
        """
        raise NotImplementedError("To be implemented in Story 2.2")

    async def delete_shared_step(self, step_id: int) -> None:
        """Delete a shared step.

        Args:
            step_id: Shared step ID

        Note:
            Implementation in Story 2.2
        """
        raise NotImplementedError("To be implemented in Story 2.2")

    # ==========================================
    # Search operations (Story 3.1, 3.2, 3.3)
    # ==========================================

    async def list_test_cases(self, project_id: int, **filters: object) -> list[object]:
        """List test cases in a project with optional filters.

        Args:
            project_id: Project ID
            **filters: Optional filter parameters

        Returns:
            List of test case summaries

        Note:
            Implementation in Story 3.1
        """
        raise NotImplementedError("To be implemented in Story 3.1")

    async def search_test_cases(self, project_id: int, query: str) -> list[object]:
        """Search test cases by name or tag.

        Args:
            project_id: Project ID
            query: Search query string

        Returns:
            List of matching test cases

        Note:
            Implementation in Story 3.3
        """
        raise NotImplementedError("To be implemented in Story 3.3")
