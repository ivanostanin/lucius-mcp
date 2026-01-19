import inspect

from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from starlette.requests import Request
from starlette.responses import PlainTextResponse


class AllureAPIError(Exception):
    """Base exception for Allure TestOps MCP logic."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
        suggestions: list[str] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body
        self.suggestions = suggestions or []


class ResourceNotFoundError(AllureAPIError):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
        suggestions: list[str] | None = None,
    ):
        if not suggestions:
            suggestions = [
                "Check if the ID is correct",
                "Verify potential access permissions",
                "List dependencies to ensure existence",
            ]
        super().__init__(message, status_code, response_body, suggestions)


class TestCaseNotFoundError(ResourceNotFoundError):
    """Raised when a test case cannot be found."""

    def __init__(
        self,
        test_case_id: int,
        status_code: int | None = None,
        response_body: str | None = None,
    ):
        message = f"Test Case ID {test_case_id} not found"
        suggestions = [
            "Verify the test case ID",
            "Use list_test_cases to find valid IDs",
            "Check access to the project containing this test case",
        ]
        super().__init__(message, status_code, response_body, suggestions)


class ValidationError(AllureAPIError):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
        suggestions: list[str] | None = None,
    ):
        if not suggestions:
            suggestions = ["Check format requirements", "Ensure required fields are present"]
        super().__init__(message, status_code, response_body, suggestions)


class AuthenticationError(AllureAPIError):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
        suggestions: list[str] | None = None,
    ):
        if not suggestions:
            suggestions = ["Check ALLURE_API_TOKEN environment variable", "Verify token permissions"]
        super().__init__(message, status_code, response_body, suggestions)


async def agent_hint_handler(request: Request, exc: Exception) -> PlainTextResponse:
    """
    Global exception handler that converts exceptions into human-readable Agent Hints.
    Returns text/plain responses instead of JSON to be LLM-friendly.
    """
    if isinstance(exc, PydanticValidationError):
        return await _handle_pydantic_error(exc, request)

    if isinstance(exc, AllureAPIError):
        return _handle_allure_error(exc)

    return _handle_generic_error(exc)


async def _handle_pydantic_error(exc: PydanticValidationError, request: Request) -> PlainTextResponse:
    error_lines = ["❌ Validation Error: Invalid Input", "", "Details:"]
    for error in exc.errors():
        # Extract field loc
        loc = " -> ".join(str(x) for x in error.get("loc", []))
        msg = error.get("msg", "Unknown error")
        ctx = error.get("ctx", {})

        # Format friendly message
        if "enum_values" in ctx:
            msg += f" (allowed: {', '.join(str(v) for v in ctx['enum_values'])})"

        error_lines.append(f"- Field '{loc}': {msg}")

    # Actionable Error Handling: Schema Hints
    found_models = _find_models_for_hint(exc, request)

    if found_models:
        from src.utils.schema_hint import generate_schema_hint

        # Use the first found model for now - usually the body
        hint = generate_schema_hint(found_models[0])
        if hint:
            error_lines.append("")
            error_lines.append(hint)

    error_lines.append("\nHint: Please correct the fields listed above and try again.")
    content = "\n".join(error_lines)
    return PlainTextResponse(content, status_code=400)


def _find_models_for_hint(exc: PydanticValidationError, request: Request) -> list[type[BaseModel]]:
    found_models = []

    # 1. Try to get model from exception (Pydantic V1/Context)
    if hasattr(exc, "model") and exc.model:
        found_models.append(exc.model)

    # 2. Inspect endpoint signature (FastMCP/Starlette)
    if not found_models and "endpoint" in request.scope:
        endpoint = request.scope["endpoint"]
        try:
            # If endpoint is a partial or wrapper, try to unwrap or inspect signature directly
            sig = inspect.signature(endpoint)
            for param in sig.parameters.values():
                # Check if annotation is a Pydantic Model
                if inspect.isclass(param.annotation) and issubclass(param.annotation, BaseModel):
                    found_models.append(param.annotation)
        except (ValueError, TypeError):
            # Introspection might fail on some adjustables/wrappers, e.g. built-ins
            pass

    return found_models


def _handle_allure_error(exc: AllureAPIError) -> PlainTextResponse:
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


def _handle_generic_error(exc: Exception) -> PlainTextResponse:
    # Fallback for generic exceptions
    # We strip detailed stack traces but provide the error message
    msg = f"❌ Unexpected Error: {exc!s}\n\nPlease check the logs for more details."
    return PlainTextResponse(msg, status_code=500)
