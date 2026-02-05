"""Custom exceptions for Allure TestOps API interactions."""

from src.utils.error import (
    AllureAPIError,
    AuthenticationError,
    ResourceNotFoundError,
    ValidationError,
)


class AllureClientError(AllureAPIError):
    """Base exception for client-side errors."""


class AllureNotFoundError(ResourceNotFoundError):
    """Resource not found (404)."""


class AllureValidationError(ValidationError):
    """Validation failed (400)."""


class TestCaseNotFoundError(ResourceNotFoundError):
    """Resource not found for a specific test case."""

    def __init__(
        self,
        test_case_id: int,
        status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        suggestions = [
            "Verify the test case ID",
            "Use list_test_cases to find valid IDs",
            "Check access to the project containing this test case",
        ]
        super().__init__(
            message=f"Test Case ID {test_case_id} not found",
            status_code=status_code,
            response_body=response_body,
            suggestions=suggestions,
        )


class LaunchNotFoundError(ResourceNotFoundError):
    """Resource not found for a specific launch."""

    def __init__(
        self,
        launch_id: int,
        status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        suggestions = [
            "Verify the launch ID",
            "Use list_launches to find valid IDs",
            "Check access to the project containing this launch",
        ]
        super().__init__(
            message=f"Launch ID {launch_id} not found",
            status_code=status_code,
            response_body=response_body,
            suggestions=suggestions,
        )


class AllureAuthError(AuthenticationError):
    """Authentication failed (401/403)."""


class AllureRateLimitError(AllureClientError):
    """Rate limit exceeded (429)."""


__all__ = [
    "AllureAPIError",
    "AllureAuthError",
    "AllureClientError",
    "AllureNotFoundError",
    "AllureRateLimitError",
    "AllureValidationError",
    "LaunchNotFoundError",
    "TestCaseNotFoundError",
]
