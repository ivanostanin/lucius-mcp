
# Test Suite - Lucius MCP

This directory contains the automated test suite for the Lucius MCP Server.

## Structure

- **unit/**: Isolated tests for individual components (logger, error handler, main logic).
- **integration/**: Tests verifying interaction between components (FastMCP + Starlette).
- **support/**: Shared test infrastructure.
  - **fixtures/**: Pytest fixtures (logger capture, client, app refresh).
  - **factories/**: Data factories using Faker.

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

- `client`: Returns a `TestClient` initialized with a fresh FastMCP session for each test.
- `capture_structured_logs`: Captures and parses JSON logs in memory (avoids stderr conflicts).
- `faker`: Shared Faker instance for data generation.
- `mocker`: Provided by `pytest-mock` for object patching.

## Implementation Details

The `tests/conftest.py` includes a robust `app` fixture that recreates the `FastMCP` ASGI application for every test. This is required because `FastMCP`'s `StreamableHTTPSessionManager` is single-use by design, and standard `TestClient` usage would otherwise crash on subsequent tests.
