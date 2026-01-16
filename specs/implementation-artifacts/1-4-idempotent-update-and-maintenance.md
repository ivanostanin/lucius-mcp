# Story 1.4: Idempotent Update & Maintenance

Status: done

## Story

As an AI Agent,
I want to update fields of an existing test case idempotently,
so that I can refine test documentation without creating duplicates or losing data.

## Acceptance Criteria

1. **Given** an existing Test Case ID, **when** I call `update_test_case` with partial fields, **then** the system performs a partial update without overwriting unspecified fields.
2. Repeated calls with the same data result in no state change (idempotency).
3. The server returns a confirmation of the update.

## Tasks / Subtasks

- [x] **Task 1: Extend TestCaseService with Update Method** (AC: #1, #2)
  - [x] 1.1: Add `async def update_test_case(self, test_case_id: int, data: TestCaseUpdate) -> TestCase` to `TestCaseService`
  - [x] 1.2: Implement partial update logic - only send non-None fields
  - [x] 1.3: Fetch current state before update to support idempotency check
  - [x] 1.4: Compare incoming data with current state to detect no-op scenarios
  - [x] 1.5: Return existing state unchanged if update would have no effect (idempotency)

- [x] **Task 2: Implement Get Test Case for Idempotency** (AC: #2)
  - [x] 2.1: Add `async def get_test_case(self, test_case_id: int) -> TestCase` to `TestCaseService`
  - [x] 2.2: Handle 404 responses with `AllureNotFoundError`
  - [x] 2.3: Cache fetched test case for duration of update operation

- [x] **Task 3: Create Update Tool Definition** (AC: #1, #3)
  - [x] 3.1: Add `update_test_case` tool to `src/tools/update_test_case.py`
  - [x] 3.2: Accept `test_case_id` as required parameter
  - [x] 3.3: All other parameters optional (partial update support)
  - [x] 3.4: Return human-readable confirmation: "Updated Test Case [ID]: [changes summary]"
  - [x] 3.5: Return "No changes needed" message for idempotent no-op calls

- [x] **Task 4: Implement Partial Update Logic** (AC: #1)
  - [x] 4.1: Create `TestCaseUpdate` Pydantic model (all fields optional)
  - [x] 4.2: Filter out None values before API call
  - [x] 4.3: Support updating: name, description, precondition, steps, tags, custom_fields
  - [x] 4.4: Support step modifications: add, remove, reorder
  - [x] 4.5: Support tag modifications: add, remove

- [x] **Task 5: Quality Assurance** (AC: implicit)
  - [x] 5.1: Write unit tests for update scenarios in `test_case_service.py`
  - [x] 5.2: Write idempotency tests - same call twice yields same result
  - [x] 5.3: Write partial update tests - unspecified fields unchanged
  - [x] 5.4: Run `mypy --strict` and `ruff check`
  - [x] 5.5: Run tests with `--alluredir=allure-results` for allure-pytest reporting

- [x] **Task 6: E2E Tests** (AC: implicit, NFR11)
  - [x] 6.1: Create `tests/e2e/test_update_test_case.py`
  - [x] 6.2: Write E2E test updating test case in sandbox
  - [x] 6.3: Verify idempotency in sandbox - update twice, same result
  - [x] 6.4: Verify partial update behavior with real API

## Dev Notes

### Idempotency Implementation (CRITICAL)

**What Idempotency Means:**
- Calling `update_test_case(id=123, name="Foo")` twice should have the same effect as calling it once
- The second call should NOT fail, it should succeed with "no changes"
- This is essential for AI agents that may retry operations

**Implementation Pattern:**
```python
async def update_test_case(
    self,
    test_case_id: int,
    data: TestCaseUpdate,
) -> tuple[TestCase, bool]:  # Returns (result, was_modified)
    """Update test case with idempotency support.
    
    Returns:
        Tuple of (updated TestCase, bool indicating if changes were made)
    """
    # 1. Fetch current state
    current = await self.get_test_case(test_case_id)
    
    # 2. Build update payload (only non-None fields)
    update_fields = data.model_dump(exclude_none=True)
    
    # 3. Check if update would change anything
    if self._is_noop(current, update_fields):
        return current, False  # No changes needed
    
    # 4. Perform the update
    updated = await self._client.update_test_case(test_case_id, data)
    return updated, True
```

**No-Op Detection:**
```python
def _is_noop(self, current: TestCase, updates: dict[str, Any]) -> bool:
    """Check if updates would result in any changes."""
    for field, new_value in updates.items():
        current_value = getattr(current, field, None)
        if current_value != new_value:
            return False
    return True  # All fields already have desired values
```

### Tool Response Messages

**Change Made:**
```
✅ Updated Test Case 12345: 'Login Test'

Changes applied:
- name: "Login Test" → "User Login Test"
- description: Added detailed steps
- tags: Added ["smoke", "regression"]
```

**No Changes (Idempotent):**
```
ℹ️ No changes needed for Test Case 12345

The test case already matches the requested state.
```

### Partial Update - Field Handling

```python
# Tool signature - ALL optional except test_case_id
@mcp.tool
async def update_test_case(
    test_case_id: int,
    name: str | None = None,
    description: str | None = None,
    precondition: str | None = None,
    steps: list[dict[str, str]] | None = None,
    tags: list[str] | None = None,
    custom_fields: dict[str, str] | None = None,
) -> str:
    """Update an existing test case with partial data.
    
    Only provided fields will be updated. Omitted fields remain unchanged.
    Repeated calls with the same data are idempotent (no duplicate changes).
    
    Args:
        test_case_id: The Allure test case ID to update (required).
            Found in the URL: /testcase/12345 → test_case_id=12345
        name: New name for the test case (optional)
        description: New description in markdown (optional)
        precondition: New preconditions text (optional)
        steps: Complete replacement of steps (optional).
            If provided, replaces ALL existing steps.
        tags: New tag list (optional).
            If provided, replaces ALL existing tags.
        custom_fields: Custom field updates (optional).
            Merges with existing custom fields.
    
    Returns:
        Confirmation message with summary of changes made,
        or "No changes needed" if update is idempotent.
    """
```

### Step Update Behavior

**IMPORTANT:** Steps are replaced entirely, not merged:
```python
# Current steps: [A, B, C]
# Update with: [A, D]
# Result: [A, D]  (not [A, B, C, D])
```

If agent wants to add a step, it must:
1. Fetch current test case
2. Append new step to existing steps
3. Send complete step list

### Tag Update Behavior

Same as steps - replacement, not merge:
```python
# Current tags: ["smoke", "login"]
# Update with: ["regression"]
# Result: ["regression"]  (not ["smoke", "login", "regression"])
```

### Custom Fields Merge Behavior

Custom fields are MERGED (different from steps/tags):
```python
# Current: {"Layer": "UI", "Priority": "High"}
# Update with: {"Priority": "Low", "Component": "Auth"}
# Result: {"Layer": "UI", "Priority": "Low", "Component": "Auth"}
```

### Previous Story Dependencies

**From Story 1.3:**
- `TestCaseService` class in `src/services/case_service.py`
- `create_test_case` tool in `src/tools/cases.py`
- Service/Tool communication pattern established

**Required Models from Story 1.2:**
- `TestCase` - full test case response
- `TestCaseUpdate` - partial update request (may need to create if not generated)

### Error Handling

**Not Found:**
```
❌ Error: Test Case Not Found

Test Case ID '99999' does not exist.

Suggestions:
- Verify the test case ID from the Allure URL
- Use search_test_cases to find the correct ID
- The test case may have been deleted
```

**Validation Error:**
```
❌ Error: Validation Failed

The 'name' field cannot be empty when provided.

Suggestions:
- Provide a non-empty name, or omit it to keep current value
```

### References

- [Source: specs/prd.md#FR6 - Idempotent Updates]
- [Source: specs/architecture.md#API Patterns]
- [Source: Story 1.3 - TestCaseService Pattern]

## Dev Agent Record

### Agent Model Used

Antigravity (Google Deepmind)

### Completion Notes List

- Implemented `update_test_case` as a standalone tool in `src/tools/update_test_case.py` instead of `cases.py` to keep files small and focused, following the "Thin Tool" pattern.
- Implemented robust idempotency checks by comparing current state fields with update data.
- Added support for partial updates, maintaining existing data where input fields are None.
- Added comprehensive unit and E2E tests covering various update scenarios, including attachments and steps.

### File List

- `src/services/test_case_service.py`
- `src/tools/update_test_case.py`
- `tests/unit/test_test_case_service.py`
- `tests/e2e/test_update_test_case.py`
