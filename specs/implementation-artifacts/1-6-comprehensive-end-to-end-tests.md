# Story 1.6: Comprehensive End-to-End Tests

Status: ready-for-dev

## Story

As a Developer,
I want comprehensive end-to-end tests that verify tool execution results against a sandbox TestOps instance,
so that I can ensure the MCP server correctly integrates with Allure TestOps in real-world scenarios.

## Acceptance Criteria

1. **Given** a sandbox Allure TestOps instance, **when** I run the E2E test suite, **then** all Test Case CRUD operations are verified against actual API responses.
2. End-to-end tests cover create, read, update, and delete operations for Test Cases.
3. Tests validate that tool outputs match expected formats (Agent Hint messages).
4. Tests run in CI/CD pipeline with configurable sandbox credentials.
5. Test execution is isolated (cleanup after each test run).

## Tasks / Subtasks

- [ ] **Task 1: Configure E2E Test Infrastructure** (AC: #4)
  - [ ] 1.1: Create `tests/e2e/` directory structure
  - [ ] 1.2: Create `tests/e2e/conftest.py` with sandbox connection fixtures
  - [ ] 1.3: Add environment variable configuration for `ALLURE_SANDBOX_URL` and `ALLURE_SANDBOX_TOKEN`
  - [ ] 1.4: Create `.env.test.example` with placeholder values
  - [ ] 1.5: Add `pytest-asyncio` configuration for async E2E tests

- [ ] **Task 2: Implement Test Data Management** (AC: #5)
  - [ ] 2.1: Create `tests/e2e/helpers/cleanup.py` for test isolation
  - [ ] 2.2: Implement automatic cleanup of created test cases after each test
  - [ ] 2.3: Add unique test run ID prefix to all created entities
  - [ ] 2.4: Implement retry logic for flaky sandbox connections

- [ ] **Task 3: Create Test Case CRUD E2E Tests** (AC: #1, #2)
  - [ ] 3.1: Create `tests/e2e/test_case_crud.py`
  - [ ] 3.2: Test `create_test_case` tool with full metadata
  - [ ] 3.3: Test `get_test_case` retrieves correct data
  - [ ] 3.4: Test `update_test_case` modifies fields correctly
  - [ ] 3.5: Test `delete_test_case` archives the test case
  - [ ] 3.6: Test idempotency of update operations

- [ ] **Task 4: Validate Tool Output Formats** (AC: #3)
  - [ ] 4.1: Verify success messages match Agent Hint format
  - [ ] 4.2: Verify error messages are LLM-friendly (not raw JSON)
  - [ ] 4.3: Test validation error responses
  - [ ] 4.4: Test not-found error responses

- [ ] **Task 5: CI/CD Integration** (AC: #4)
  - [ ] 5.1: Add E2E test job to GitHub Actions workflow
  - [ ] 5.2: Configure secrets for sandbox credentials
  - [ ] 5.3: Add conditional E2E execution (skip if no sandbox configured)
  - [ ] 5.4: Generate Allure report artifacts and upload to GitHub Actions

- [ ] **Task 6: Documentation** (AC: implicit)
  - [ ] 6.1: Document E2E test setup in README
  - [ ] 6.2: Document sandbox requirements
  - [ ] 6.3: Add troubleshooting guide for common E2E failures

## Dev Notes

### NFR11 Coverage

This story directly addresses **NFR11**:
> End-to-End Tests: Implemented involving verification of tool execution results in sandbox TestOps instance or project.

### Sandbox Configuration

**Required Environment Variables:**
```bash
# .env.test
ALLURE_SANDBOX_URL=https://sandbox.allure.example.com
ALLURE_SANDBOX_TOKEN=your-sandbox-api-token
ALLURE_SANDBOX_PROJECT_ID=123
```

**Fixture Pattern:**
```python
# tests/e2e/conftest.py
import os
import pytest
from src.client import AllureClient
from pydantic import SecretStr

@pytest.fixture
async def sandbox_client():
    """Configured client for sandbox TestOps instance."""
    url = os.environ.get("ALLURE_SANDBOX_URL")
    token = os.environ.get("ALLURE_SANDBOX_TOKEN")
    
    if not url or not token:
        pytest.skip("Sandbox credentials not configured")
    
    async with AllureClient(
        base_url=url,
        token=SecretStr(token),
    ) as client:
        yield client

@pytest.fixture
def test_run_id():
    """Unique ID for test isolation."""
    import uuid
    return f"e2e-{uuid.uuid4().hex[:8]}"
```

### Test Isolation Pattern

Each test creates entities with unique prefixes and cleans up after:

```python
# tests/e2e/test_case_crud.py
import pytest
from tests.e2e.helpers.cleanup import CleanupTracker

@pytest.fixture
async def cleanup_tracker(sandbox_client):
    """Track created entities for cleanup."""
    tracker = CleanupTracker(sandbox_client)
    yield tracker
    await tracker.cleanup_all()

async def test_create_test_case(sandbox_client, cleanup_tracker, test_run_id):
    """E2E: Create test case in sandbox."""
    # Create with unique name
    name = f"[{test_run_id}] Login Test"
    
    result = await sandbox_client.create_test_case(
        project_id=int(os.environ["ALLURE_SANDBOX_PROJECT_ID"]),
        data=TestCaseCreate(name=name, description="E2E test case"),
    )
    
    # Track for cleanup
    cleanup_tracker.track_test_case(result.id)
    
    # Verify
    assert result.id is not None
    assert result.name == name
```

### CleanupTracker Implementation

```python
# tests/e2e/helpers/cleanup.py
class CleanupTracker:
    """Tracks created entities for cleanup after tests."""
    
    def __init__(self, client: AllureClient):
        self._client = client
        self._test_cases: list[int] = []
        self._shared_steps: list[int] = []
    
    def track_test_case(self, test_case_id: int) -> None:
        self._test_cases.append(test_case_id)
    
    def track_shared_step(self, step_id: int) -> None:
        self._shared_steps.append(step_id)
    
    async def cleanup_all(self) -> None:
        """Delete all tracked entities."""
        for tc_id in self._test_cases:
            try:
                await self._client.delete_test_case(tc_id)
            except Exception:
                pass  # Best effort cleanup
        
        for ss_id in self._shared_steps:
            try:
                await self._client.delete_shared_step(ss_id)
            except Exception:
                pass
```

### E2E Test Examples

**Full CRUD Flow:**
```python
async def test_full_test_case_lifecycle(sandbox_client, cleanup_tracker, test_run_id):
    """E2E: Complete create-read-update-delete cycle."""
    project_id = int(os.environ["ALLURE_SANDBOX_PROJECT_ID"])
    
    # CREATE
    created = await sandbox_client.create_test_case(
        project_id=project_id,
        data=TestCaseCreate(
            name=f"[{test_run_id}] Lifecycle Test",
            description="Testing full CRUD",
            steps=[
                StepCreate(action="Step 1", expected="Result 1"),
            ],
        ),
    )
    cleanup_tracker.track_test_case(created.id)
    assert created.id is not None
    
    # READ
    fetched = await sandbox_client.get_test_case(created.id)
    assert fetched.name == created.name
    assert len(fetched.steps) == 1
    
    # UPDATE
    updated = await sandbox_client.update_test_case(
        created.id,
        TestCaseUpdate(description="Updated description"),
    )
    assert updated.description == "Updated description"
    
    # DELETE
    await sandbox_client.delete_test_case(created.id)
    
    # VERIFY DELETED
    with pytest.raises(AllureNotFoundError):
        await sandbox_client.get_test_case(created.id)
```

**Tool Output Format Validation:**
```python
async def test_tool_returns_agent_hint_format(mcp_server, sandbox_client):
    """E2E: Verify tool outputs are LLM-friendly."""
    # Call tool through MCP interface
    result = await mcp_server.call_tool(
        "create_test_case",
        {
            "project_id": 123,
            "name": "Test Case",
        }
    )
    
    # Verify output format
    assert "Created Test Case" in result.content
    assert "ID:" in result.content or result.content.isdigit() == False  # Not raw JSON
    assert "{" not in result.content  # No JSON dumps
```

### CI/CD Configuration

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on:
  push:
    branches: [main]
  pull_request:

jobs:
  e2e:
    runs-on: ubuntu-latest
    if: ${{ secrets.ALLURE_SANDBOX_URL != '' }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.14'
      
      - name: Install uv
        run: pip install uv
      
      - name: Install dependencies
        run: uv sync
      
      - name: Run E2E tests
        env:
          ALLURE_SANDBOX_URL: ${{ secrets.ALLURE_SANDBOX_URL }}
          ALLURE_SANDBOX_TOKEN: ${{ secrets.ALLURE_SANDBOX_TOKEN }}
          ALLURE_SANDBOX_PROJECT_ID: ${{ secrets.ALLURE_SANDBOX_PROJECT_ID }}
        run: uv run pytest tests/e2e/ -v --tb=short --alluredir=allure-results
      
      - name: Generate Allure Report
        if: always()
        run: |
          uv run allure generate allure-results -o reports/allure-report --clean
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: e2e-test-results
          path: reports/allure-report/
```

### Project Structure After This Story

```
tests/
├── unit/                        # Existing unit tests
├── integration/                 # Existing integration tests
└── e2e/                         # NEW - End-to-end tests
    ├── __init__.py
    ├── conftest.py              # Sandbox fixtures
    ├── helpers/
    │   ├── __init__.py
    │   └── cleanup.py           # Test isolation helpers
    ├── test_case_crud.py        # Test Case E2E tests
    └── test_tool_outputs.py     # Tool format validation
```

### Previous Story Dependencies

**From Story 1.1-1.5:**
- All Test Case CRUD operations implemented
- `AllureClient` with all methods
- Tool definitions in `src/tools/cases.py`
- Exception handling and Agent Hints

### References

- [Source: specs/prd.md#NFR11 - End-to-End Tests]
- [Source: specs/prd.md#Technical Success - Testability]
- [Source: specs/architecture.md#Quality Requirements]

## Dev Agent Record

### Agent Model Used

_To be filled by implementing agent_

### Completion Notes List

_To be filled during implementation_

### File List

_To be filled during implementation_
