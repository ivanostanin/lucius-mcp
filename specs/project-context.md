---
project_name: 'lucius-mcp'
user_name: 'Ivan Ostanin'
date: '2025-12-26'
sections_completed: ['technology_stack_discovery', 'context_generation', 'pattern_definition']
existing_patterns_found: 4
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

## 1. Technology Stack & Versions

*   **Language:** Python 3.14 (Managed by `uv`). **Do not use pip/poetry.**
*   **Web Framework:** Starlette (Asynchronous).
*   **MCP Framework:** FastMCP (v2.0+) mounted on Starlette.
*   **Validation:** Pydantic v2 (Strict Mode). Use `model_validate` and `Field`.
*   **HTTP Client:** `httpx` (Async only).
*   **Linting/Formatting:** `ruff` (Strict compliance).
*   **Type Checking:** `mypy` (Strict mode).

## 2. Critical Implementation Patterns

### The "Thin Tool / Fat Service" Pattern (STRICT)
*   **Tools (`src/tools/`)**: MUST be thin wrappers.
    *   **Permitted:** Argument validation, calling a service, formatting the service response into a human-readable string.
    *   **FORBIDDEN:** Business logic, direct API calls, complex data transformation.
*   **Services (`src/services/`)**: Contain ALL business logic.
    *   **Permitted:** `httpx` logic, data processing, returning Pydantic models.
    *   **Response:** Services return structured data (Models/Tuples), NEVER specific MCP formatted text.

### Error Handling Strategy
*   **Global Handling:** The app uses a global exception handler (in `src/utils/error_handler.py`).
*   **In Services:** Raise specific, typed exceptions (e.g., `ResourceNotFoundError`, `AllureAPIError`).
*   **In Tools:** **DO NOT use `try/except` blocks.** Let exceptions bubble up. The global handler will convert them into "Agent Hints" (informative text messages explaining why the action failed).

### Pydantic & Data
*   **Schema First:** Use `datamodel-code-generator` to create models from OpenAPI specs.
*   **Strict Mode:** All models must use `ConfigDict(strict=True)`.
*   **Secrets:** Use `SecretStr` for API keys in configuration.

## 3. Communication Rules (Agent-to-Agent)

### Tool Outputs
*   **Text over JSON:** Tools are for Agents, not APIs. Return clear, concise markdown text.
    *   *Bad:* Returns raw JSON dump of a test case.
    *   *Good:* "Created Test Case 123: 'Login Flow' (Status: Draft)."
*   **Verbosity:** Be terse. Agents have limited context windows.

### Tool Names & Args
*   **Naming:** `snake_case` (e.g., `create_test_case`, not `CreateTestCase`).
*   **Descriptions:** Detailed Google-style docstrings are MANDATORY. The "Args" section defines the prompt engineering for the tool user.

## 4. File Structure Boundaries
*   `src/tools/`: **Only** FastMCP tool definitions.
*   `src/services/`: Business logic and API interactions.
*   `src/client/`: Generated API clients (do not modify manually).
*   `deployment/`: K8s charts and Dockerfiles.
*   `deployment/scripts/`: Shell scripts for build, run, and push operations.
*   `tests/`: `pytest` suites.


## 5. Development Workflow (AI Agent Instructions)
1.  **Dependency Management:** Always use `uv add` / `uv run`.
2.  **Async/Await:** EVERYTHING is `async`. Do not write synchronous I/O.
3.  **Pathing:** Use `pathlib.Path` objects, never string path manipulation.
4.  **Testing:** Write `pytest` tests for every service method. Mock external API calls using `respx`.

## 6. Forbidden Practices 🛑
*   **No Synchronous HTTP:** Use `httpx`, never `requests`.
*   **No Global State:** Do not store user state in module-level variables.
*   **No Wildcard Imports:** `from module import *` is banned.
*   **No `print()`:** Use the configured logger.
