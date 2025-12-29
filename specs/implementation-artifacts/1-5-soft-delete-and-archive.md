# Story 1.5: Soft Delete & Archive

Status: ready-for-dev

## Story

As an AI Agent,
I want to archive obsolete test cases,
so that the test repository remains focused on the current product state.

## Acceptance Criteria

1. **Given** an existing Test Case, **when** I call `delete_test_case`, **then** the test case status is updated to "Archived" or moved to the soft-delete bin in Allure.
2. The tool returns a confirmation of the archival.

## Tasks / Subtasks

- [ ] **Task 1: Research Allure Delete Behavior** (AC: #1)
  - [ ] 1.1: Verify Allure TestOps DELETE endpoint behavior (soft vs hard delete)
  - [ ] 1.2: Document the actual status/state change on delete
  - [ ] 1.3: Determine if deleted test cases are recoverable
  - [ ] 1.4: Check for any associated data cleanup (steps, attachments)

- [ ] **Task 2: Extend TestCaseService with Delete Method** (AC: #1)
  - [ ] 2.1: Add `async def delete_test_case(self, test_case_id: int) -> DeleteResult` to `TestCaseService`
  - [ ] 2.2: Implement soft delete via Allure API
  - [ ] 2.3: Handle already-deleted test cases gracefully (idempotent)
  - [ ] 2.4: Return structured result with deletion status

- [ ] **Task 3: Create Delete Tool Definition** (AC: #2)
  - [ ] 3.1: Add `delete_test_case` tool to `src/tools/cases.py`
  - [ ] 3.2: Accept `test_case_id` as required parameter
  - [ ] 3.3: Add optional `confirm` parameter for safety (default: True required)
  - [ ] 3.4: Return human-readable confirmation: "Archived Test Case [ID]: '[Name]'"

- [ ] **Task 4: Implement Safety Checks** (AC: #1)
  - [ ] 4.1: Verify test case exists before attempting delete
  - [ ] 4.2: Warn if test case is linked to recent launches
  - [ ] 4.3: Consider adding `force` parameter for override
  - [ ] 4.4: Log deletion for audit purposes

- [ ] **Task 5: Quality Assurance** (AC: implicit)
  - [ ] 5.1: Write unit tests for delete scenarios
  - [ ] 5.2: Write idempotency test - delete same ID twice
  - [ ] 5.3: Write not-found handling test
  - [ ] 5.4: Run `mypy --strict` and `ruff check`
  - [ ] 5.5: Run tests with `--alluredir=allure-results` for allure-pytest reporting

- [ ] **Task 6: E2E Tests** (AC: implicit, NFR11)
  - [ ] 6.1: Create `tests/e2e/test_delete_test_case.py`
  - [ ] 6.2: Write E2E test creating then deleting test case in sandbox
  - [ ] 6.3: Verify deleted case is not retrievable via API
  - [ ] 6.4: Verify idempotent delete behavior - delete twice succeeds

## Dev Notes

### Soft Delete vs Hard Delete

**Expected Allure Behavior:**
- Most Allure TestOps instances use **soft delete** (archive)
- Test cases move to "Archived" or "Deleted" status
- Data is retained for audit/recovery purposes
- Some instances may support permanent hard delete

**Implementation Approach:**
```python
async def delete_test_case(self, test_case_id: int) -> DeleteResult:
    """Archive/soft-delete a test case.
    
    Note: This is typically a soft delete. The test case may be
    recoverable from the Allure UI.
    """
    # Verify exists first (for better error messages)
    try:
        test_case = await self.get_test_case(test_case_id)
    except AllureNotFoundError:
        # Already deleted - return success (idempotent)
        return DeleteResult(
            test_case_id=test_case_id,
            status="already_deleted",
            message="Test case was already deleted or doesn't exist"
        )
    
    # Perform deletion
    await self._client.delete_test_case(test_case_id)
    
    return DeleteResult(
        test_case_id=test_case_id,
        status="archived",
        name=test_case.name,
        message=f"Test case '{test_case.name}' has been archived"
    )
```

### DeleteResult Model

```python
from pydantic import BaseModel

class DeleteResult(BaseModel):
    """Result of a delete operation."""
    test_case_id: int
    status: Literal["archived", "deleted", "already_deleted", "not_found"]
    name: str | None = None
    message: str
```

### Tool Definition with Safety

```python
@mcp.tool
async def delete_test_case(
    test_case_id: int,
    confirm: bool = False,
) -> str:
    """Archive an obsolete test case.
    
    This performs a SOFT DELETE (archive). The test case can typically
    be recovered from the Allure UI if needed.
    
    ⚠️ CAUTION: This action removes the test case from active views.
    Historical data and launch associations may be affected.
    
    Args:
        test_case_id: The Allure test case ID to archive (required).
            Found in the URL: /testcase/12345 → test_case_id=12345
        confirm: Must be set to True to proceed with deletion.
            This is a safety measure to prevent accidental deletions.
    
    Returns:
        Confirmation message with the archived test case details.
    
    Example:
        delete_test_case(test_case_id=12345, confirm=True)
        → "Archived Test Case 12345: 'Login Test'"
    
    Raises:
        ValidationError: If confirm is not True
        NotFoundError: If test case doesn't exist (or already deleted)
    """
    if not confirm:
        return (
            "⚠️ Deletion requires confirmation.\n\n"
            "Please call again with confirm=True to proceed with archiving "
            f"test case {test_case_id}."
        )
    
    service = TestCaseService(get_client())
    result = await service.delete_test_case(test_case_id)
    
    if result.status == "already_deleted":
        return f"ℹ️ Test Case {test_case_id} was already archived or doesn't exist."
    
    return f"✅ Archived Test Case {result.test_case_id}: '{result.name}'"
```

### Idempotent Delete Behavior

**First call:**
```
✅ Archived Test Case 12345: 'Login Test'
```

**Second call (same ID):**
```
ℹ️ Test Case 12345 was already archived or doesn't exist.
```

This is idempotent - calling delete twice doesn't error, it just confirms the state.

### Audit Logging

```python
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def delete_test_case(self, test_case_id: int) -> DeleteResult:
    # ... deletion logic ...
    
    logger.info(
        "Test case archived",
        extra={
            "test_case_id": test_case_id,
            "test_case_name": test_case.name,
            "action": "delete",
            "result": "archived",
        }
    )
```

### Error Responses

**Not Found:**
```
ℹ️ Test Case 12345 was already archived or doesn't exist.

If you expected this test case to exist:
- Verify the ID from the Allure URL
- It may have been deleted by another user
- Use search_test_cases to find similar test cases
```

**Confirmation Required:**
```
⚠️ Deletion requires confirmation.

Please call again with confirm=True to proceed with archiving test case 12345.

This safety measure prevents accidental deletions.
```

### Previous Story Dependencies

**From Story 1.3:**
- `TestCaseService` class with `create_test_case` method
- `src/tools/cases.py` tool file structure

**From Story 1.4:**
- `get_test_case` method in `TestCaseService`
- Idempotency pattern established

### Project Structure After Epic 1

```
src/
├── client/
│   ├── __init__.py
│   ├── client.py              # AllureClient (Story 1.2)
│   ├── models.py              # Generated models (Story 1.2)
│   └── exceptions.py          # API exceptions (Story 1.2)
├── tools/
│   ├── __init__.py
│   └── cases.py               # create, update, delete tools
├── services/
│   ├── __init__.py
│   ├── case_service.py        # TestCaseService with all CRUD
│   └── attachment_service.py  # Attachment handling (Story 1.3)
└── utils/
    ├── logger.py              # Structured logging (Story 1.1)
    └── error.py               # Global exception handler (Story 1.1)
```

### Epic 1 Completion Checklist

After this story, Epic 1 should provide:
- ✅ Project initialization with uv, FastMCP, Starlette (1.1)
- ✅ Generated Pydantic models from OpenAPI (1.2)
- ✅ Thin httpx AllureClient (1.2)
- ✅ Create test case with full metadata (1.3)
- ✅ Idempotent partial updates (1.4)
- ✅ Soft delete/archive (1.5)
- ✅ Structured logging with request correlation
- ✅ Global exception handler with Agent Hints

### References

- [Source: specs/prd.md#FR5 - Soft Delete]
- [Source: specs/architecture.md#Error Handling]
- [Source: Story 1.4 - Idempotency Pattern]

## Dev Agent Record

### Agent Model Used

_To be filled by implementing agent_

### Completion Notes List

_To be filled during implementation_

### File List

_To be filled during implementation_
