"""Custom exceptions for Allure TestOps API interactions."""


class AllureAPIError(Exception):
    """Base exception for all Allure API errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        """Initialize AllureAPIError.

        Args:
            message: Human-readable error message
            status_code: HTTP status code if available
            response_body: Response body from the API for debugging
        """
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class AllureNotFoundError(AllureAPIError):
    """Resource not found (404)."""


class AllureValidationError(AllureAPIError):
    """Validation failed (400)."""


class AllureAuthError(AllureAPIError):
    """Authentication failed (401/403)."""


class AllureRateLimitError(AllureAPIError):
    """Rate limit exceeded (429)."""
