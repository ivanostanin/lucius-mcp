from starlette.requests import Request
from starlette.responses import PlainTextResponse


class AllureAPIError(Exception):
    """Base exception for Allure TestOps MCP logic."""

    def __init__(self, message: str, suggestions: list[str] | None = None):
        super().__init__(message)
        self.message = message
        self.suggestions = suggestions or []


class ResourceNotFoundError(AllureAPIError):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str, suggestions: list[str] | None = None):
        if not suggestions:
            suggestions = [
                "Check if the ID is correct",
                "Verify potential access permissions",
                "List dependencies to ensure existence",
            ]
        super().__init__(message, suggestions)


class ValidationError(AllureAPIError):
    """Raised when input validation fails."""

    def __init__(self, message: str, suggestions: list[str] | None = None):
        if not suggestions:
            suggestions = ["Check format requirements", "Ensure required fields are present"]
        super().__init__(message, suggestions)


class AuthenticationError(AllureAPIError):
    """Raised when authentication fails."""

    def __init__(self, message: str, suggestions: list[str] | None = None):
        if not suggestions:
            suggestions = ["Check ALLURE_API_TOKEN environment variable", "Verify token permissions"]
        super().__init__(message, suggestions)


async def agent_hint_handler(request: Request, exc: Exception) -> PlainTextResponse:
    """
    Global exception handler that converts exceptions into human-readable Agent Hints.
    Returns text/plain responses instead of JSON to be LLM-friendly.
    """
    if isinstance(exc, AllureAPIError):
        status_code = 500
        if isinstance(exc, ResourceNotFoundError):
            status_code = 404
        elif isinstance(exc, ValidationError):
            status_code = 400
        elif isinstance(exc, AuthenticationError):
            status_code = 401

        content = f"❌ Error: {exc.message}\n\n"
        if exc.suggestions:
            content += "Suggestions:\n"
            for suggestion in exc.suggestions:
                content += f"- {suggestion}\n"

        return PlainTextResponse(content, status_code=status_code)

    # Fallback for generic exceptions
    # We strip detailed stack traces but provide the error message
    msg = f"❌ Unexpected Error: {exc!s}\n\nPlease check the logs for more details."
    return PlainTextResponse(msg, status_code=500)
