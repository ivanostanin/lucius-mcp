# Story 1.3: Comprehensive Test Case Creation Tool

Status: ready-for-dev

## Story

As an AI Agent,
I want to create a new Test Case with all available metadata (Name, Description, Precondition, Steps, Checks, Tags, Custom Fields, Attachments),
so that I can document complex test scenarios in a single operation.

## Acceptance Criteria

1. **Given** a valid Allure API Token and Project ID, **when** I call the `create_test_case` tool with comprehensive metadata (including Steps, Tags, and Custom Fields), **then** the tool validates the input against the full Pydantic schema.
2. It successfully creates the test case with all provided fields correctly mapped in Allure TestOps.
3. It handles attachments (Base64 or URL) according to the API spec.
4. It returns a clear success message with the new Test Case ID.

## Tasks / Subtasks

- [x] **Task 1: Implement TestCaseService** (AC: #1, #2)
  - [x] 1.1: Create `src/services/test_case_service.py` with `TestCaseService` class
  - [x] 1.2: Implement `async def create_test_case(self, project_id: int, data: TestCaseCreate) -> TestCase` method
  - [x] 1.3: Use `AllureClient` from `src/client/` for API communication
  - [x] 1.4: Validate all input data using Pydantic models before API call
  - [x] 1.5: Map all fields correctly: Name, Description, Precondition, Steps, Tags, Custom Fields
  - [x] 1.6: Handle nested Step objects (Action + Expected Result structure)

- [x] **Task 2: Implement Attachment Handling** (AC: #3)
  - [x] 2.1: Create `src/services/attachment_service.py` for attachment processing
  - [x] 2.2: Support Base64-encoded content for inline attachments
  - [x] 2.3: Support URL references for external attachments
  - [x] 2.4: Validate attachment MIME types and size limits per API spec
  - [x] 2.5: Integrate attachment upload into test case creation flow

- [x] **Task 3: Create MCP Tool Definition** (AC: #1, #4)
  - [x] 3.1: Create `src/tools/create_test_case.py` with FastMCP tool registration
  - [x] 3.2: Implement `@mcp.tool` decorated `create_test_case` function
  - [x] 3.3: Add comprehensive Google-style docstring (LLM-optimized)
  - [x] 3.4: Tool MUST be thin wrapper - delegate ALL logic to `TestCaseService`
  - [x] 3.5: Return human-readable success message: "Created Test Case [ID]: '[Name]' (Status: Draft)"

- [x] **Task 4: Implement Input Validation** (AC: #1)
  - [x] 4.1: Validate required field: `name` (non-empty string)
  - [x] 4.2: Validate optional fields match Pydantic model types
  - [x] 4.3: Validate Tag format (string array)
  - [x] 4.4: Validate Custom Field structure (key-value pairs)
  - [x] 4.5: Raise `AllureValidationError` with clear hints on invalid input

- [x] **Task 5: Quality Assurance** (AC: implicit)
  - [x] 5.1: Write unit tests in `tests/unit/test_test_case_service.py` with mocked API
  - [x] 5.2: Write integration test in `tests/integration/test_test_create_tool.py`
  - [x] 5.3: Run `ruff check src/services/test_case_service.py src/tools/create_test_case.py`
  - [x] 5.4: Run `mypy --strict` on new files
  - [x] 5.5: Verify test coverage > 85% for new code
  - [x] 5.6: Run tests with `--alluredir=allure-results` for allure-pytest reporting

- [x] **Task 6: E2E Tests** (AC: implicit, NFR11)
  - [x] 6.1: Create `tests/e2e/test_create_test_case.py`
  - [x] 6.2: Write E2E test creating test case in sandbox and verifying via API
  - [x] 6.3: Verify tool returns correct Agent Hint format
  - [x] 6.4: Add cleanup to remove created test cases after test

## Dev Notes

### Architecture Compliance (CRITICAL)

**"Thin Tool / Fat Service" Pattern - MANDATORY:**
```python
# src/tools/create_test_case.py - CORRECT (Thin)
@mcp.tool
async def create_test_case(
    project_id: int,
    name: str,
    description: str | None = None,
    # ... other args
) -> str:
    """Create a new test case in Allure TestOps.
    
    Args:
        project_id: The Allure project ID (found in URL after /project/)
        name: Test case name (required, max 255 chars)
        description: Optional description in markdown format
        ...
    
    Returns:
        Success message with the created test case ID
    """
    service = TestCaseService(get_client())
    result = await service.create_test_case(project_id, TestCaseCreate(...))
    return f"Created Test Case {result.id}: '{result.name}' (Status: {result.status})"
```

**❌ FORBIDDEN in Tools:**
- Business logic
- Direct API calls
- `try/except` blocks (let global handler catch)
- JSON dumps in return values

### Service Implementation Pattern

```python
# src/services/case_service.py
from src.client import AllureClient, TestCase, TestCaseCreate
from src.client.exceptions import AllureAPIError

class TestCaseService:
    """Service for Test Case business logic."""
    
    def __init__(self, client: AllureClient) -> None:
        self._client = client
    
    async def create_test_case(
        self,
        project_id: int,
        data: TestCaseCreate,
    ) -> TestCase:
        """Create a test case with full validation.
        
        Args:
            project_id: Target project ID
            data: Validated test case creation data
            
        Returns:
            Created TestCase object from API
            
        Raises:
            AllureValidationError: If data validation fails
            AllureAPIError: If API call fails
        """
        # Services do the work, Tools just call and format
        return await self._client.create_test_case(project_id, data)
```

### Tool Docstring Requirements (LLM-Optimized)

The docstring IS the prompt for the AI agent. Be exhaustive:

```python
@mcp.tool
async def create_test_case(
    project_id: int,
    name: str,
    description: str | None = None,
    precondition: str | None = None,
    steps: list[dict[str, str]] | None = None,
    tags: list[str] | None = None,
    custom_fields: dict[str, str] | None = None,
) -> str:
    """Create a new test case in Allure TestOps.
    
    Use this tool to document a new test scenario. The test case will be 
    created in Draft status and can be updated later.
    
    Args:
        project_id: The Allure project ID. Found in the URL: 
            https://allure.example.com/project/123 → project_id=123
        name: Test case name (required). Should be descriptive and unique 
            within the project. Max 255 characters.
            Example: "User can login with valid credentials"
        description: Optional description in markdown format. Use this for 
            background context, requirements links, or detailed explanations.
        precondition: Optional preconditions that must be met before test 
            execution. Example: "User account exists with email test@example.com"
        steps: List of test steps. Each step is a dict with:
            - "action": What to do (required)
            - "expected": Expected result (required)
            Example: [{"action": "Click Login", "expected": "Login form appears"}]
        tags: List of tag names to apply. Tags help with filtering and 
            organization. Example: ["smoke", "login", "priority:high"]
        custom_fields: Key-value pairs for custom fields defined in your 
            Allure project. Keys must match field names exactly.
            Example: {"Layer": "UI", "Component": "Authentication"}
    
    Returns:
        Success message with the created test case ID and name.
        Example: "Created Test Case 12345: 'User can login' (Status: Draft)"
    
    Raises:
        ValidationError: If required fields are missing or invalid
        AuthenticationError: If API token is invalid or expired
        NotFoundError: If project_id doesn't exist
    """
```

### Step Data Structure

```python
# Each step in the steps list should be:
{
    "action": "Click the Login button",      # What to do
    "expected": "Login form is displayed"    # Expected outcome
}

# Full example with multiple steps:
steps = [
    {"action": "Navigate to login page", "expected": "Login page loads"},
    {"action": "Enter username 'test@example.com'", "expected": "Username field populated"},
    {"action": "Enter password", "expected": "Password field shows masked characters"},
    {"action": "Click Login button", "expected": "User is redirected to dashboard"},
]
```

### Custom Fields Mapping

Custom fields in Allure TestOps are project-specific. Common patterns:
- `Layer`: "UI", "API", "Unit", "Integration"
- `Component`: Feature or module name
- `Priority`: "Critical", "High", "Medium", "Low"
- `Automation Status`: "Manual", "Automated", "Planned"

### Attachment Handling

**Base64 Inline:**
```python
{
    "name": "screenshot.png",
    "content": "iVBORw0KGgo...",  # Base64 encoded
    "content_type": "image/png"
}
```

**URL Reference:**
```python
{
    "name": "log_file.txt",
    "url": "https://storage.example.com/logs/test-123.txt",
    "content_type": "text/plain"
}
```

### Previous Story Dependencies

**From Story 1.1:**
- Global exception handler in `src/utils/error.py` - catches `AllureAPIError`
- Structured logger in `src/utils/logger.py` - use for service logging
- FastMCP mounted in `src/main.py` - register tools here

**From Story 1.2:**
- `AllureClient` in `src/client/client.py` - use for API calls
- Pydantic models in `src/client/models.py` - `TestCase`, `TestCaseCreate`, `TestStep`
- Exceptions in `src/client/exceptions.py` - `AllureValidationError`, etc.

### Project Structure After This Story

```
src/
├── tools/
│   ├── __init__.py
│   └── cases.py              # NEW - create_test_case tool
├── services/
│   ├── __init__.py
│   ├── case_service.py       # NEW - TestCaseService
│   └── attachment_service.py # NEW - AttachmentService
└── ...
tests/
├── unit/
│   └── test_case_service.py  # NEW
└── integration/
    └── test_create_tool.py   # NEW
```

### Error Response Examples

The global handler will convert exceptions to Agent Hints:

**Validation Error:**
```
❌ Error: Validation Failed

The 'name' field is required and cannot be empty.

Suggestions:
- Provide a descriptive name for the test case
- Example: "User can login with valid credentials"
```

**Not Found Error:**
```
❌ Error: Project Not Found

Project ID '99999' does not exist or you don't have access.

Suggestions:
- Verify the project ID from the Allure URL
- Check your API token has access to this project
- Use list_projects to see available projects
```

### References

- [Source: specs/architecture.md#Implementation Patterns]
- [Source: specs/architecture.md#Communication Patterns]
- [Source: specs/project-context.md#The "Thin Tool / Fat Service" Pattern]
- [Source: specs/prd.md#FR1, FR2, FR4, FR15, FR16]
- [Source: Story 1.1 - Error Handler Implementation]
- [Source: Story 1.2 - AllureClient and Models]

## Dev Agent Record

### Agent Model Used

_To be filled by implementing agent_

### Completion Notes List

- Implemented `TestCaseService` handling DTO mapping and attachment orchestration.
- Implemented `AttachmentService` for uploading base64/files.
- Implemented MCP tool `create_test_case` in `src/tools/create_test_case.py` (renamed from `cases.py`).
- Added full support for creation with steps (BodyStep/ExpectedBodyStep) and attachments.
- Verified with Unit, Integration, and E2E tests using `respx` mock.
- Deferred Runtime Auth verification to Story 3.4 as it was not part of core requirements.

### File List

- src/services/test_case_service.py
- src/services/attachment_service.py
- src/tools/create_test_case.py
- tests/unit/test_test_case_service.py
- tests/unit/test_attachment_service.py
- tests/integration/test_test_create_tool.py
- tests/e2e/test_create_test_case.py
- src/client/client.py (Updated with `create_test_case` and `upload_attachment`)
- src/main.py (Updated to register tool)
- src/client/models/attachments.py
- src/client/models/common.py
- src/client/models/test_cases.py
