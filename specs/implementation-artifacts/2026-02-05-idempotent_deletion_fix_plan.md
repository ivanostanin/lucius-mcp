# Idempotent Deletion Feedback Fix

The goal is to ensure that deletion tools report "Deleted successfully" ONLY if the entity existed and was deleted, and "Already archived/deleted" if it did not exist. This requires a "check-then-delete" pattern in the services, as the underlying API presumably returns success (200/204) for idempotent deletions of non-existent entities.

## User Review Required

> [!NOTE]
> This change introduces a "Check then Act" pattern (get -> delete) which adds an extra API call. This is acceptable for Agent Tools where accurate feedback is prioritized over raw performance.

## Entity Analysis

I have scanned the codebase for all deletion tools and services to identify which ones require this fix:

| Entity | Tool | Service Method | Status |
|--------|------|----------------|--------|
| **Test Layer** | `delete_test_layer` | `TestLayerService.delete_test_layer` | **Needs Fix** |
| **Test Layer Schema** | `delete_test_layer_schema` | `TestLayerService.delete_test_layer_schema` | **Needs Fix** |
| **Shared Step** | `delete_shared_step` | `SharedStepService.delete_shared_step` | **Needs Fix** |
| **Test Case** | `delete_test_case` | `TestCaseService.delete_test_case` | **Already Correct** (Checks status/existence) |
| **Launch** | *None* | *N/A* | No deletion tool found |
| **Attachment** | *None* | *N/A* | No deletion tool found |

## Proposed Changes

### Services

#### [MODIFY] [test_layer_service.py](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/services/test_layer_service.py)
- **`delete_test_layer`**: 
    - Attempt to `get_test_layer` first.
    - If `AllureNotFoundError` (or equivalent) is raised, return `False`.
    - If found, proceed to `delete` and return `True`.
- **`delete_test_layer_schema`**:
    - Attempt to `get_test_layer_schema` first.
    - If not found, return `False`.
    - If found, delete and return `True`.

#### [MODIFY] [shared_step_service.py](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/services/shared_step_service.py)
- **`delete_shared_step`**:
    - Change return type from `None` to `bool`.
    - Attempt to `get_shared_step` first.
    - If not found, return `False`.
    - If found, delete and return `True`.

### Tools

#### [MODIFY] [shared_steps.py](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/tools/shared_steps.py)
- **`delete_shared_step`**:
    - Update logic to handle the boolean return value from the service.
    - Return a specific message if `False` returned (already deleted).

*(Note: `delete_test_layer.py` and `delete_test_layer_schema.py` tools already rely on the boolean return from the service, so they should work automatically once the service is updated, assuming they use the return value correctly.)*

### Tests

#### [MODIFY] [test_test_layer_service.py](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/tests/unit/test_test_layer_service.py)
- Update `test_delete_test_layer_success` to mock the `get` call returning a layer.
- Update `test_delete_test_layer_idempotent` to mock the `get` call raising `AllureNotFoundError`.
- Update `test_delete_test_layer_schema_success` and `idempotent` similarly.

#### [MODIFY] [test_shared_step_service.py](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/tests/unit/test_shared_step_service.py)
- Update `test_delete_shared_step_success` to mock `get_shared_step` and assert `True` return.
- Update `test_delete_shared_step_idempotent` to mock `get_shared_step` raising exception and assert `False` return.

## Verification Plan

### Automated Tests
Run the updated unit tests:
```bash
uv run --env-file .env.test pytest tests/unit/test_test_layer_service.py tests/unit/test_shared_step_service.py
```

### Manual Verification
1. **Test Layer Deletion**:
    - Run `list_test_layers` to find a layer ID (or create one).
    - Run `delete_test_layer(layer_id=...)`. Expect: "Deleted successfully".
    - Run `delete_test_layer(layer_id=...)` AGAIN. Expect: "Already deleted".
2. **Test Layer Schema Deletion**:
    - Similar steps with `list_test_layer_schemas` and `delete_test_layer_schema`.
3. **Shared Step Deletion**:
    - Similar steps with `list_shared_steps` and `delete_shared_step`.
