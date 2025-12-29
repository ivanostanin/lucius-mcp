# Story 1.1: Project Initialization & Core Architecture

Status: ready-for-dev

## Story

As a Developer,
I want to initialize the lucius-mcp repository with uv, fastmcp, and starlette,
so that I have a production-ready, structured foundation for the MCP server.

## Acceptance Criteria

1. **Given** a new repository, **when** I run the initialization scripts, **then** the project structure is created including `src/main.py`, `src/services/`, and `src/utils/`.
2. `uv` dependency management is configured with Python 3.14.
3. FastMCP is mounted on a Starlette application.
4. Structured JSON logging and the global exception handler for "Agent Hints" are implemented.

## Tasks / Subtasks

- [ ] **Task 1: Initialize Project with uv** (AC: #1, #2)
  - [ ] 1.1: Run `uv init . --app --python 3.14` in the project root
  - [ ] 1.2: Run `uv add "fastmcp<3" pydantic starlette uvicorn httpx`
  - [ ] 1.3: Run `uv add --dev pytest pytest-asyncio pytest-cov allure-pytest mypy ruff respx`
  - [ ] 1.4: Verify `pyproject.toml` and `uv.lock` are created correctly
  - [ ] 1.5: Add `[tool.ruff]` and `[tool.mypy]` strict configurations to `pyproject.toml`

- [ ] **Task 2: Create Directory Structure** (AC: #1)
  - [ ] 2.1: Create `src/` directory with `__init__.py`
  - [ ] 2.2: Create `src/client/` with `__init__.py` (for future API client)
  - [ ] 2.3: Create `src/tools/` with `__init__.py` (for MCP tool definitions)
  - [ ] 2.4: Create `src/services/` with `__init__.py` (for business logic)
  - [ ] 2.5: Create `src/utils/` with `__init__.py` (for shared utilities)
  - [ ] 2.6: Create `tests/` directory structure (`unit/`, `integration/`, `conftest.py`)
  - [ ] 2.7: Create `deployment/` with `scripts/` and `charts/` subdirectories
  - [ ] 2.8: Create `.env.example` with placeholder for `ALLURE_API_TOKEN`

- [ ] **Task 3: Implement Structured Logger** (AC: #4)
  - [ ] 3.1: Create `src/utils/logger.py` with JSON structured logging
  - [ ] 3.2: Configure log format: `{timestamp, level, logger, message, context, request_id}`
  - [ ] 3.3: Implement `SecretStr` masking for sensitive values (API tokens)
  - [ ] 3.4: Add correlation ID (Request ID) support for all log entries

- [ ] **Task 4: Implement Global Exception Handler** (AC: #4)
  - [ ] 4.1: Create `src/utils/error.py` with `AllureAPIError` base exception
  - [ ] 4.2: Implement Starlette exception handler that converts exceptions to "Agent Hints"
  - [ ] 4.3: Ensure all errors return text-based, LLM-friendly messages (not JSON dumps)
  - [ ] 4.4: Implement specific error types: `ResourceNotFoundError`, `ValidationError`, `AuthenticationError`

- [ ] **Task 5: Create Main Application Entry Point** (AC: #3)
  - [ ] 5.1: Create `src/main.py` with FastMCP server initialization
  - [ ] 5.2: Mount FastMCP on Starlette application for HTTP transport
  - [ ] 5.3: Register the global exception handler middleware
  - [ ] 5.4: Add placeholder `@mcp.tool` decorator (no-op tool for testing)
  - [ ] 5.5: Configure uvicorn startup with proper host/port settings

- [ ] **Task 6: Quality Assurance Setup** (AC: implicit)
  - [ ] 6.1: Run `ruff check src/` and fix any linting issues
  - [ ] 6.2: Run `mypy --strict src/` and ensure zero type errors
  - [ ] 6.3: Write basic unit test for logger in `tests/unit/test_logger.py`
  - [ ] 6.4: Verify `uv run python src/main.py` starts the server successfully

## Dev Notes

### Architecture Compliance (CRITICAL)

**"Thin Tool / Fat Service" Pattern:**
- Tools in `src/tools/` MUST be thin wrappers - NO business logic!
- All logic goes in `src/services/`
- This story sets up the structure; actual tools come in later stories

**Error Handling Strategy:**
- **DO NOT** use `try/except` in tools
- Let exceptions bubble up to the global handler
- Global handler converts to "Agent Hints" (text, not JSON)

### Technical Requirements

**Python Version:** 3.14 (managed via `uv`, NOT pip/poetry)

**Required Dependencies:**
```
fastmcp<3          # Pin to avoid breaking changes when v3 releases
pydantic>=2.0      # Strict mode required
starlette          # Async web framework
uvicorn            # ASGI server
httpx              # Async HTTP client (for future API client)
```

**Dev Dependencies:**
```
pytest             # Testing framework
pytest-asyncio     # Async test support
pytest-cov         # Test coverage measurement
allure-pytest      # Allure test reporting
mypy               # Strict type checking
ruff               # Linting/formatting
respx              # httpx mocking
```

### Project Structure to Create

```
lucius-mcp/
├── pyproject.toml          # uv managed
├── uv.lock
├── .env.example
├── README.md
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── main.py             # FastMCP + Starlette entrypoint
│   ├── client/
│   │   └── __init__.py
│   ├── tools/
│   │   └── __init__.py
│   ├── services/
│   │   └── __init__.py
│   └── utils/
│       ├── __init__.py
│       ├── logger.py       # Structured JSON logging
│       └── error.py        # Global exception handler
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   └── __init__.py
│   └── integration/
│       └── __init__.py
└── deployment/
    ├── scripts/
    └── charts/
        └── lucius-mcp/
```

### Logger Implementation Notes

**Required Format (JSON):**
```json
{
  "timestamp": "2025-12-27T19:00:00.000Z",
  "level": "INFO",
  "logger": "lucius-mcp",
  "message": "Tool invoked",
  "request_id": "uuid-here",
  "context": {"tool": "create_test_case"}
}
```

**Secret Masking:**
- Use `pydantic.SecretStr` for API tokens
- Logger must mask any `SecretStr` values automatically

### Exception Handler Implementation Notes

**Agent Hint Format:**
```
❌ Error: Resource Not Found

The test case with ID '12345' was not found in project 'ABC'.

Suggestions:
- Verify the test case ID is correct
- Check if you have access to project 'ABC'
- Use list_test_cases to find available test cases
```

**NEVER return:**
- Raw JSON error responses
- Stack traces (except in debug mode)
- Technical jargon without explanation

### FastMCP + Starlette Integration

**Key Pattern:**
```python
from fastmcp import FastMCP
from starlette.applications import Starlette

mcp = FastMCP("lucius-mcp")

# Mount on Starlette for HTTP transport
app = Starlette()
app.mount("/mcp", mcp.get_asgi_app())
```

### References

- [Source: specs/architecture.md#Starter Template Evaluation]
- [Source: specs/architecture.md#Project Structure & Boundaries]
- [Source: specs/project-context.md#Technology Stack & Versions]
- [Source: specs/project-context.md#Critical Implementation Patterns]

## Dev Agent Record

### Agent Model Used

_To be filled by implementing agent_

### Completion Notes List

_To be filled during implementation_

### File List

_To be filled during implementation_
