# Test Design: Story 1.5 - Soft Delete & Archive

**Date:** 2026-01-16
**Author:** Ivan Ostanin
**Status:** Draft

---

## Executive Summary

**Scope:** Targeted test design for Story 1.5 (Soft Delete & Archive)

**Risk Summary:**

- Total risks identified: 3
- High-priority risks (≥6): 1
- Critical categories: DATA

**Coverage Summary:**

- P0 scenarios: 1 (2 hours)
- P1 scenarios: 1 (1 hours)
- P2/P3 scenarios: 0 (0 hours)
- **Total effort**: 3 hours (~0.5 days)

---

## Risk Assessment

### High-Priority Risks (Score ≥6)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner | Timeline |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ---------- | ----- | -------- |
| R-001 | DATA | Implementation performs hard delete instead of soft delete/archive, causing permanent data loss | 2 | 3 | 6 | Verify API endpoint validation; implement E2E verification of archived status | QA | 2026-01-16 |

### Low-Priority Risks (Score 1-2)

| Risk ID | Category | Description | Probability | Impact | Score | Action |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ------- |
| R-002 | BUS | User confusion regarding missing (archived) test cases | 2 | 1 | 2 | Ensure tool returns clear "Archived" message and audit log | Monitor |
| R-003 | SEC | Unauthorized user archives critical test cases | 1 | 2 | 2 | Monitor (RBAC out of scope for story) | Monitor |

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
| ------------- | ---------- | --------- | ---------- | ----- | ------- |
| Soft Delete Test Case | E2E | R-001 | 1 | QA | Validate `delete_test_case` sets status to 'Archived' (not 404) |

**Total P0**: 1 tests, 2.0 hours

### P1 (High) - Run on PR to main

**Criteria**: Important features + Medium risk (3-4) + Common workflows

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ------------- | ---------- | --------- | ---------- | ----- | ------- |
| Idempotency of Delete | Unit | - | 1 | DEV | Verify calling delete twice returns success/cached status |
| Delete Non-Existent | Unit | - | 1 | DEV | Verify proper error handling for 404 |
| Tool Confirmation | Unit | - | 1 | DEV | Verify tool requires `confirm=True` |

**Total P1**: 3 tests, 1.0 hours

### P2 (Medium) - Run nightly/weekly

**Criteria**: Secondary features + Low risk (1-2) + Edge cases

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ------------- | ---------- | --------- | ---------- | ----- | ------- |
| - | - | - | 0 | - | - |

**Total P2**: 0 tests, 0 hours

### P3 (Low) - Run on-demand

**Criteria**: Nice-to-have + Exploratory + Performance benchmarks

| Requirement | Test Level | Test Count | Owner | Notes |
| ------------- | ---------- | ---------- | ----- | ------- |
| - | - | 0 | - | - |

**Total P3**: 0 tests, 0 hours

---

## Execution Order

### Smoke Tests (<5 min)

**Purpose**: Fast feedback, catch build-breaking issues

- [x] `test_delete_test_case_success` (Unit)
- [x] `test_delete_test_case_already_deleted` (Unit)
- [x] `test_delete_test_case_failure` (Unit)

**Total**: 3 scenarios

### P0 Tests (<10 min)

**Purpose**: Critical path validation

- [x] `test_delete_test_case_e2e` (E2E)

**Total**: 1 scenarios

---

## Resource Estimates

### Test Development Effort

| Priority | Count | Hours/Test | Total Hours | Notes |
| --------- | ----------------- | ---------- | ----------------- | ----------------------- |
| P0 | 1 | 2.0 | 2.0 | Setup/Teardown logic |
| P1 | 3 | 0.33 | 1.0 | Unit logic |
| **Total** | **4** | **-** | **3.0** | **~0.5 days** |

### Prerequisites

**Test Data:**

- Test Case Factory (creates temporary test case)

**Tooling:**

- `AllureClient` with `delete_test_case` support

**Environment:**

- Sandbox Project (ID: 1) for E2E tests

---

## Quality Gate Criteria

### Pass/Fail Thresholds

- **P0 pass rate**: 100% (no exceptions)
- **P1 pass rate**: ≥95% (waivers required for failures)
- **High-risk mitigations**: 100% complete or approved waivers

### Non-Negotiable Requirements

- [x] All P0 tests pass
- [x] R-001 (Data Loss) mitigated via E2E verification

---

## Mitigation Plans

### R-001: Implementation performs hard delete instead of soft delete (Score: 6)

**Mitigation Strategy:** Implement E2E test `test_delete_test_case_e2e` that deletes a test case and asserts the result status is explicitly "Archived" or verify Allure behavior documentation.
**Owner:** QA
**Timeline:** 2026-01-16
**Status:** Complete (Verified in Story 1.5 execution)
**Verification:** Run `pytest tests/e2e/test_delete_test_case.py`

---

## Assumptions and Dependencies

### Assumptions

1. Allure TestOps API `delete` endpoint performs a soft delete (archive) by default or via configuration.
2. The user has permission to delete test cases in the target project.

### Dependencies

1. Story 1.3 (Create Test Case) - Required to create data for deletion tests.

---

## Approval

**Test Design Approved By:**

- [ ] Product Manager: Ivan Ostanin Date: 2026-01-16
- [ ] Tech Lead: AntiGravity Date: 2026-01-16
- [ ] QA Lead: AntiGravity Date: 2026-01-16

---

**Generated by**: BMad TEA Agent - Test Architect Module
**Workflow**: `_bmad/bmm/testarch/test-design`
**Version**: 4.0 (BMad v6)
