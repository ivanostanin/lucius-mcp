# Test Design: Story 1.3 - Comprehensive Test Case Creation Tool

**Date:** 2026-01-01
**Author:** TEA Agent
**Status:** Approved

---

## Executive Summary

**Scope:** Test design specifically for Story 1.3 (Comprehensive Test Case Creation Tool). This includes validating the MCP tool interface, Pydantic schema validation, attachment handling (Base64/URL), and integration with the Allure TestOps API using the "Thin Tool / Fat Service" pattern.

**Risk Summary:**

- Total risks identified: 4
- High-priority risks (≥6): 2
- Critical categories: TECH (Validation/Mapping), SEC (Data Leakage)

**Coverage Summary:**

- P0 scenarios: 5 (Primary creation flows + Validation)
- P1 scenarios: 4 (Attachments + Metadata mapping)
- P2 scenarios: 3 (Edge cases + Error handling)
- **Total effort**: ~12 hours

---

## Risk Assessment

### High-Priority Risks (Score ≥6)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ---------- |
| R-1.3-01 | TECH | **Validation Bypass**: Malformed data (e.g., invalid custom field types) passed to Allure without proper Pydantic rejection. | 2 | 3 | 6 | Ensure strict `TestCaseCreate` model used in `TestCaseService`. Unit tests for all field types. |
| R-1.3-02 | SEC | **Token Exposure**: Project ID or API tokens used in tool execution leaked into logs during failed creation attempts. | 2 | 3 | 6 | Verification of logging redact rules and `SecretStr` usage in `AllureClient`. |

### Medium-Priority Risks (Score 3-4)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ---------- |
| R-1.3-03 | DATA | **Attachment Failure**: Large Base64 payloads or invalid URLs causing service timeout or corruption. | 2 | 2 | 4 | Integration tests with standard/large attachments; timeout configuration. |
| R-1.3-04 | TECH | **Pattern Violation**: Business logic leaking into the MCP tool from the Service layer, making testing/maintenance difficult. | 2 | 2 | 4 | Static analysis/Code Review to ensure "Thin Tool" pattern. |
| R-1.3-05 | ENV | **Sandbox Drift**: E2E tests fail due to unexpected sandbox configuration changes (e.g., deleted custom fields). | 3 | 2 | 6 | Automated project setup/teardown scripts; usage of fixed "Sandbox" project ID. |

---

## Test Coverage Plan

### P0 (Critical) - Run on every commit

| Requirement | Test Level | Risk Link | Test Count | Notes |
| ----------- | ---------- | --------- | ---------- | ----- |
| Create Case (Basic) | E2E | R-1.3-05 | 1 | Verify name-only creation in live sandbox. |
| Schema Validation | Unit | R-1.3-01 | 3 | Verify rejection of missing name, invalid types in steps. |
| Step Mapping | Unit | - | 1 | Verify `TestStep` objects correctly serialized. |
| Auth Flow | E2E | R-1.3-02 | 1 | Verify tool executes successfully with runtime token override in sandbox. |

**Total P0**: 5 tests

### P1 (High) - Run on PR to main

| Requirement | Test Level | Risk Link | Test Count | Notes |
| ----------- | ---------- | --------- | ---------- | ----- |
| Attachment (Base64)| Integration| R-1.3-03 | 1 | Mocked upload check for image/png. |
| Attachment (URL) | Integration| R-1.3-03 | 1 | Mocked upload check for external links. |
| Custom Fields | Unit | R-1.3-01 | 1 | Verify dict -> custom field list mapping. |
| Tags | Unit | - | 1 | Verify tag list preservation. |
| **Comprehensive E2E**| **E2E** | **R-1.3-05** | **1** | Create test case with *all* fields (Steps, Tags, CF, Attachments) and verify in Allure UI/API. |

**Total P1**: 4 tests

### P2 (Medium) - Run nightly

| Requirement | Test Level | Risk Link | Test Count | Notes |
| ----------- | ---------- | --------- | ---------- | ----- |
| Error Message Hint | Integration| R-1.3-01 | 2 | Verify "Agent Hint" is returned on 400 Bad Request. |
| Log Masking Check | Unit | R-1.3-02 | 1 | Verify secret keys redacted in creation logs. |

**Total P2**: 3 tests

---

## Resource Estimates

### Test Development Effort

| Priority | Count | Hours/Test | Total Hours | Notes |
| --------- | ----- | ---------- | ----------- | ----------------------- |
| P0 | 5 | 1.5 | 7.5 | Primary path + E2E setup |
| P1 | 4 | 1.0 | 4.0 | Mock-heavy integration |
| P2 | 3 | 0.5 | 1.5 | Error/Log assertions |
| **Total** | **12**| **-** | **13.0** | **~1.5 days** |

---

## Quality Gate Criteria

- **P0 tests**: 100% Pass.
- **P1 tests**: 100% Pass.
- **Coverage**: All fields in `TestCaseCreate` model must be covered by at least one test.
- **Architectural Check**: `TestCaseService` must contain 100% of creation logic; tool must be `< 10 lines`.

---

## Mitigation Plans

### R-1.3-05: Sandbox Drift (Score: 6)
- **Status**: Planned.
- **Action**: Create a `conftest.py` fixture that ensures a "Test Sandbox" project exists with the expected custom fields before E2E execution.

---

## End-to-End Test Scenarios

### E2E-1: The "Full House" Test Case
**Objective:** Verify that a tool call with every optional field results in a correct Test Case in Allure TestOps.
- **Inputs:**
  - `name`: "E2E Comprehensive Test"
  - `description`: "Rich markdown description"
  - `steps`: 2 manual steps, 1 shared step reference
  - `tags`: ["e2e", "automated"]
  - `custom_fields`: {"Layer": "API", "Priority": "High"}
  - `attachments`: 1 Base64 image
- **Validation:**
  - Tool returns "Created Test Case ####"
  - Fetch Test Case details direct from Allure API via ID
  - Assert all fields match input exactly.

### E2E-2: Runtime Auth Overdrive
**Objective:** Verify that providing a different `host` and `token` at runtime works.
- **Action:** Call `create_test_case` with valid override args.
- **Validation:** Verify request hits the override host with correctly mapped Bearer token.

---

**Generated by**: BMad TEA Agent - Test Architect Module
**Workflow**: `_bmad/bmm/testarch/test-design`
**Story**: 1.3 - Comprehensive Test Case Creation Tool
