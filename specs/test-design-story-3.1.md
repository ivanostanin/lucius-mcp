# Test Design: Story 3.1 - List Test Cases by Project

**Date:** 2026-01-20
**Author:** Ivan Ostanin
**Status:** Draft
**Epic:** 3 (Search & Contextual Access)

---

## Executive Summary

**Scope:** Epic-Level (Targeted Story 3.1 validation)
**Goal:** Ensure agents can reliably list, paginate, and filter test cases with LLM-friendly output.

**Risk Summary:**

- Total risks identified: 4
- High-priority risks (≥6): 2
- Critical categories: BUS, PERF

**Coverage Summary:**

- P0 scenarios: 2 (4.0 hours)
- P1 scenarios: 3 (3.0 hours)
- P2/P3 scenarios: 4 (1.75 hours)
- **Total effort:** 8.75 hours (~1.1 days)

---

## Risk Assessment

### High-Priority Risks (Score ≥6)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner | Timeline |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ---------- | ----- | -------- |
| R-3.1-1 | BUS | **Agent misinterpretation**: LLM-friendly output missing status/tags or pagination hints leads to incorrect decisions about test coverage. | 2 (Possible) | 3 (Critical) | 6 | Enforce formatting tests on `_format_test_case_list` and E2E output assertions. | Dev/QA | Story 3.1 |
| R-3.1-2 | PERF | **Large project listing**: Large result sets cause timeouts or unusable output if pagination isn’t enforced. | 2 (Possible) | 3 (Critical) | 6 | Validate pagination defaults and size limits; include E2E pagination scenario. | Dev | Story 3.1 |

### Medium-Priority Risks (Score 3-4)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ---------- | ----- |
| R-3.1-3 | DATA | **Filter mismatch**: AQL-compatible filters (name/tag/status) not applied correctly, returning misleading lists. | 2 (Possible) | 2 (Degraded) | 4 | Unit coverage for filter forwarding; E2E filter sanity checks. | Dev |

### Low-Priority Risks (Score 1-2)

| Risk ID | Category | Description | Probability | Impact | Score | Action |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ------ |
| R-3.1-4 | OPS | **Validation hint regression**: Invalid Project ID doesn’t return a clear error hint. | 1 (Unlikely) | 2 (Degraded) | 2 | Unit validation tests; monitor. | Monitor |

---

## Test Coverage Plan

### P0 (Critical) - Run on every commit

**Criteria**: Core discovery journey + High risk (≥6)

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ----------- | ---------- | --------- | ---------- | ----- | ----- |
| AC #1, #4, #6 | E2E | R-3.1-1 | 1 | QA | Verify list returns items and LLM-friendly formatting in sandbox. |
| AC #2 | E2E | R-3.1-2 | 1 | QA | Verify pagination works across multiple pages with hints. |

**Total P0**: 2 tests, 4.0 hours

### P1 (High) - Run on PR to main

**Criteria**: Important features + Medium risk

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ----------- | ---------- | --------- | ---------- | ----- | ----- |
| AC #3 | E2E | R-3.1-3 | 1 | QA | Validate filters (name/tag/status) are AQL-compatible. |
| AC #5 | Unit | R-3.1-4 | 1 | Dev | Validate error hint on invalid Project ID. |
| AC #4 | Unit | R-3.1-1 | 1 | Dev | `_format_test_case_list` includes status/tags and pagination hint. |

**Total P1**: 3 tests, 3.0 hours

### P2 (Medium) - Run nightly/weekly

**Criteria**: Secondary coverage + edge cases

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ----------- | ---------- | --------- | ---------- | ----- | ----- |
| AC #2 | Unit | R-3.1-2 | 1 | Dev | Pagination edge cases (empty results, single page, multiple pages). |
| AC #3 | Unit | R-3.1-3 | 1 | Dev | Filter combinations forwarded correctly. |
| AC #1 | Unit | - | 1 | Dev | Mapping from API response to list summary. |

### P3 (Low) - Run on-demand

**Criteria**: Nice-to-have, low-risk

| Requirement | Test Level | Test Count | Owner | Notes |
| ----------- | ---------- | ---------- | ----- | ----- |
| AC #4 | Unit | 1 | Dev | Output remains stable when tags/status are missing. |

**Total P2/P3**: 4 tests, 1.75 hours

---

## Execution Order

### Smoke Tests (<5 min)

- [ ] `test_list_test_cases_paginates_and_formats` (E2E)
- [ ] `test_list_test_cases_filters_are_aql_compatible` (E2E)

### P0 Tests (<10 min)

- [ ] `test_list_test_cases_paginates_and_formats` (E2E)
- [ ] `test_list_test_cases_filters_are_aql_compatible` (E2E)

### P1 Tests (<30 min)

- [ ] `test_list_test_cases_handles_invalid_project` (Unit)
- [ ] `test_format_test_case_list_includes_status_tags` (Unit)
- [ ] `test_list_test_cases_filters_are_aql_compatible` (E2E)

### P2/P3 Tests (<60 min)

- [ ] `test_list_test_cases_returns_paginated_results` (Unit)
- [ ] `test_list_test_cases_passes_filters` (Unit)
- [ ] `test_list_test_cases_validates_pagination` (Unit)
- [ ] `test_format_test_case_list_handles_missing_fields` (Unit)

---

## Resource Estimates

### Test Development Effort

| Priority  | Count             | Hours/Test | Total Hours       | Notes                     |
| --------- | ----------------- | ---------- | ----------------- | ------------------------- |
| P0        | 2                 | 2.0        | 4.0               | Sandbox E2E coverage      |
| P1        | 3                 | 1.0        | 3.0               | Output + validation checks|
| P2        | 3                 | 0.5        | 1.5               | Service-level edge cases  |
| P3        | 1                 | 0.25       | 0.25              | Format stability          |
| **Total** | **9**             | **-**      | **8.75**          | **~1.1 days**             |

### Prerequisites

**Test Data:**

- Sandbox project with known test cases for pagination
- Tags/status coverage in sandbox data set

**Tooling:**

- `pytest` with existing E2E harness
- `respx` for unit mocks where needed

**Environment:**

- `ALLURE_ENDPOINT` and `ALLURE_API_TOKEN` configured for sandbox

---

## Quality Gate Criteria

### Pass/Fail Thresholds

- **P0 pass rate**: 100%
- **P1 pass rate**: ≥95%
- **High-risk mitigations**: 100% complete or approved waivers

### Coverage Targets

- **Critical paths**: ≥80%
- **Search/Discovery workflows**: ≥80%
- **Error handling**: ≥70%

### Non-Negotiable Requirements

- [ ] E2E tests validate LLM-friendly output (no raw JSON)
- [ ] Pagination hint shown when additional pages exist
- [ ] Invalid project ID returns a clear error hint

---

## Mitigation Plans

### R-3.1-1: Agent misinterpretation (Score: 6)

**Mitigation Strategy:** Add focused unit tests for `_format_test_case_list` plus E2E assertions on formatting fields.
**Owner:** QA/Dev
**Timeline:** Story 3.1
**Status:** Planned
**Verification:** Unit test for formatting + E2E assertion on output.

### R-3.1-2: Large project listing (Score: 6)

**Mitigation Strategy:** Enforce pagination limits and ensure hinting for next page.
**Owner:** Dev
**Timeline:** Story 3.1
**Status:** Planned
**Verification:** Unit tests for pagination validation + E2E pagination test.

---

## Assumptions and Dependencies

### Assumptions

1. Sandbox project contains enough cases to exercise pagination.
2. Test case records include at least one tag/status for format validation.
3. LLM-friendly output expectations align with existing formatting helpers.

### Dependencies

1. Story 1.6 E2E harness and sandbox credentials configured.
2. SearchService and AllureClient implementations available (Story 3.1 tasks).

### Risks to Plan

- **Risk**: Sandbox data lacks tags/status coverage.
  - **Impact**: Format validation may be weak.
  - **Contingency**: Seed at least one test case with tags/status or adjust E2E assertions.

---

## Follow-on Workflows (Manual)

- Run `*atdd` to generate failing P0 tests (separate workflow; not auto-run).
- Run `*automate` after implementation stabilizes for broader coverage.

---

## Approval

**Test Design Approved By:**

- [ ] Product Manager: {name} Date: {date}
- [ ] Tech Lead: {name} Date: {date}
- [ ] QA Lead: {name} Date: {date}

**Comments:**

---

## Appendix

### Knowledge Base References

- `risk-governance.md` - Risk classification framework
- `probability-impact.md` - Risk scoring methodology
- `test-levels-framework.md` - Test level selection
- `test-priorities-matrix.md` - P0-P3 prioritization

### Related Documents

- PRD: specs/prd.md
- Epic: specs/project-planning-artifacts/epics.md (Story 3.1)
- Architecture: specs/architecture.md
- Implementation: specs/implementation-artifacts/3-1-list-test-cases-by-project.md

---

**Generated by**: BMad TEA Agent - Test Architect Module
**Workflow**: `_bmad/bmm/testarch/test-design`
