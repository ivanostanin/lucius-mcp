# Story 3.4: Runtime Authentication Override

Status: ready-for-dev

## Story

As an AI Agent,
I want to override the default authentication context (API Token, Project ID) at runtime,
so that I can operate across different projects or with different credentials within a single session.

## Acceptance Criteria

1. **Given** a tool call that requires authentication, **when** I provide `api_token` and `project_id` arguments directly, **then** these arguments override any environment variables or default configurations.
2. The operation is executed successfully with the provided runtime context.
3. Runtime overrides do NOT persist between tool calls (stateless).
4. Environment variable defaults are still used when runtime arguments are not provided.
5. Clear error message when neither runtime nor environment authentication is available.
6. API tokens passed at runtime must be masked in all logs.

## Tasks / Subtasks

- [ ] **Task 1: Implement AuthContext Model** (AC: #1, #3, #4)
  - [ ] 1.1: Create `AuthContext` dataclass in `src/utils/auth.py`
  - [ ] 1.2: Add `api_token` (SecretStr) and `project_id` (Optional[int]) fields
  - [ ] 1.3: Implement `from_environment()` class method
  - [ ] 1.4: Implement `with_overrides()` method for runtime values

- [ ] **Task 2: Create get_auth_context Helper** (AC: #1, #4, #5)
  - [ ] 2.1: Implement `get_auth_context()` function
  - [ ] 2.2: Accept optional runtime overrides as parameters
  - [ ] 2.3: Fall back to environment variables for unspecified values
  - [ ] 2.4: Raise `AuthenticationError` if no token available

- [ ] **Task 3: Integrate with Services** (AC: #1, #2)
  - [ ] 3.1: Update `SearchService` to accept `AuthContext`
  - [ ] 3.2: Update `CaseService` to accept `AuthContext`
  - [ ] 3.3: Pass auth context to `AllureClient` on each request

- [ ] **Task 4: Update All Tools** (AC: #1)
  - [ ] 4.1: Add optional `api_token` parameter to all tools
  - [ ] 4.2: Add optional `project_id` parameter where applicable
  - [ ] 4.3: Document runtime override capability in docstrings

- [ ] **Task 5: Secure Logging** (AC: #6)
  - [ ] 5.1: Verify SecretStr masks token in __repr__ and __str__
  - [ ] 5.2: Ensure no token leakage in error messages
  - [ ] 5.3: Test log output for masked tokens

- [ ] **Task 6: Unit Tests** (AC: #1-6)
  - [ ] 6.1: Test runtime override takes precedence
  - [ ] 6.2: Test environment fallback works
  - [ ] 6.3: Test missing auth raises clear error
  - [ ] 6.4: Test stateless behavior (overrides don't persist)
  - [ ] 6.5: Test token masking in logs

## Dev Notes

### FR14 Coverage

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

All tools should follow this pattern:

```python
# src/tools/cases.py (example)

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
- [Source: specs/architecture.md#Authentication & Security]
- [Source: specs/project-context.md#Pydantic & Data - Secrets]
- [Source: specs/prd.md#NFR5 - API Token Masking]

## Dev Agent Record

### Agent Model Used

_To be filled by implementing agent_

### Completion Notes List

_To be filled during implementation_

### File List

_To be filled during implementation_
