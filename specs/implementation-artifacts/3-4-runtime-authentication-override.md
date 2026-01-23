# Story 3.4: Runtime Authentication Override

Status: done

## Story

As an AI Agent,
I want to override the default authentication context (API Token, Project ID) at runtime,
so that I can operate across different projects or with different credentials within a single session.

## Acceptance Criteria

1. **Given** a tool call that requires authentication, **when** I provide `api_token` and/or `project_id` arguments directly, **then** these arguments are optional and override any environment variables or default configurations.
2. The operation is executed successfully with the provided runtime context.
3. Runtime overrides do NOT persist between tool calls (stateless).
4. Environment variable defaults are still used when runtime arguments are not provided.
5. Clear error hint when neither runtime nor environment authentication is available.
6. API tokens passed at runtime must be masked in all logs.
7. All tools still function correctly when runtime authentication is not configured.
8. **NFR11 / AC11 (E2E):** End-to-end tests run against a sandbox TestOps instance and validate:
   - runtime overrides are honored for a tool call,
   - runtime overrides are optional,
   - runtime overrides are supported for all tools,
   - environment defaults are used when overrides are absent,
   - overrides do not persist across calls,
   - errors are clear when no auth is available,
   - tests skip when sandbox credentials are not configured.

## Tasks / Subtasks

- [x] **Task 1: Implement AuthContext Model** (AC: #1, #3, #4)
  - [x] 1.1: Create `AuthContext` dataclass in `src/utils/auth.py`
  - [x] 1.2: Add `api_token` (SecretStr) and `project_id` (Optional[int]) fields
  - [x] 1.3: Implement `from_environment()` class method
  - [x] 1.4: Implement `with_overrides()` method for runtime values

- [x] **Task 2: Create get_auth_context Helper** (AC: #1, #4, #5)
  - [x] 2.1: Implement `get_auth_context()` function
  - [x] 2.2: Accept optional runtime overrides as parameters
  - [x] 2.3: Fall back to environment variables for unspecified values
  - [x] 2.4: Raise `AuthenticationError` if no token available

- [x] **Task 3: Integrate with Services** (AC: #1, #2)
  - [x] 3.1: Update `SearchService` to accept `AuthContext`
  - [x] 3.2: Update `CaseService` to accept `AuthContext`
  - [x] 3.3: Pass auth context to `AllureClient` on each request

- [x] **Task 4: Update All Tools** (AC: #1)
  - [x] 4.1: Add optional `api_token` parameter to all tools
  - [x] 4.2: Add optional `project_id` parameter where applicable
  - [x] 4.3: Document runtime override capability in docstrings

- [x] **Task 5: Secure Logging** (AC: #6)
  - [x] 5.1: Verify SecretStr masks token in __repr__ and __str__
  - [x] 5.2: Ensure no token leakage in error messages
  - [x] 5.3: Test log output for masked tokens

- [x] **Task 6: Unit Tests** (AC: #1-6)
  - [x] 6.1: Test runtime override takes precedence
  - [x] 6.2: Test environment fallback works
  - [x] 6.3: Test missing auth raises clear error
  - [x] 6.4: Test stateless behavior (overrides don't persist)
  - [x] 6.5: Test token masking in logs

- [x] **Task 7: E2E Tests for Runtime Auth** (AC: #7)
  - [x] 7.1: Add `tests/e2e/test_runtime_auth_override.py`
  - [x] 7.2: Validate runtime override precedence in a tool call
  - [x] 7.3: Validate stateless behavior across calls
  - [x] 7.4: Validate clear error when no auth configured
  - [x] 7.5: Skip gracefully when sandbox credentials are absent

## Dev Notes

### FR14 Coverage
This story addresses **FR14** (runtime auth override).

This story directly addresses **FR14**:
> Agents can override authentication context (Token, Project ID) via tool arguments at runtime.

Also addresses **NFR5**:
> API Tokens passed via environment variables must be masked in all logs.

### AuthContext Implementation

```python
# src/utils/auth.py
from dataclasses import dataclass
from typing import Optional
import os
from pydantic import SecretStr

class AuthenticationError(Exception):
    """Raised when authentication is not configured."""
    pass

@dataclass
class AuthContext:
    """Authentication context for API operations.
    
    Supports both environment-based and runtime authentication.
    Runtime values always take precedence over environment.
    
    Attributes:
        api_token: The Allure TestOps API token (always masked in logs).
        project_id: Optional default project ID for operations.
    """
    api_token: SecretStr
    project_id: Optional[int] = None
    
    @classmethod
    def from_environment(cls) -> "AuthContext":
        """Create context from environment variables.
        
        Environment Variables:
            ALLURE_API_TOKEN: Required API authentication token.
            ALLURE_PROJECT_ID: Optional default project ID.
        
        Raises:
            AuthenticationError: If ALLURE_API_TOKEN is not set.
        """
        token = os.environ.get("ALLURE_API_TOKEN")
        if not token:
            raise AuthenticationError(
                "No API token configured. "
                "Set ALLURE_API_TOKEN environment variable or provide api_token argument."
            )
        
        project_id_str = os.environ.get("ALLURE_PROJECT_ID")
        project_id = int(project_id_str) if project_id_str else None
        
        return cls(
            api_token=SecretStr(token),
            project_id=project_id,
        )
    
    def with_overrides(
        self,
        api_token: Optional[str] = None,
        project_id: Optional[int] = None,
    ) -> "AuthContext":
        """Create new context with runtime overrides.
        
        Returns a new AuthContext with specified values overridden.
        Original context is not modified (immutable pattern).
        
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
    api_token: Optional[str] = None,
    project_id: Optional[int] = None,
) -> AuthContext:
    """Get authentication context with optional runtime overrides.
    
    Resolution order:
    1. Runtime arguments (highest priority)
    2. Environment variables (fallback)
    
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
    # Start with environment-based context
    try:
        base_context = AuthContext.from_environment()
    except AuthenticationError:
        # If env not configured, we NEED runtime token
        if not api_token:
            raise AuthenticationError(
                "Authentication required. Either:\n"
                "1. Set ALLURE_API_TOKEN environment variable, or\n"
                "2. Provide api_token argument to this tool"
            )
        base_context = AuthContext(api_token=SecretStr(api_token))
    
    # Apply any runtime overrides
    if api_token or project_id is not None:
        return base_context.with_overrides(api_token=api_token, project_id=project_id)
    
    return base_context
```

### Tool Integration Pattern
- Tools are thin wrappers (no business logic, no try/except).
- Services accept AuthContext and pass it to the client.
- Use `get_auth_context` for runtime overrides.

All tools should follow this pattern:

```python
# src/tools/update_test_case.py (example)

@mcp.tool
async def create_test_case(
    project_id: int,
    name: str,
    description: str | None = None,
    # ... other params ...
    api_token: str | None = None,  # Runtime auth override
) -> str:
    """Create a new test case in Allure TestOps.
    
    Args:
        project_id: Target project ID. Overrides ALLURE_PROJECT_ID env var.
        name: Test case name.
        description: Optional description.
        api_token: Optional API token override. Uses ALLURE_API_TOKEN if not provided.
    
    Returns:
        Success message with created test case ID.
    """
    # Get context with potential runtime overrides
    auth_context = get_auth_context(
        api_token=api_token,
        project_id=project_id,  # Always use provided project_id
    )
    
    service = CaseService(auth_context)
    result = await service.create_test_case(...)
    return f"Created Test Case TC-{result.id}: {result.name}"
```

### Service Integration

```python
# src/services/case_service.py

class CaseService:
    """Service for test case operations."""
    
    def __init__(self, auth_context: AuthContext):
        """Initialize with authentication context.
        
        Args:
            auth_context: Authentication context for API calls.
        """
        self._auth = auth_context
        self._client = AllureClient(
            token=auth_context.api_token,
            project_id=auth_context.project_id,
        )
```

### Client Integration

```python
# src/client/client.py

class AllureClient:
    """Async client for Allure TestOps API."""
    
    def __init__(
        self,
        token: SecretStr,
        project_id: Optional[int] = None,
        base_url: Optional[str] = None,
    ):
        self._token = token
        self._project_id = project_id
        self._base_url = base_url or os.environ.get(
            "ALLURE_BASE_URL", 
            "https://allure.example.com"
        )
        self._http = httpx.AsyncClient(
            base_url=self._base_url,
            headers={"Authorization": f"Bearer {token.get_secret_value()}"},
        )
```

### Secure Logging

The logger must NEVER expose tokens:

```python
# src/utils/logger.py
import structlog

def mask_sensitive_data(_, __, event_dict):
    """Mask sensitive data in log events."""
    # SecretStr already masks itself, but double-check
    if "api_token" in event_dict:
        event_dict["api_token"] = "***MASKED***"
    if "token" in event_dict:
        event_dict["token"] = "***MASKED***"
    return event_dict

logger = structlog.wrap_logger(
    structlog.get_logger(),
    processors=[mask_sensitive_data, ...],
)
```

### Error Messages

```python
# Good: No token in error
"Authentication failed. The provided API token is invalid or expired."

# Bad: Token exposed
"Authentication failed for token abc123..."  # NEVER DO THIS
```

### Project Structure Notes

Files modified:
- `src/utils/auth.py` - AuthContext and get_auth_context
- All tool files - Add api_token parameter
- All service files - Accept AuthContext in constructor
- `src/client/client.py` - Accept token in constructor

### Testing Strategy

```python
# tests/unit/test_auth.py

class TestGetAuthContext:
    def test_runtime_token_overrides_env(self, monkeypatch):
        """Runtime token takes precedence over environment."""
        monkeypatch.setenv("ALLURE_API_TOKEN", "env-token")
        
        ctx = get_auth_context(api_token="runtime-token")
        
        assert ctx.api_token.get_secret_value() == "runtime-token"
    
    def test_env_fallback_when_no_runtime(self, monkeypatch):
        """Falls back to environment when no runtime provided."""
        monkeypatch.setenv("ALLURE_API_TOKEN", "env-token")
        
        ctx = get_auth_context()
        
        assert ctx.api_token.get_secret_value() == "env-token"
    
    def test_raises_when_no_auth_available(self, monkeypatch):
        """Raises clear error when no auth configured."""
        monkeypatch.delenv("ALLURE_API_TOKEN", raising=False)
        
        with pytest.raises(AuthenticationError) as exc:
            get_auth_context()
        
        assert "ALLURE_API_TOKEN" in str(exc.value)
        assert "api_token argument" in str(exc.value)
    
    def test_stateless_behavior(self, monkeypatch):
        """Context overrides don't persist between calls."""
        monkeypatch.setenv("ALLURE_API_TOKEN", "env-token")
        
        # First call with override
        ctx1 = get_auth_context(api_token="override")
        
        # Second call without override
        ctx2 = get_auth_context()
        
        assert ctx1.api_token.get_secret_value() == "override"
        assert ctx2.api_token.get_secret_value() == "env-token"
    
    def test_token_masked_in_repr(self):
        """Token is masked when context is logged/printed."""
        ctx = AuthContext(api_token=SecretStr("secret123"))
        
        repr_str = repr(ctx)
        str_str = str(ctx)
        
        assert "secret123" not in repr_str
        assert "secret123" not in str_str
```

### Dependencies

- Foundational for all tools (cross-cutting concern)
- Requires Pydantic SecretStr from Story 1.1
- Used by all services

### References
- [Source: specs/project-planning-artifacts/epics.md#Story 3.4]
- [Source: specs/prd.md#NFR5 - API Token Masking]
- [Source: specs/prd.md#NFR11 - End-to-End Tests]
- [Source: specs/architecture.md#Authentication & Security]
- [Source: specs/project-context.md#Pydantic & Data - Secrets]
- [Source: specs/implementation-artifacts/1-6-comprehensive-end-to-end-tests.md#NFR11 Coverage]

## Dev Agent Record

### Agent Model Used
gpt-5.2-codex

### Completion Notes List
- Regenerated story to explicitly require NFR11/AC11 E2E coverage for runtime auth override.
- **Code Review (2026-01-23):** Addressed 9 findings from adversarial review (excluding H2 per user request):
  - H1: Updated File List with all 16 modified files
  - H3: Enhanced E2E tests with proper runtime override verification and improved naming
  - M1: Fixed E2E test exception type (AuthenticationError vs AllureAuthError)
  - M2: Removed redundant os.environ restoration
  - M3: Fixed get_auth_context to preserve project_id when creating from runtime-only values
  - M4: Added Raises sections to all tool docstrings
  - M5: Validated with mypy --strict (success)
  - L1: Improved E2E test naming for clarity
  - L2: Added integration test for log masking (AC#6)
  - All unit tests passing (9/9), all validations passing

### File List
- specs/implementation-artifacts/3-4-runtime-authentication-override.md
- src/utils/auth.py (NEW - AuthContext and get_auth_context)
- src/services/test_case_service.py (MODIFIED - accepts AuthContext)
- src/services/search_service.py (MODIFIED - accepts AuthContext)
- src/services/shared_step_service.py (MODIFIED - accepts AuthContext)
- src/services/attachment_service.py (MODIFIED - uses client with auth)
- src/client/client.py (MODIFIED - accepts SecretStr token)
- src/tools/create_test_case.py (MODIFIED - added api_token parameter)
- src/tools/update_test_case.py (MODIFIED - added api_token parameter)
- src/tools/delete_test_case.py (MODIFIED - added api_token parameter)
- src/tools/search.py (MODIFIED - added api_token parameter to all search tools)
- src/tools/shared_steps.py (MODIFIED - added api_token parameter to all shared step tools)
- src/tools/link_shared_step.py (MODIFIED - added api_token parameter)
- src/tools/unlink_shared_step.py (MODIFIED - added api_token parameter)
- tests/unit/test_auth.py (NEW - unit tests for AuthContext)
- tests/e2e/test_runtime_auth_override.py (NEW - E2E tests for runtime auth)
