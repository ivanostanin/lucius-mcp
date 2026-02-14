# Story 7.1: Test Plan Management

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **AI Agent**,
I want to **create and manage Test Plans using manual selection or filters/AQL queries**,
so that **I can organize testing efforts around specific releases or milestones efficiently**.

## Acceptance Criteria

1.  **Create Test Plan (Manual Selection):**
    *   **Given** a Project ID and a list of Test Case IDs.
    *   **When** I call `create_test_plan(name, test_case_ids=[...])`.
    *   **Then** a new Test Plan is created in Allure TestOps containing exactly those test cases.
    *   **And** the tool returns `id`, `name`, and `test_case_count`.

2.  **Create Test Plan (AQL Filter):**
    *   **Given** a Project ID and an AQL query (e.g., `"tag:smoke AND layer:api"`).
    *   **When** I call `create_test_plan(name, aql_filter="...")`.
    *   **Then** the system automatically selects all test cases matching the query.
    *   **And** a new Test Plan is created with those cases.
    *   **And** the response indicates how many cases were added.

3.  **Edit Test Plan:**
    *   **Given** an existing Test Plan ID.
    *   **When** I call `update_test_plan(id, name=..., description=...)`.
    *   **Then** the metadata is updated.
    *   **And** checks for idempotency (no change if data is same).

4.  **Manage Test Plan Content (Add/Remove):**
    *   **Given** an existing Test Plan.
    *   **When** I call `add_test_cases_to_plan(id, test_case_ids=[...])` or `remove_test_cases_from_plan(id, test_case_ids=[...])`.
    *   **Then** the plan content is updated accordingly.
    *   **And** invalid Test Case IDs result in a partial success or specific error hints (per agent-proofing NFRs).

5.  **List Test Plans:**
    *   **Given** a Project ID.
    *   **When** I call `list_test_plans(project_id)`.
    *   **Then** it returns a list of plans with their IDs, names, status, and test case counts.
    *   **And** supports pagination or basic filtering if applicable.

6.  **Agent-Proofing & Validation:**
    *   Inputs are validated against strict Pydantic models.
    *   Missing required fields (e.g., `name`) return a descriptive error with a hint.
    *   Destructive operations (if any) require `confirm=True` (though creation isn't destructive, removal of cases might be considered so, but strictly `delete_test_plan` would be). AC4 `remove_test_cases` should probably have `confirm=True` if it's a bulk removal, but standard practice for list modification usually doesn't. Let's stick to standard safety: explicit `delete_test_plan` (if implemented) needs confirmation. For this story, `create` and `update` are safe.

## Tasks / Subtasks

- [ ] **1. Define Pydantic Models** (AC 1-6)
    - [ ] Create `TestPlanCreate`, `TestPlanUpdate`, `TestPlan` in `src/client/models/plans.py` (or facade equivalent).
    - [ ] Ensure `ConfigDict(strict=True)`.
    - [ ] Map AQL filter options if supported by upstream API schema.

- [ ] **2. Implement Test Plan Service** (AC 1-5)
    - [ ] Create `src/services/plan_service.py`.
    - [ ] Implement `create_plan` (handle both ID list and AQL).
    - [ ] Implement `update_plan`.
    - [ ] Implement `add_cases` / `remove_cases`.
    - [ ] Implement `list_plans`.
    - [ ] **Constraint:** Business logic ONLY in service.

- [ ] **3. Implement MCP Tools** (AC 1-5)
    - [ ] Create `src/tools/plans.py`.
    - [ ] Define `create_test_plan` tool (thin wrapper).
    - [ ] Define `update_test_plan` tool.
    - [ ] Define `manage_test_plan_content` tool (or separate add/remove).
    - [ ] Define `list_test_plans` tool.
    - [ ] **Constraint:** Detailed docstrings + `confirm=True` for removal if added.

- [ ] **4. Unit Tests**
    - [ ] Create `tests/unit/test_plan_service.py`.
    - [ ] Mock `AllureClient` responses.
    - [ ] Verify AQL query handling logic.
    - [ ] Verify error handling (Agent Hints).

- [ ] **5. Integration/E2E Tests**
    - [ ] Add scenarios to `tests/integration/test_tools.py` (or `test_plans.py`).
    - [ ] Verify against real/sandbox Allure instance (if available) or strict mocks.

## Dev Notes

- **Architecture Patterns:**
    - **Thin Tool / Fat Service:** `src/tools/plans.py` MUST simply call `src/services/plan_service.py`.
    - **Models:** Check `src/client/generated` first to see if `TestPlan` models exist. If so, re-export in `src/client/models/plans.py`.
    - **Async:** Use `await` for all service calls.

- **Source Tree Components:**
    - `src/client/models/` (New: `plans.py`)
    - `src/services/` (New: `plan_service.py`)
    - `src/tools/` (New: `plans.py`)
    - `src/main.py` (Register new tools)

- **Testing Standards:**
    - `pytest` for all tests.
    - `respx` for mocking `httpx` in unit tests.
    - Coverage > 85%.

### Project Structure Notes

- **New File:** `src/tools/plans.py` - Verify this aligns with `cases.py` and `launches.py` pattern.
- **New File:** `src/services/plan_service.py` - Verify alignment with `case_service.py`.

### References

- **PRD:** `specs/prd.md` Section "Functional Requirements" -> "Test Planning" (implied in future).
- **Architecture:** `specs/architecture.md` -> "Implementation Patterns".
- **Project Context:** `specs/project-context.md` -> "Forbidden Practices" (No synchronous HTTP).

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### Review Notes
- [AI Review] Found bug in `update_plan` where arguments were ignored.
- [AI Review] **CRITICIAL**: `description`, `tags`, and `product_area_id` are NOT supported by the current `TestPlan` DTOs in the generated client. Removed these fields from Service and Tools to avoid runtime errors.
- [AI Review] Added missing unit test for `update_plan` (name update only).
- [AI Review] Verified implementation against ACs (with noted exceptions).

### File List

- src/client/models/plans.py
- src/services/plan_service.py
- src/tools/plans.py
- tests/unit/test_plan_service.py
- tests/integration/test_plan_tools.py
