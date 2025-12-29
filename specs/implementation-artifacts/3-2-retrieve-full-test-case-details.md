# Story 3.2: Retrieve Full Test Case Details

Status: ready-for-dev

## Story

As an AI Agent,
I want to retrieve the complete details of a specific Test Case,
so that I can understand its full context, steps, and metadata.

## Acceptance Criteria

1. **Given** a valid Test Case ID, **when** I call `get_test_case_details`, **then** the tool returns the full Test Case object including all steps, tags, and custom fields.
2. Returns all metadata: name, description, preconditions, steps, tags, custom fields, attachments.
3. Handles cases where the Test Case ID is not found with a clear error.
4. Tool returns LLM-friendly formatted output, not raw JSON.
5. Supports runtime authentication override via optional `api_token` argument.

## Tasks / Subtasks

- [ ] **Task 1: Define Get Test Case Details Tool** (AC: #1, #4, #5)
  - [ ] 1.1: Create `get_test_case_details` tool in `src/tools/search.py`
  - [ ] 1.2: Define input parameters (`test_case_id`, optional `api_token`)
  - [ ] 1.3: Add comprehensive Google-style docstring
  - [ ] 1.4: Format response as readable markdown-style text

- [ ] **Task 2: Extend Search Service** (AC: #1, #2)
  - [ ] 2.1: Add `get_test_case_details()` method to `SearchService`
  - [ ] 2.2: Return full `TestCase` Pydantic model with all fields populated
  - [ ] 2.3: Include steps, tags, custom fields, and attachments

- [ ] **Task 3: Extend AllureClient** (AC: #1, #2)
  - [ ] 3.1: Add `get_test_case()` method if not already implemented
  - [ ] 3.2: Ensure full response deserialization (steps, tags, custom fields)
  - [ ] 3.3: Handle attachment metadata retrieval

- [ ] **Task 4: Error Handling** (AC: #3)
  - [ ] 4.1: Add `TestCaseNotFoundError` exception if not exists
  - [ ] 4.2: Ensure global handler returns "Test Case ID X not found" Agent Hint
  - [ ] 4.3: Validate test_case_id is positive integer

- [ ] **Task 5: Unit Tests** (AC: #1, #2, #3)
  - [ ] 5.1: Test successful retrieval with full metadata
  - [ ] 5.2: Test not-found error handling
  - [ ] 5.3: Test output formatting
  - [ ] 5.4: Mock API responses

## Dev Notes

### FR11 Coverage

This story directly addresses **FR11**:
> Agents can retrieve the full details of a specific Test Case by its Allure ID.

### API Endpoint Reference

**Allure TestOps API:**
```
GET /api/rs/testcase/{id}
Path Parameters:
  - id: integer (REQUIRED) - The test case ID

Response includes:
  - id, name, description, preconditions
  - steps: list of Step objects (action, expected, attachments)
  - tags: list of tag strings
  - customFields: key-value pairs
  - automationStatus, status
  - attachments: list of attachment metadata
```

### Tool Implementation

```python
# src/tools/search.py

@mcp.tool
async def get_test_case_details(
    test_case_id: int,
    api_token: str | None = None,
) -> str:
    """Get complete details of a specific test case.
    
    Retrieves all information about a test case including its steps,
    tags, custom fields, and attachments. Use this before updating
    a test case to understand its current state.
    
    Args:
        test_case_id: The unique ID of the test case to retrieve.
        api_token: Optional override for the default API token.
    
    Returns:
        Formatted test case details including all metadata.
    
    Example:
        "Test Case TC-123: Login Flow
        Status: Draft | Automation: Manual
        
        Description:
        Verifies user can log in with valid credentials.
        
        Steps:
        1. Navigate to login page → Login form displayed
        2. Enter valid credentials → Fields populated
        3. Click submit → User logged in
        
        Tags: smoke, auth, login
        Custom Fields: Layer=UI, Component=Auth"
    """
    auth_context = get_auth_context(api_token=api_token)
    service = SearchService(auth_context)
    
    test_case = await service.get_test_case_details(test_case_id)
    return _format_test_case_details(test_case)
```

### Service Method

```python
# src/services/search_service.py

async def get_test_case_details(self, test_case_id: int) -> TestCase:
    """Retrieve complete test case details.
    
    Raises:
        TestCaseNotFoundError: If test case doesn't exist.
    """
    return await self._client.get_test_case(test_case_id)
```

### Response Formatter

```python
def _format_test_case_details(tc: TestCase) -> str:
    """Format test case as LLM-friendly text."""
    lines = [
        f"**Test Case TC-{tc.id}: {tc.name}**",
        f"Status: {tc.status} | Automation: {tc.automation_status}",
        "",
    ]
    
    if tc.description:
        lines.extend(["**Description:**", tc.description, ""])
    
    if tc.preconditions:
        lines.extend(["**Preconditions:**", tc.preconditions, ""])
    
    if tc.steps:
        lines.append("**Steps:**")
        for i, step in enumerate(tc.steps, 1):
            lines.append(f"{i}. {step.action} → {step.expected}")
        lines.append("")
    
    if tc.tags:
        lines.append(f"**Tags:** {', '.join(tc.tags)}")
    
    if tc.custom_fields:
        cf_str = ", ".join(f"{k}={v}" for k, v in tc.custom_fields.items())
        lines.append(f"**Custom Fields:** {cf_str}")
    
    return "\n".join(lines)
```

### Error Handling

The global exception handler should produce:
```
Unable to find Test Case with ID 99999.

Suggestions:
- Verify the test case ID is correct
- Use list_test_cases to find valid IDs in your project
- Check you have access to the project containing this test case
```

### Project Structure Notes

Files modified/created:
- `src/tools/search.py` - Add `get_test_case_details` tool
- `src/services/search_service.py` - Add `get_test_case_details` method

### Dependencies

- Requires Story 3.1 (SearchService foundation)
- Requires Story 1.2 (AllureClient, Pydantic models)
- Reuses authentication from Story 1.1

### Testing Strategy

```python
# tests/unit/test_search_service.py

async def test_get_test_case_details_returns_full_data():
    """Service returns complete test case with all fields."""
    mock_response = TestCase(
        id=123,
        name="Login Test",
        description="Test login flow",
        steps=[Step(action="Click", expected="Button pressed")],
        tags=["smoke", "auth"],
        custom_fields={"Layer": "UI"},
    )
    mock_client = AsyncMock()
    mock_client.get_test_case.return_value = mock_response
    
    service = SearchService(mock_client)
    result = await service.get_test_case_details(123)
    
    assert result.id == 123
    assert len(result.steps) == 1
    assert "smoke" in result.tags


async def test_get_test_case_not_found_raises_error():
    """Service raises appropriate error for missing test case."""
    mock_client = AsyncMock()
    mock_client.get_test_case.side_effect = AllureNotFoundError("Not found")
    
    service = SearchService(mock_client)
    
    with pytest.raises(TestCaseNotFoundError):
        await service.get_test_case_details(99999)
```

### References

- [Source: specs/project-planning-artifacts/epics.md#Story 3.2]
- [Source: specs/architecture.md#Error Handling Strategy]
- [Source: specs/project-context.md#Tool Outputs]

## Dev Agent Record

### Agent Model Used

_To be filled by implementing agent_

### Completion Notes List

_To be filled during implementation_

### File List

_To be filled during implementation_
