# Story 2.3: Link Shared Step to Test Case

Status: ready-for-dev

## Story

As an AI Agent,
I want to attach a Shared Step to a Test Case by reference ID,
so that I can maintain consistency and reduce manual duplication of test logic.

## Acceptance Criteria

1. **Given** a Test Case and a Shared Step ID, **when** I add the shared step reference to the Test Case's step list, **then** the Allure API correctly links the shared logic to the test case.
2. The test case reflects the shared steps in its execution flow.

## Tasks / Subtasks

- [ ] **Task 1: Understand Allure Linking Mechanism** (AC: #1)
  - [ ] 1.1: Research how Allure API represents shared step references in test cases
  - [ ] 1.2: Document the step structure (inline vs reference)
  - [ ] 1.3: Verify if steps can mix inline and shared references
  - [ ] 1.4: Check if position/order matters for shared step insertion

- [ ] **Task 2: Extend TestCaseService** (AC: #1, #2)
  - [ ] 2.1: Add `async def add_shared_step_to_case(self, test_case_id: int, shared_step_id: int, position: int | None) -> TestCase`
  - [ ] 2.2: Add `async def remove_shared_step_from_case(self, test_case_id: int, shared_step_id: int) -> TestCase`
  - [ ] 2.3: Implement step list manipulation logic
  - [ ] 2.4: Validate shared step exists before linking

- [ ] **Task 3: Create MCP Tool Definitions** (AC: #1, #2)
  - [ ] 3.1: Add `link_shared_step` tool to `src/tools/cases.py` (or new file)
  - [ ] 3.2: Add `unlink_shared_step` tool
  - [ ] 3.3: Add comprehensive LLM-optimized docstrings
  - [ ] 3.4: Return clear confirmation with updated step list

- [ ] **Task 4: Handle Step Ordering** (AC: #2)
  - [ ] 4.1: Support inserting shared step at specific position
  - [ ] 4.2: Support appending to end of step list (default)
  - [ ] 4.3: Handle edge cases (empty step list, invalid position)

- [ ] **Task 5: Quality Assurance** (AC: implicit)
  - [ ] 5.1: Write unit tests for linking operations
  - [ ] 5.2: Test position insertion scenarios
  - [ ] 5.3: Test unlinking and step list update
  - [ ] 5.4: Run `mypy --strict` and `ruff check`
  - [ ] 5.5: Run tests with `--alluredir=allure-results` for allure-pytest reporting

- [ ] **Task 6: E2E Tests** (AC: implicit, NFR11)
  - [ ] 6.1: Create `tests/e2e/test_link_shared_step.py`
  - [ ] 6.2: Write E2E test linking shared step to test case in sandbox
  - [ ] 6.3: Verify linked test case retrieval shows shared step reference
  - [ ] 6.4: Write E2E test unlinking and verifying step list update

## Dev Notes

### How Shared Step References Work

Test case steps can contain two types of entries:
1. **Inline Steps**: Direct action/expected pairs
2. **Shared Step References**: Pointer to a shared step by ID

**Example Test Case Step List:**
```python
steps = [
    # Inline step
    {"type": "step", "action": "Open browser", "expected": "Browser opens"},
    
    # Shared step reference (expands to multiple steps at runtime)
    {"type": "shared", "shared_step_id": 789},  # "Login as Admin" 
    
    # Inline step
    {"type": "step", "action": "Click Settings", "expected": "Settings page"},
]
```

At execution time, the shared step reference expands to its full step sequence.

### Allure API Step Structure

The exact structure depends on the Allure OpenAPI spec, but typically:

```python
# Step item in test case
class StepItem(BaseModel):
    # For inline steps
    action: str | None = None
    expected: str | None = None
    
    # For shared step reference
    shared_step_id: int | None = None
    
    # Discriminator
    step_type: Literal["inline", "shared"] = "inline"
```

### Service Implementation

```python
async def add_shared_step_to_case(
    self,
    test_case_id: int,
    shared_step_id: int,
    position: int | None = None,
) -> TestCase:
    """Add a shared step reference to a test case.
    
    Args:
        test_case_id: Target test case
        shared_step_id: Shared step to link
        position: Where to insert (0-indexed). None = append to end.
    
    Returns:
        Updated TestCase with new step list
    """
    # 1. Verify shared step exists
    shared_step = await self._shared_step_service.get_shared_step(shared_step_id)
    
    # 2. Get current test case
    test_case = await self.get_test_case(test_case_id)
    
    # 3. Build new step list with shared reference
    current_steps = list(test_case.steps or [])
    shared_ref = StepItem(step_type="shared", shared_step_id=shared_step_id)
    
    if position is None:
        current_steps.append(shared_ref)
    else:
        current_steps.insert(position, shared_ref)
    
    # 4. Update test case
    return await self._client.update_test_case(
        test_case_id,
        TestCaseUpdate(steps=current_steps)
    )
```

### Tool Definition - link_shared_step

```python
@mcp.tool
async def link_shared_step(
    test_case_id: int,
    shared_step_id: int,
    position: int | None = None,
) -> str:
    """Link a shared step to a test case.
    
    Adds a reference to the shared step in the test case's step list.
    The shared step's actions will expand at execution time.
    
    Args:
        test_case_id: The test case to modify.
            Found in URL: /testcase/12345
        shared_step_id: The shared step to link.
            Found via list_shared_steps or in Allure UI.
        position: Where to insert the shared step (0-indexed, optional).
            - 0 = Insert at beginning
            - None = Append to end (default)
            - N = Insert after step N
    
    Returns:
        Confirmation with updated step list preview.
    
    Example:
        link_shared_step(
            test_case_id=12345,
            shared_step_id=789,  # "Login as Admin"
            position=0  # Insert at beginning
        )
        → "Linked 'Login as Admin' to Test Case 12345 at position 0.
           
           Updated steps:
           1. [Shared: Login as Admin] (4 steps)
           2. Navigate to Dashboard
           3. Verify widgets loaded"
    
    Tip: Use list_shared_steps to find available shared steps before linking.
    """
```

### Tool Definition - unlink_shared_step

```python
@mcp.tool
async def unlink_shared_step(
    test_case_id: int,
    shared_step_id: int,
) -> str:
    """Remove a shared step reference from a test case.
    
    Removes the link to the shared step. The test case will no longer
    include those steps at execution time.
    
    Args:
        test_case_id: The test case to modify.
        shared_step_id: The shared step to unlink.
    
    Returns:
        Confirmation with updated step list.
    
    Note: This only removes the REFERENCE. The shared step itself
    remains in the library and other test cases are unaffected.
    
    Example:
        unlink_shared_step(test_case_id=12345, shared_step_id=789)
        → "Unlinked 'Login as Admin' from Test Case 12345.
           
           Remaining steps:
           1. Navigate to Dashboard
           2. Verify widgets loaded"
    """
```

### Response Formatting

**Link Success:**
```
✅ Linked Shared Step to Test Case 12345

Added: 'Login as Admin' (ID: 789) at position 0

Updated step sequence:
1. 📦 [Shared: Login as Admin] (4 steps)
   └─ Expands to: Navigate → Enter creds → Click Login → Verify
2. Navigate to Dashboard
3. Click Settings
4. Verify settings page
```

**Link Already Exists:**
```
ℹ️ Shared Step 789 is already linked to Test Case 12345

Current position: Step 1

No changes made. Use update_test_case if you need to change position.
```

**Unlink Success:**
```
✅ Unlinked Shared Step from Test Case 12345

Removed: 'Login as Admin' (ID: 789)

Remaining steps:
1. Navigate to Dashboard
2. Click Settings
3. Verify settings page
```

### Position Examples

```
Original: [Step A, Step B, Step C]

link_shared_step(..., position=0):
Result: [Shared, Step A, Step B, Step C]

link_shared_step(..., position=1):
Result: [Step A, Shared, Step B, Step C]

link_shared_step(..., position=None):  # Default - append
Result: [Step A, Step B, Step C, Shared]
```

### Error Handling

**Shared Step Not Found:**
```
❌ Error: Shared Step Not Found

Shared Step ID '999' does not exist.

Suggestions:
- Use list_shared_steps to find available shared steps
- The step may have been deleted
```

**Test Case Not Found:**
```
❌ Error: Test Case Not Found

Test Case ID '12345' does not exist.

Suggestions:
- Verify the test case ID from the Allure URL
- Use search_test_cases to find the correct ID
```

**Invalid Position:**
```
❌ Error: Invalid Position

Position 10 is out of range. The test case has 3 steps (valid: 0-3).

Suggestions:
- Use position=None to append to end
- Use position=0 to insert at beginning
```

### Previous Story Dependencies

**From Story 1.4:**
- `TestCaseService.get_test_case()` method
- `TestCaseService.update_test_case()` method

**From Story 2.1:**
- `SharedStepService.get_shared_step()` method
- Shared step model structure

### Epic 2 Completion Checklist

After this story, Epic 2 should provide:
- ✅ Create shared steps with named step sequences (2.1)
- ✅ List shared steps in project library (2.1)
- ✅ Update shared steps with propagation (2.2)
- ✅ Delete shared steps with safety checks (2.2)
- ✅ Link shared step to test case (2.3)
- ✅ Unlink shared step from test case (2.3)
- ✅ Position-aware step insertion

### References

- [Source: specs/prd.md#FR3 - Attach Shared Steps]
- [Source: specs/epics.md#Story 2.3]
- [Source: Story 2.1 - SharedStep Structure]
- [Source: Story 1.4 - TestCase Update Pattern]

## Dev Agent Record

### Agent Model Used

_To be filled by implementing agent_

### Completion Notes List

_To be filled during implementation_

### File List

_To be filled during implementation_
