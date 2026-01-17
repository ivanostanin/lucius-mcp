    # Test Design: Epic 1 - Foundation & Test Case Management

**Date:** 2025-12-30
**Author:** Ivan Ostanin
**Status:** Approved

---

## Executive Summary

**Scope:** Epic-Level test design for Epic 1 (Foundation & Test Case Management). Focus on Core Architecture, Authentication, Logging, Test Case CRUD, and Idempotent Update (Story 1.4).

**Risk Summary:**

- Total risks identified: 8
- High-priority risks (≥6): 3
- Critical categories: SEC (Security), REL (Reliability), DATA (Data Integrity)

**Coverage Summary:**

- P0 scenarios: 7 (14 hours)
- P1 scenarios: 14 (14 hours)
- P2/P3 scenarios: 10 (4.5 hours)
- **Total effort**: 32.5 hours (~4 days)

---

## Risk Assessment

### High-Priority Risks (Score ≥6)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner | Timeline |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ---------- | ----- | -------- |
| R-001 | SEC | API Token Leakage in Logs | 2 (Possible) | 3 (Critical) | 6 | Use `pydantic.SecretStr` for strict masking in all loggers. | Dev (Story 1.1) | 2025-12-27 |
| R-002 | REL | Agent Error Loops on Unhandled Exceptions | 3 (Likely) | 2 (Degraded) | 6 | Implement Global Exception Handler to return descriptive "Agent Hints" instead of 500s/Stack Traces. | Dev (Story 1.1) | 2025-12-27 |
| R-006 | DATA | Partial update overwrites or clears unspecified fields (steps, tags, attachments) | 2 (Possible) | 3 (Critical) | 6 | Filter None fields, compare current vs patch, and verify preservation in unit + E2E tests. | Dev (Story 1.4) | 2026-01-16 |

### Medium-Priority Risks (Score 3-4)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ---------- | ----- |
| R-003 | TECH | Schema Drift (Pydantic vs OpenAPI) | 2 (Possible) | 2 (Degraded) | 4 | Use `datamodel-code-generator` to auto-gen models from Spec. Enforce `mypy --strict`. | Dev (Story 1.2) |
| R-007 | TECH | Idempotency check misses no-op changes due to normalization differences (tags order, empty values) | 2 (Possible) | 2 (Degraded) | 4 | Normalize comparison inputs; unit tests for no-op, empty values, and tag order. | Dev (Story 1.4) |
| R-008 | DATA | Scenario update drops steps/attachments/links when replacing execution flow | 2 (Possible) | 2 (Degraded) | 4 | Preserve existing scenario elements and validate with unit + E2E scenario tests. | Dev (Story 1.4) |

### Low-Priority Risks (Score 1-2)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ---------- | ----- |
| R-004 | PERF | Server Startup Time > 2s | 1 (Unlikely) | 2 (Degraded) | 2 | Monitor startup time in CI. Use `uv` for fast resolution. | Monitor |
| R-005 | OPS | Local Environment Config Issues | 1 (Unlikely) | 1 (Minor) | 1 | Provide `.env.example` and validation on startup. | Monitor |

### Risk Category Legend

- **TECH**: Technical/Architecture (flaws, integration, scalability)
- **SEC**: Security (access controls, auth, data exposure)
- **PERF**: Performance (SLA violations, degradation, resource limits)
- **DATA**: Data Integrity (loss, corruption, inconsistency)
- **BUS**: Business Impact (UX harm, logic errors, revenue)
- **OPS**: Operations (deployment, config, monitoring)

---

## Test Coverage Plan

### P0 (Critical) - Run on every commit

**Criteria**: Blocks core journey + High risk (≥6) + No workaround

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ----------- | ---------- | --------- | ---------- | ----- | ----- |
| App Startup | Integration | R-004 | 1 | Dev | Verify `main.py` entrypoint loads FastMCP |
| Auth (Env) | Unit | R-001 | 2 | Dev | Verify `ALLURE_API_TOKEN` loading and masking |
| Error Handling | Unit | R-002 | 1 | Dev | Verify `AllureAPIError` converts to Agent Hint string |
| Update Partial Fields + Idempotency | Unit | R-006, R-007 | 2 | Dev | Verify unspecified fields preserved and no-op skips update |
| Update Tool Confirmation | Integration | R-007 | 1 | Dev | Verify tool returns "Updated" vs "No changes needed" |

**Total P0**: 7 tests, 14 hours

### P1 (High) - Run on PR to main

**Criteria**: Important features + Medium risk (3-4) + Common workflows

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ----------- | ---------- | --------- | ---------- | ----- | ----- |
| Logging Structure | Unit | - | 2 | Dev | Verify JSON format and Correlation ID |
| Schema Validation| Unit | R-003 | 4 | Dev | Verify Pydantic validation for missing fields |
| Scenario Preservation (Steps/Attachments) | Unit | R-008 | 2 | Dev | Verify updating one preserves the other |
| Tags + Custom Fields Merge | Unit | R-006 | 2 | Dev | Verify tags replace, custom fields merge |
| Update Core Fields (Sandbox) | E2E | R-006 | 1 | QA | Update name/description/precondition/expected_result |
| Update Scenario Elements (Sandbox) | E2E | R-008 | 2 | QA | Steps update + attachments/links update |
| Combined Update + Idempotent Repeat | E2E | R-007 | 1 | QA | Full update then repeated no-op |

**Total P1**: 14 tests, 14 hours

### P2 (Medium) - Run nightly/weekly

**Criteria**: Secondary features + Low risk (1-2) + Edge cases

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ----------- | ---------- | --------- | ---------- | ----- | ----- |
| Config Loading | Unit | R-005 | 3 | Dev | Verify `.env` file parsing edge cases |
| Health Check | Integration| - | 2 | Dev | Basic liveness probe |
| Nested Step Hierarchy | Unit | R-008 | 1 | Dev | Verify nested steps serialize correctly |
| Scenario Recreate Rollback | Unit | R-008 | 1 | Dev | Verify rollback restores scenario on failure |
| Edge-Case Updates (Sandbox) | E2E | R-007 | 1 | QA | Empty tags, empty description, no-op |

**Total P2**: 8 tests, 4 hours

### P3 (Low) - Run on-demand

**Criteria**: Nice-to-have + Exploratory + Performance benchmarks

| Requirement | Test Level | Test Count | Owner | Notes |
| ----------- | ---------- | ---------- | ----- | ----- |
| Linting Check | Static | 1 | CI | `ruff check` |
| Type Check | Static | 1 | CI | `mypy --strict` |

**Total P3**: 2 tests (Automated checks), 0.5 hours

---

## Execution Order

### Smoke Tests (<5 min)

**Purpose**: Fast feedback, catch build-breaking issues

- [ ] Unit Test: Logger Masking (30s)
- [ ] Integration: Server Startup (45s)
- [ ] Unit Test: Update Idempotency No-op (30s)

**Total**: 3 scenarios

### P0 Tests (<10 min)

**Purpose**: Critical path validation

- [ ] Unit Test: Error Handler (Agent Hints)
- [ ] Unit Test: Auth Config Loading
- [ ] Unit Test: Update Partial Fields (No Overwrite)
- [ ] Integration: Update Tool Confirmation

**Total**: 7 scenarios

### P1 Tests (<30 min)

**Purpose**: Important feature coverage

- [ ] Unit Test: Schema Validation (Happy/Unhappy paths)
- [ ] Unit Test: Structured Logging Format
- [ ] Unit Test: Scenario Preservation (Steps/Attachments)
- [ ] E2E: Update Core Fields
- [ ] E2E: Update Steps/Attachments/Links

**Total**: 14 scenarios

### P2/P3 Tests (<60 min)

**Purpose**: Full regression coverage

- [ ] Full Suite Run (`pytest`)
- [ ] Static Analysis (`ruff`, `mypy`)
- [ ] E2E: Edge-Case Updates
- [ ] Unit: Scenario Recreate Rollback

**Total**: All scenarios

---

## Resource Estimates

### Test Development Effort

| Priority | Count | Hours/Test | Total Hours | Notes |
| -------- | ----- | ---------- | ----------- | ----- |
| P0 | 7 | 2.0 | 14 | Core architecture + idempotent update |
| P1 | 14 | 1.0 | 14 | Update scenario coverage + unit tests |
| P2 | 8 | 0.5 | 4 | Edge cases + rollback |
| P3 | 2 | 0.25 | 0.5 | CI checks |
| **Total** | **31** | **-** | **32.5** | **~4 days** |

### Prerequisites

**Tooling:**

- `pytest` for test execution
- `allure-pytest` for reporting
- `respx` for API mocking (for Client tests)

**Environment:**

- Local Python 3.14 via `uv`
- `.env` file with dummy credentials

---

## Quality Gate Criteria

### Pass/Fail Thresholds

- **P0 pass rate**: 100% (no exceptions)
- **P1 pass rate**: ≥95% (waivers required for failures)
- **High-risk mitigations**: 100% complete or approved waivers

### Coverage Targets

- **Critical paths (Auth/Error)**: 100%
- **Utils (Logger/Config)**: ≥90%
- **Overall**: ≥85% (NFR7)

### Non-Negotiable Requirements

- [ ] All P0 tests pass
- [ ] No high-risk (≥6) items unmitigated
- [ ] Security tests (Masking) pass 100%
- [ ] Idempotent update tests (no-op + partial update) pass 100%

---

## Mitigation Plans

### R-001: API Token Leakage in Logs (Score: 6)

**Mitigation Strategy:** Implement `SecretStr` type usage in Pydantic config models and ensure custom JSON formatter explicitly filters known secret keys.
**Owner:** Dev (Story 1.1)
**Timeline:** 2025-12-27
**Status:** Complete
**Verification:** Run `test_logger.py` assertion that tokens are replaced with `******`.

### R-002: Agent Error Loops on Unhandled Exceptions (Score: 6)

**Mitigation Strategy:** Implement starlette exception handler that captures all `Exception` types, formats them into a simplified "Agent Hint" string, and returns 400/500 code with the hint in body.
**Owner:** Dev (Story 1.1)
**Timeline:** 2025-12-27
**Status:** Complete
**Verification:** Integration test triggering a forced exception receives formatted hint.

### R-006: Partial Update Overwrites Unspecified Fields (Score: 6)

**Mitigation Strategy:** Filter None fields, compare current vs patch, and preserve scenario elements (steps/attachments/links).
**Owner:** Dev (Story 1.4)
**Timeline:** 2026-01-16
**Status:** Planned
**Verification:** Unit tests for no-op + preservation; E2E update retains existing scenario elements.

---

## Assumptions and Dependencies

### Assumptions

1. `uv` is correctly installed on CI and Dev environments.
2. `python 3.14` is available.
3. Test cases can be created in sandbox projects for update flows.

### Dependencies

1. Allure TestOps OpenAPI Spec (for Model Check) - Required by Story 1.2
2. Starlette library Stability
3. Story 1.3 create_test_case capability (required for E2E update setup)
4. Sandbox project with update permissions and stable workflow/status IDs

---

## Approval

**Test Design Approved By:**

- [ ] Product Manager: [Name] Date: [Date]
- [ ] Tech Lead: [Name] Date: [Date]
- [ ] QA Lead: [Name] Date: [Date]

**Comments:**
Story 1.1 Implementation verified the P0 risks (Security/Reliability).

---

## Appendix

### Related Documents

- PRD: specs/prd.md
- Epic: specs/project-planning-artifacts/epics.md
- Architecture: specs/architecture.md
- Story: specs/implementation-artifacts/1-1-project-initialization-and-core-architecture.md
- Story: specs/implementation-artifacts/1-4-idempotent-update-and-maintenance.md

---

**Generated by**: BMad TEA Agent - Test Architect Module
**Workflow**: `_bmad/bmm/testarch/test-design`
**Version**: 4.0 (BMad v6)
