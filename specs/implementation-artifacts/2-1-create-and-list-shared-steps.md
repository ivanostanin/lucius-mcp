# Story 2.1: Create & List Shared Steps

Status: ready-for-dev

## Story

As an AI Agent,
I want to create reusable Shared Steps and list them,
so that I can build a library of common test logic for discovery and reuse.

## Acceptance Criteria

1. **Given** a Project ID, **when** I call `create_shared_step` with a name and a list of steps, **then** the shared step is created in the Allure library.
2. **When** I call `list_shared_steps`, it returns the new step among others.
3. The tools provide LLM-optimized descriptions for discovery.

## Tasks / Subtasks

- [ ] **Task 1: Create SharedStepService** (AC: #1, #2)
  - [ ] 1.1: Create `src/services/shared_step_service.py` with `SharedStepService` class
  - [ ] 1.2: Implement `async def create_shared_step(self, project_id: int, data: SharedStepCreate) -> SharedStep`
  - [ ] 1.3: Implement `async def list_shared_steps(self, project_id: int) -> list[SharedStep]`
  - [ ] 1.4: Use `AllureClient` for API communication
  - [ ] 1.5: Handle pagination for list operations (if needed by API)

- [ ] **Task 2: Extend AllureClient with Shared Step Methods** (AC: #1, #2)
  - [ ] 2.1: Add `create_shared_step` method to `AllureClient`
  - [ ] 2.2: Add `list_shared_steps` method to `AllureClient`
  - [ ] 2.3: Verify correct API endpoints from OpenAPI spec
  - [ ] 2.4: Add proper error handling for API responses

- [ ] **Task 3: Create MCP Tool Definitions** (AC: #1, #2, #3)
  - [ ] 3.1: Create `src/tools/shared_steps.py` with FastMCP tools
  - [ ] 3.2: Implement `@mcp.tool` decorated `create_shared_step` function
  - [ ] 3.3: Implement `@mcp.tool` decorated `list_shared_steps` function
  - [ ] 3.4: Add comprehensive LLM-optimized docstrings
  - [ ] 3.5: Tools MUST be thin wrappers - delegate to `SharedStepService`

- [ ] **Task 4: Validate Pydantic Models** (AC: #1)
  - [ ] 4.1: Verify `SharedStep` model exists in generated models
  - [ ] 4.2: Verify `SharedStepCreate` model exists or create manually
  - [ ] 4.3: Ensure models include: name, steps (list of actions/expectations)
  - [ ] 4.4: Add model overrides if generated models are insufficient

- [ ] **Task 5: Quality Assurance** (AC: implicit)
  - [ ] 5.1: Write unit tests in `tests/unit/test_shared_step_service.py`
  - [ ] 5.2: Run `mypy --strict` and `ruff check`
  - [ ] 5.3: Verify test coverage > 85%
  - [ ] 5.4: Run tests with `--alluredir=allure-results` for allure-pytest reporting
  - [ ] 5.5: Verify error hints for invalid inputs (Actionable Error Handling)

- [ ] **Task 6: E2E Tests** (AC: implicit, NFR11)
  - [ ] 6.1: Create `tests/e2e/test_shared_steps.py`
  - [ ] 6.2: Write E2E test creating shared step in sandbox
  - [ ] 6.3: Write E2E test listing shared steps and verifying created step appears
  - [ ] 6.4: Add cleanup to remove created shared steps after test

## Dev Notes

### What Are Shared Steps?

Shared Steps are reusable test step sequences that can be referenced by multiple Test Cases. They:
- Reduce duplication across test cases
- Allow centralized updates (change once, affect all)
- Provide a library of common test logic

**Example Use Case:**
- "Login as Admin" shared step containing:
  1. Navigate to login page
  2. Enter admin credentials
  3. Click login
  4. Verify admin dashboard loads

This can be reused in 50+ test cases instead of duplicating the steps.

### SharedStep Data Structure

```python
# Created shared step
SharedStep(
    id=789,
    name="Login as Admin",
    steps=[
        StepItem(action="Navigate to /login", expected="Login page loads"),
        StepItem(action="Enter admin@example.com", expected="Email field populated"),
        StepItem(action="Enter password", expected="Password masked"),
        StepItem(action="Click Login", expected="Redirected to /admin/dashboard"),
    ]
)
```

### Service Implementation Pattern

```python
# src/services/shared_step_service.py
from src.client import AllureClient, SharedStep, SharedStepCreate

class SharedStepService:
    """Service for Shared Step business logic."""
    
    def __init__(self, client: AllureClient) -> None:
        self._client = client
    
    async def create_shared_step(
        self,
        project_id: int,
        data: SharedStepCreate,
    ) -> SharedStep:
        """Create a reusable shared step.
        
        Args:
            project_id: Target project ID
            data: Shared step creation data
            
        Returns:
            Created SharedStep object
        """
        return await self._client.create_shared_step(project_id, data)
    
    async def list_shared_steps(
        self,
        project_id: int,
        page: int = 0,
        size: int = 100,
    ) -> list[SharedStep]:
        """List all shared steps in a project.
        
        Args:
            project_id: Target project ID
            page: Pagination page (0-indexed)
            size: Items per page
            
        Returns:
            List of SharedStep objects
        """
        return await self._client.list_shared_steps(project_id, page=page, size=size)
```

### Tool Definition - create_shared_step

```python
@mcp.tool
async def create_shared_step(
    project_id: int,
    name: str,
    steps: list[dict[str, str]],
    description: str | None = None,
) -> str:
    """Create a reusable shared step for the test library.
    
    Shared steps are reusable test sequences that can be linked to multiple
    test cases. Use them for common flows like login, setup, or teardown.
    
    Args:
        project_id: The Allure project ID. Found in URL: /project/123
        name: Descriptive name for the shared step. Should clearly describe
            what the step sequence does.
            Examples: "Login as Admin", "Setup Test Data", "Verify Navigation"
        steps: List of step objects. Each step has:
            - "action": What to do (required)
            - "expected": Expected result (required)
            Example: [
                {"action": "Navigate to login", "expected": "Login page loads"},
                {"action": "Enter credentials", "expected": "Fields populated"},
            ]
        description: Optional description explaining when/why to use this
            shared step. Helpful for discovery.
    
    Returns:
        Success message with the created shared step ID.
        Example: "Created Shared Step 789: 'Login as Admin' (4 steps)"
    
    Example usage:
        create_shared_step(
            project_id=123,
            name="Login as Standard User",
            steps=[
                {"action": "Go to /login", "expected": "Login page displayed"},
                {"action": "Enter user@test.com", "expected": "Email entered"},
                {"action": "Enter password", "expected": "Password masked"},
                {"action": "Click Login", "expected": "Dashboard shown"},
            ],
            description="Standard user login flow for functional tests"
        )
    """
```

### Tool Definition - list_shared_steps

```python
@mcp.tool
async def list_shared_steps(
    project_id: int,
    search: str | None = None,
) -> str:
    """List available shared steps in the project's test library.
    
    Use this to discover existing reusable steps before creating new ones.
    This helps avoid duplication and promotes reuse.
    
    Args:
        project_id: The Allure project ID. Found in URL: /project/123
        search: Optional search term to filter by name. Case-insensitive.
    
    Returns:
        Formatted list of shared steps with IDs and step counts.
        Example:
            "Found 3 shared steps:
            - [ID: 789] Login as Admin (4 steps)
            - [ID: 790] Setup Test Database (2 steps)
            - [ID: 791] Verify Footer Links (5 steps)"
    
    Tip: Use this before creating a new shared step to check if a similar
    one already exists. You can then use or extend the existing step.
    """
```

### Response Formatting

**Create Response:**
```
✅ Created Shared Step 789: 'Login as Admin'

Contains 4 steps:
1. Navigate to login → Login page loads
2. Enter credentials → Fields populated
3. Click Login → Authentication succeeds
4. Verify dashboard → Admin dashboard displayed

Use this ID (789) when linking to test cases.
```

**List Response:**
```
📚 Found 3 shared steps in project 123:

1. [ID: 789] Login as Admin (4 steps)
   Used in: 15 test cases

2. [ID: 790] Setup Test Database (2 steps)
   Used in: 8 test cases

3. [ID: 791] Verify Footer Links (5 steps)
   Used in: 3 test cases

💡 Tip: Use list_test_cases with shared_step_id filter to see linked cases.
```

### Previous Story Dependencies

**From Epic 1:**
- `AllureClient` in `src/client/client.py` (Story 1.2)
- Pydantic models in `src/client/models.py` (Story 1.2)
- Tool pattern established in `src/tools/cases.py` (Story 1.3)
- Service pattern established in `src/services/case_service.py` (Story 1.3)

**Coordination with Story 2.3:**
- This story creates the shared steps
- Story 2.3 links them to test cases

### Project Structure After This Story

```
src/
├── tools/
│   ├── cases.py               # Test case tools (Epic 1)
│   └── shared_steps.py        # NEW - create/list shared steps
├── services/
│   ├── case_service.py        # TestCaseService (Epic 1)
│   └── shared_step_service.py # NEW - SharedStepService
└── client/
    └── client.py              # Add shared step methods
```

### References

- [Source: specs/prd.md#FR7, FR9 - Shared Steps]
- [Source: specs/epics.md#Epic 2]
- [Source: specs/architecture.md#Implementation Patterns]

## Dev Agent Record

### Agent Model Used

_To be filled by implementing agent_

### Completion Notes List

_To be filled during implementation_

### File List

_To be filled during implementation_
