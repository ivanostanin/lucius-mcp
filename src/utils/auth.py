"""Authentication context helpers."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import SecretStr

from src.utils.auth_resolution import resolve_auth_settings
from src.utils.error import AuthenticationError


@dataclass(frozen=True)
class AuthContext:
    """Authentication context for API operations.

    Supports both environment-based and runtime authentication.
    Runtime values take precedence over environment values.

    Attributes:
        api_token: The Allure TestOps API token (masked in logs).
        project_id: Optional default project ID for operations.
    """

    api_token: SecretStr
    project_id: int | None = None

    @classmethod
    def from_environment(cls) -> AuthContext:
        """Create context from resolved non-runtime auth configuration.

        Resolution order:
            environment variables -> saved CLI auth config -> defaults

        Raises:
            AuthenticationError: If ALLURE_API_TOKEN is not set.
        """
        resolved = resolve_auth_settings(include_endpoint=False)
        if not resolved.api_token:
            raise AuthenticationError(
                "No API token configured. Set ALLURE_API_TOKEN environment variable or provide api_token argument."
            )

        return cls(
            api_token=resolved.api_token,
            project_id=resolved.project_id,
        )

    def with_overrides(
        self,
        api_token: str | None = None,
        project_id: int | None = None,
    ) -> AuthContext:
        """Create new context with runtime overrides.

        Returns a new AuthContext with specified values overridden.
        Original context is not modified.

        Args:
            api_token: Override the API token.
            project_id: Override the project ID.

        Returns:
            New AuthContext with overrides applied.
        """
        return AuthContext(
            api_token=SecretStr(api_token) if api_token else self.api_token,
            project_id=project_id if project_id is not None else self.project_id,
        )


def get_auth_context(
    api_token: str | None = None,
    project_id: int | None = None,
) -> AuthContext:
    """Get authentication context with optional runtime overrides.

    Resolution order:
    1. Runtime arguments
    2. Environment variables
    3. Saved CLI auth config
    4. Defaults

    This function is stateless - each call creates a fresh context.
    Overrides from one call do NOT affect subsequent calls.

    Args:
        api_token: Optional runtime API token override.
        project_id: Optional runtime project ID override.

    Returns:
        AuthContext ready for API operations.

    Raises:
        AuthenticationError: If no token available from any source.
    """
    resolved = resolve_auth_settings(
        api_token=api_token,
        project_id=project_id,
        include_endpoint=False,
    )
    if not resolved.api_token:
        raise AuthenticationError(
            "Authentication required. Either:\n"
            "1. Set ALLURE_API_TOKEN environment variable, or\n"
            "2. Provide api_token argument to this tool"
        ) from None

    return AuthContext(
        api_token=resolved.api_token,
        project_id=resolved.project_id,
    )
