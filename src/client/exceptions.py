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


class AllureAuthError(AuthenticationError):
    """Authentication failed (401/403)."""


class AllureRateLimitError(AllureClientError):
    """Rate limit exceeded (429)."""


__all__ = [
    "AllureAPIError",
    "AllureClientError",
    "AllureNotFoundError",
    "AllureValidationError",
    "AllureAuthError",
    "AllureRateLimitError",
]
