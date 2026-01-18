# Test Design: Epic 2 - Shared Step Reusability

**Date:** 2026-01-18
**Author:** BMad Agent
**Status:** Draft

---

## Executive Summary

**Scope:** Test design for **Epic 2**, specifically **Story 2.2: Update & Delete Shared Steps** and **Story 2.3: Link Shared Step to Test Case**.

**Risk Summary:**

- Total risks identified: 6
- High-priority risks (≥6): 2
- Critical categories: DATA, BUS

**Coverage Summary:**

- P0 scenarios: 4 (8.0 hours)
- P1 scenarios: 4 (4.0 hours)
- P2/P3 scenarios: 3 (1.5 hours)
- **Total effort:** 13.5 hours (~2 days)

---

## Risk Assessment

### High-Priority Risks (Score ≥6)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner | Timeline |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ---------- | ----- | -------- |
| R-2.3-1 | DATA | Linking non-existent Shared Step ID breaks test execution or corrupts test case | 2 (Possible) | 3 (Critical) | 6 | Strict validation: Verify Shared Step exists via API/Service before attempting to link | DEV | 2026-01-18 |
| R-2.2-1 | BUS | Update Propagation: Modifying a shared step invalidates logic in linked test cases without warning | 2 (Possible) | 3 (Critical) | 6 | Tool warning: explicitly list affected test count; E2E verification of propagation | DEV | 2026-01-18 |

### Medium-Priority Risks (Score 3-4)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ---------- | ----- |
| R-2.3-2 | TECH | Cyclic dependency (Shared Step A links to B which links to A) | 2 (Possible) | 2 (Degraded) | 4 | Handle Allure API recursion errors gracefully | DEV |
| R-2.3-3 | TECH | Invalid position index during insertion (IndexError) | 2 (Possible) | 2 (Degraded) | 4 | Service-layer bounds checking | DEV |
| R-2.2-2 | DATA | Delete In-Use: Deleting a shared step breaks linked test cases | 2 (Possible) | 2 (Degraded) | 4 | `delete_shared_step` blocks if linked cases exist unless `force=True` | DEV |

### Low-Priority Risks (Score 1-2)

| Risk ID | Category | Description | Probability | Impact | Score | Action |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ------ |
| R-2.2-3 | TECH | Idempotency: Repeated updates duplicate data | 2 (Possible) | 1 (Minor) | 2 | Service-layer idempotency check |

### Risk Category Legend

- **TECH**: Technical/Architecture
- **DATA**: Data Integrity
- **BUS**: Business Impact

---

## Test Coverage Plan

### P0 (Critical) - Run on every commit

**Criteria**: Blocks core user journey + High risk (≥6)

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ----------- | ---------- | --------- | ---------- | ----- | ----- |
| Link Shared Step to Test Case | E2E | R-2.3-1 | 1 | QA | Verify shared step reference appears in Test Case details |
| Link Shared Step (Happy Path) | API | - | 1 | DEV | Verify API 200 OK |
| Update Shared Step & Propagate | E2E | R-2.2-1 | 1 | QA | Verify update changes logic in linked test case |
| Delete Shared Step (Safe) | E2E | - | 1 | QA | Verify deletion of unlinked step |

**Total P0**: 4 tests, 8.0 hours

### P1 (High) - Run on PR to main

**Criteria**: Important features + Medium risk (3-4)

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ----------- | ---------- | --------- | ---------- | ----- | ----- |
| Unlink Shared Step | API | - | 1 | DEV | Verify step can be removed |
| Insert Shared Step at Position | Unit | R-2.3-3 | 1 | DEV | Verify list insertion logic |
| Delete In-Use (Blocked) | E2E | R-2.2-2 | 1 | QA | Verify deletion is blocked with warning |
| Delete In-Use (Forced) | E2E | R-2.2-2 | 1 | QA | Verify force delete works but breaks link |

**Total P1**: 4 tests, 4.0 hours

### P2 (Medium) - Run nightly/weekly

**Criteria**: Secondary features + Edge cases

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ----------- | ---------- | --------- | ---------- | ----- | ----- |
| Link with Invalid/Missing ID | Unit | R-2.3-1 | 1 | DEV | Verify error hint |
| Update Idempotency | Unit | R-2.2-3 | 1 | DEV | Verify repeated calls |
| Update Invalid ID | Unit | - | 1 | DEV | Verify error handling |

**Total P2**: 3 tests, 1.5 hours

---

## Execution Order

### Smoke Tests (<5 min)

- [ ] Unit: Insert Shared Step at Position
- [ ] Unit: Update Idempotency
- [ ] Unit: Link with Invalid/Missing ID

### P0 Tests (<10 min)

- [ ] API: Link Shared Step (Happy Path)
- [ ] E2E: Link Shared Step to Test Case
- [ ] E2E: Update Shared Step & Propagate

### P1 Tests (<30 min)

- [ ] API: Unlink Shared Step
- [ ] E2E: Delete In-Use (Blocked/Forced)

---

## Resource Estimates

### Test Development Effort

| Priority | Count | Hours/Test | Total Hours | Notes |
| -------- | ----- | ---------- | ----------- | ----- |
| P0 | 4 | 2.0 | 8.0 | E2E setup |
| P1 | 4 | 1.0 | 4.0 | Logic/Integration |
| P2 | 3 | 0.5 | 1.5 | Unit tests |
| **Total** | **11** | **-** | **13.5** | **~2 days** |

### Prerequisites

**Test Data:**
- `SharedStepFactory`: Create source step
- `TestCaseFactory`: Create target case
- `LinkedCaseFactory`: Create case WITH shared step (for delete testing)

**Tooling:**
- `update_shared_step` / `delete_shared_step` MCP tools
- `link_shared_step` / `unlink_shared_step` MCP tools

---

## Quality Gate Criteria

### Pass/Fail Thresholds
- **P0 pass rate**: 100%
- **P1 pass rate**: ≥95%
- **High-risk mitigations**: 100% complete

### Coverage Targets
- **Critical paths**: 100% (Link, Update, Delete)
- **Safety checks**: 100% (Delete blocking, ID validation)

---

## Approval

**Test Design Approved By:**
- [ ] Agent Self-Approval Date: 2026-01-18
