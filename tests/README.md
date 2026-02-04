
# Test Suite - Lucius MCP

This directory contains the automated test suite for the Lucius MCP Server.

## Manual MCP tool-call validation
See `agentic-tool-calls-tests.md` for the manual MCP tool-call checklist. It requires you to set up the MCP connection to your agent manually before running those steps.
This scenario can be used to perform end-to-end testing of the MCP server using your favorite agent.

## Structure

- **agentic/**: Manual/agent-driven validation assets.
- **e2e/**: End-to-end tests.
- **unit/**: Isolated tests for individual components (logger, error handler, main logic).
- **integration/**: Tests verifying interaction between components (FastMCP + Starlette).
- **packaging/**: Packaging and distribution tests.
- **support/**: Shared test infrastructure.
  - **fixtures/**: Pytest fixtures (logger capture, client, app refresh).
  - **factories/**: Data factories using Faker.
- **conftest.py**: Global pytest fixtures.
- **__init__.py**: Test package marker.

## Running Tests

Execute all tests:
```bash
uv add --dev pytest-mock  # Ensure this is installed
uv run pytest tests/
```

Run specific test file:
```bash
uv run pytest tests/unit/test_main.py
```

## Key Fixtures

- `client`: Returns a `Starlette TestClient` initialized with a fresh FastMCP session for each test.
- `allure_client`: Provides an initialized `AllureClient` with mocked OAuth session and `respx` network mocking.
- `capture_structured_logs`: Captures and parses JSON logs in memory (avoids stderr conflicts).
- `faker`: Shared Faker instance for data generation.
- `mocker`: Provided by `pytest-mock` for object patching.

## Data Factories

Standardized factories for Allure DTOs are located in `tests/support/factories/model_factories.py`. Use them to generate valid test data with easy overrides:

```python
from tests.support.factories.model_factories import create_test_case_create_v2_dto

dto = create_test_case_create_v2_dto(name="Custom Name")
```

## Implementation Details

The `tests/conftest.py` includes a robust `app` fixture that recreates the `FastMCP` ASGI application for every test. This is required because `FastMCP`'s `StreamableHTTPSessionManager` is single-use by design, and standard `TestClient` usage would otherwise crash on subsequent tests.
