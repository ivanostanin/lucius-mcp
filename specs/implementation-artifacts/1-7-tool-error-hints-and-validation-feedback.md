# Story 1.7: Tool Error Hints & Validation Feedback

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an AI Agent,
I want to receive clear, actionable error hints when my tool inputs are invalid or incomplete,
So that I can autonomously correct my requests and successfully execute the tool.

## Acceptance Criteria

1. **Structured Validation Errors**: When a tool call fails Pydantic validation (e.g., missing field, wrong type), the server returns a 400 error with a structured message listing *every* invalid field and the specific reason (e.g., "Field 'priority': value is not a valid enumeration member; permitted: 'normal', 'critical'").
2. **Schema Hints**: The error message includes a "Usage Hint" or "Schema Snippet" for the failing model, helping the agent understand the expected format without guessing.
3. **Business Logic Hints**: When `AllureAPIError` is raised (e.g. 404 Not Found), the specific suggestions provided in the exception are strictly formatted and returned in the text response.
4. **Integration Tests for Errors**: A new integration test suite (`tests/integration/test_error_handling.py`) is created that specifically targets:
    - Missing required fields in `create_test_case`.
    - Invalid data types (e.g. string for integer ID).
    - Invalid enum values (e.g. status='super_done').
    - Partial update validation on `update_test_case`.
    - Simulation of "Bad LLM Input" (hallucinated fields, nested structure errors).
5. **Hint Verification in Tests**: These tests MUST assert that the returned error message contains specific "Hint" text or corrected schema details, proving the mechanism works.

## Tasks / Subtasks

- [x] Task 1: Enhance `ValidationError` handling in `src/utils/error.py`
  - [x] Implement a handler that catches Pydantic's `ValidationError`.
  - [x] Parse `e.errors()` to extract location (field name) and message.
  - [x] Format a clear bulleted list of errors: "- field_name: error message".
- [x] Task 2: Implement "Schema Hint" generation
  - [x] Create a utility to generate a simplified schema usage string from a Pydantic model.
  - [x] Integrate this into the exception handler to append usage hints for common errors.
- [x] Task 3: Create Integration Test Suite for Error Scenarios
  - [x] Create `tests/integration/test_error_handling.py`.
  - [x] Test Case 1: `create_test_case` with empty body / missing name.
  - [x] Test Case 2: `create_test_case` with invalid enum (e.g. `layer`).
  - [x] Test Case 3: `update_test_case` with invalid ID type.
  - [x] Test Case 4: `update_test_case` with invalid nested field (e.g. `steps[0].name` missing).
  - [x] Test Case 5: `create_test_case` with hallucinated extra fields (should fail if Extra.forbid, or warn).
  - [x] Verify that response body contains "❌ Error", "Suggestions", and specific field names.

## Dev Notes

- **Pydantic V2**: Use `e.errors()` which returns a list of dictionaries. The `loc` tuple contains the field path.
- **FastMCP**: FastMCP might catch validation errors before our global handler if they occur at the parameter parsing level. We need to ensure we can intercept them. If FastMCP returns its own 400, we might need to wrap the tools or add a middleware.
- **Middleware vs Exception Handler**: Starlette's `exception_handler` is preferred. Ensure Pydantic `ValidationError` is registered.

### Project Structure Notes

- Keep the logic in `src/utils/error.py`.
- New tests in `tests/integration/`.

### References

- [Source: src/utils/error.py](file:///Users/anmaro/Code/personal/github.com/lucius-mcp/src/utils/error.py)
- [Pydantic V2 Errors](https://docs.pydantic.dev/latest/errors/errors/)

## Dev Agent Record

### Agent Model Used

Antigravity (simulated)

### Completion Notes List

- Implemented comprehensive error handling middleware in `src/utils/error.py`
- Added schema hint generation in `src/utils/schema_hint.py`
- Added integration tests covering validation scenarios

### File List

- src/utils/error.py
- src/utils/schema_hint.py
- tests/integration/test_error_handling.py
