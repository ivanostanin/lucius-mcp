# Story 2.2: Update & Delete Shared Steps

Status: ready-for-dev

## Story

As an AI Agent,
I want to modify or remove Shared Steps in the library,
so that the reusable library can evolve alongside the product requirements.

## Acceptance Criteria

1. **Given** an existing Shared Step, **when** I call `update_shared_step` to modify its steps or metadata, **then** the changes are saved and propagated where applicable.
2. **When** I call `delete_shared_step`, it is removed/archived from the library.

## Tasks / Subtasks

- [ ] **Task 1: Extend SharedStepService with Update Method** (AC: #1)
  - [ ] 1.1: Add `async def update_shared_step(self, step_id: int, data: SharedStepUpdate) -> SharedStep`
  - [ ] 1.2: Implement partial update logic (only non-None fields)
  - [ ] 1.3: Implement idempotency check (same as Story 1.4 pattern)
  - [ ] 1.4: Add `async def get_shared_step(self, step_id: int) -> SharedStep` for fetch

- [ ] **Task 2: Extend SharedStepService with Delete Method** (AC: #2)
  - [ ] 2.1: Add `async def delete_shared_step(self, step_id: int) -> DeleteResult`
  - [ ] 2.2: Handle already-deleted steps gracefully (idempotent)
  - [ ] 2.3: Check for linked test cases before deletion (warning)
  - [ ] 2.4: Implement soft delete if supported by API

- [ ] **Task 3: Extend AllureClient** (AC: #1, #2)
  - [ ] 3.1: Add `update_shared_step` method to `AllureClient`
  - [ ] 3.2: Add `delete_shared_step` method to `AllureClient`
  - [ ] 3.3: Add `get_shared_step` method to `AllureClient`

- [ ] **Task 4: Create MCP Tool Definitions** (AC: #1, #2)
  - [ ] 4.1: Add `update_shared_step` tool to `src/tools/shared_steps.py`
  - [ ] 4.2: Add `delete_shared_step` tool to `src/tools/shared_steps.py`
  - [ ] 4.3: Add comprehensive LLM-optimized docstrings
  - [ ] 4.4: Include safety confirmation for delete (same as Story 1.5)

- [ ] **Task 5: Quality Assurance** (AC: implicit)
  - [ ] 5.1: Extend unit tests in `test_shared_step_service.py`
  - [ ] 5.2: Test idempotency for update operations
  - [ ] 5.3: Test cascade warning for delete with linked cases
  - [ ] 5.4: Run `mypy --strict` and `ruff check`
  - [ ] 5.5: Run tests with `--alluredir=allure-results` for allure-pytest reporting
  - [ ] 5.6: Verify error hints for invalid inputs (Actionable Error Handling)

- [ ] **Task 6: E2E Tests** (AC: implicit, NFR11)
  - [ ] 6.1: Extend `tests/e2e/test_shared_steps.py`
  - [ ] 6.2: Write E2E test updating shared step in sandbox
  - [ ] 6.3: Write E2E test verifying update propagates to linked test cases
  - [ ] 6.4: Write E2E test for delete with and without linked cases

## Dev Notes

### Update Propagation (CRITICAL CONCEPT)

When a Shared Step is updated, all Test Cases that reference it automatically get the new steps. This is the key benefit of shared steps:

**Before Update:**
```
Shared Step 789: "Login as Admin"
├── Step 1: Go to /login
├── Step 2: Enter admin credentials
└── Step 3: Click Login

Test Case A → uses Shared Step 789
Test Case B → uses Shared Step 789
Test Case C → uses Shared Step 789
```

**After Update (add step 4):**
```
Shared Step 789: "Login as Admin"
├── Step 1: Go to /login
├── Step 2: Enter admin credentials
├── Step 3: Click Login
└── Step 4: Verify admin badge visible  ← NEW

Test Case A → automatically has 4 steps now
Test Case B → automatically has 4 steps now
Test Case C → automatically has 4 steps now
```

### Tool Definition - update_shared_step

```python
@mcp.tool
async def update_shared_step(
    step_id: int,
    name: str | None = None,
    steps: list[dict[str, str]] | None = None,
    description: str | None = None,
) -> str:
    """Update an existing shared step.
    
    ⚠️ IMPORTANT: Changes propagate to ALL test cases using this shared step.
    
    Only provided fields will be updated. Omitted fields remain unchanged.
    Repeated calls with the same data are idempotent.
    
    Args:
        step_id: The shared step ID to update (required).
            Found via list_shared_steps or in the Allure URL.
        name: New name for the shared step (optional).
        steps: Complete replacement of step sequence (optional).
            If provided, replaces ALL existing steps.
            Format: [{"action": "...", "expected": "..."}]
        description: New description (optional).
    
    Returns:
        Confirmation message with summary of changes.
        Includes count of affected test cases.
    
    Example:
        update_shared_step(
            step_id=789,
            steps=[
                {"action": "Go to /login", "expected": "Login page loads"},
                {"action": "Enter admin@test.com", "expected": "Email entered"},
                {"action": "Click Login", "expected": "Logged in"},
                {"action": "Verify admin badge", "expected": "Badge visible"},
            ]
        )
    
    Note: Step sequences are REPLACED entirely, not merged. To add a step,
    fetch current steps first, append the new step, then update.
    """
```

### Tool Definition - delete_shared_step

```python
@mcp.tool
async def delete_shared_step(
    step_id: int,
    confirm: bool = False,
    force: bool = False,
) -> str:
    """Delete a shared step from the library.
    
    ⚠️ CAUTION: If this shared step is used by test cases, deleting it
    will break those references. Use force=True to override this warning.
    
    Args:
        step_id: The shared step ID to delete (required).
        confirm: Must be True to proceed (safety measure).
        force: If True, delete even if test cases reference this step.
            The linked test cases will have broken step references.
    
    Returns:
        Confirmation message, or warning if step is in use.
    
    Example (safe delete):
        delete_shared_step(step_id=789, confirm=True)
        → "Archived Shared Step 789: 'Login as Admin'"
    
    Example (in use warning):
        delete_shared_step(step_id=789, confirm=True)
        → "⚠️ Cannot delete: 15 test cases use this shared step.
           Use force=True to delete anyway (will break references)."
    
    Example (forced delete):
        delete_shared_step(step_id=789, confirm=True, force=True)
        → "Deleted Shared Step 789. Warning: 15 test cases now have broken references."
    """
```

### Idempotency Pattern (from Story 1.4)

```python
async def update_shared_step(
    self,
    step_id: int,
    data: SharedStepUpdate,
) -> tuple[SharedStep, bool]:
    """Update with idempotency support."""
    current = await self.get_shared_step(step_id)
    update_fields = data.model_dump(exclude_none=True)
    
    if self._is_noop(current, update_fields):
        return current, False  # No changes needed
    
    updated = await self._client.update_shared_step(step_id, data)
    return updated, True
```

### Linked Test Case Detection

Before deleting, check for linked test cases:

```python
async def delete_shared_step(
    self,
    step_id: int,
    force: bool = False,
) -> DeleteResult:
    """Delete shared step with linked case check."""
    # Check for linked test cases
    linked_cases = await self._client.get_test_cases_by_shared_step(step_id)
    
    if linked_cases and not force:
        return DeleteResult(
            step_id=step_id,
            status="blocked",
            message=f"Cannot delete: {len(linked_cases)} test cases use this step",
            linked_count=len(linked_cases),
        )
    
    # Proceed with deletion
    await self._client.delete_shared_step(step_id)
    
    return DeleteResult(
        step_id=step_id,
        status="deleted",
        message="Shared step deleted",
        linked_count=len(linked_cases) if linked_cases else 0,
    )
```

### Response Examples

**Update Success:**
```
✅ Updated Shared Step 789: 'Login as Admin'

Changes applied:
- steps: Updated from 3 steps to 4 steps

📢 Propagated to 15 linked test cases.
```

**Update No-Op:**
```
ℹ️ No changes needed for Shared Step 789

The shared step already matches the requested state.
```

**Delete Blocked:**
```
⚠️ Cannot delete Shared Step 789: 'Login as Admin'

This step is used by 15 test cases:
- TC-1234: User Login Flow
- TC-1235: Admin Dashboard Access
- TC-1236: Permission Check
... and 12 more

Options:
1. Update the test cases to remove this shared step first
2. Use force=True to delete anyway (will break references)
```

**Delete Forced:**
```
🗑️ Deleted Shared Step 789: 'Login as Admin'

⚠️ Warning: 15 test cases now have broken step references.
Consider running a cleanup to fix or remove these references.
```

### Previous Story Dependencies

**From Story 2.1:**
- `SharedStepService` class with create/list methods
- `src/tools/shared_steps.py` tool file
- `AllureClient` shared step methods

**From Stories 1.4 & 1.5:**
- Idempotency pattern for updates
- Safety confirmation pattern for deletes
- `DeleteResult` model

### References

- [Source: specs/prd.md#FR8 - Update Shared Steps]
- [Source: Story 1.4 - Idempotency Pattern]
- [Source: Story 1.5 - Delete Safety Pattern]
- [Source: Story 2.1 - SharedStepService]

## Dev Agent Record

### Agent Model Used

_To be filled by implementing agent_

### Completion Notes List

_To be filled during implementation_

### File List

_To be filled during implementation_
