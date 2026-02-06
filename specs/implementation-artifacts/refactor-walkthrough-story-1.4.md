# Test Review Recommendations Addressed

I have addressed the recommendations from `specs/test-review-story-1.4.md`:

## Changes Implemented

### 1. Centralize Test Data
- **Problem**: `pixel_b64` definition was duplicated.
- **Solution**: Moved `pixel_b64` to `tests/e2e/conftest.py` as a pytest fixture.

### 2. Standardize Fixture Usage
- **Problem**: `test_update_test_case_e2e` was manually instantiating `AllureClient`.
- **Solution**: Updated the test to use the `allure_client` fixture, ensuring consistent authentication and resource management.

### 3. Reduce File Length
- **Problem**: `tests/e2e/test_update_test_case.py` was >600 lines.
- **Solution**: Split the file into two:
  - `tests/e2e/test_update_test_case.py`: Contains "Core" updates (fields, status, tags, custom fields) and the main E2E flow.
  - `tests/e2e/test_update_test_case_extended.py`: Contains "Extended" updates (steps, attachments, links, nested steps).

### 4. Code Quality
- Verified that all new and modified files pass `mypy` type checking (fixed several typing issues related to generated clients).
- Verified `ruff` linting passes.

## Verification
- Ran `pytest` to ensure tests are discovered (skipped due to missing env vars, but discovery confirms syntax and import correctness).
- Ran `mypy` and `ruff` with success.

## Files Modified
- [tests/e2e/conftest.py](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/tests/e2e/conftest.py)
- [tests/e2e/test_update_test_case.py](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/tests/e2e/test_update_test_case.py)
- [tests/e2e/test_update_test_case_extended.py](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/tests/e2e/test_update_test_case_extended.py) (New)
