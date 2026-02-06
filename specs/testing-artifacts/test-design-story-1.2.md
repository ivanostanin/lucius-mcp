# Test Design: Story 1.2 - Generated Client & Data Models

**Epic**: 1 - Foundation & Test Case Management  
**Date:** 2026-01-01
**Author:** Ivan Ostanin  
**Status:** Approved

---

## Story Context

**Story 1.2: Generated Client & Data Models**

As a Developer, I want to generate Pydantic models from the Allure TestOps OpenAPI spec, so that I can interact with the API with 100% schema fidelity and strict type safety.

**Acceptance Criteria:**
- Pydantic v2 models successfully created in `src/client/models.py`
- Thin `httpx` based `AllureClient` created in `src/client/client.py`
- `mypy --strict` passes for generated models and client

**Related NFRs:**
- NFR4: Schema fidelity 100% compliant with Allure Open API 3.1
- NFR7: Unit Test coverage > 85%
- NFR8: 100% mypy strict type checking compliance  
- NFR11: End-to-End Tests implemented

---

## Executive Summary

**Scope:** Targeted test design for Story 1.2

**Risk Summary:**
- Total risks identified: 8
- High-priority risks (≥6): 3
- Critical categories: TECH, DATA, SEC

**Coverage Summary:**
- P0 scenarios: 8 (16 hours)
- P1 scenarios: 12 (12 hours)
- P2/P3 scenarios: 10 (3.5 hours)
- **Total effort**: 31.5 hours (~4 days)

---

## Risk Assessment

### High-Priority Risks (Score ≥6)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner | Timeline |
| ------- | -------- | ------------- | ----------- | ------ | ----- | ------------ | ------- | -------- |
| R-001 | TECH | Code generation from OpenAPI spec produces models that don't match actual Allure API responses | 2 | 3 | 6 | E2E tests against sandbox TestOps instance validating all generated model fields | DEV | Sprint 1 |
| R-002 | DATA | Generated models allow invalid data to pass (schema fidelity < 100%) | 2 | 3 | 6 | Unit tests with edge cases, strict Pydantic validation, mypy strict mode | QA | Sprint 1 |
| R-003 | TECH | `datamodel-code-generator` CLI fails or produces non-compilable Python code | 2 | 3 | 6 | Version lock generator tool, unit test generated code compiles, CI/CD validation | DEV | Sprint 1 |

### Medium-Priority Risks (Score 3-4)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner |
| ------- | -------- | ------------- | ----------- | ------ | ----- | ------------ | ------- |
| R-004 | TECH | Generated models don't support all Python 3.14 typing features (e.g., optional fields, unions) | 1 | 3 | 3 | Test generated code with Python 3.14 interpreter, validate typing edge cases | DEV |
| R-005 | OPS | OpenAPI spec changes upstream, breaking regeneration pipeline | 2 | 2 | 4 | Version control spec file, diff-based change detection, CI alert on spec drift | DEV |
| R-006 | SEC | httpx client exposes API tokens in logs or error traces | 1 | 3 | 3 | Unit tests validate SecretStr masking, E2E log inspection | QA |

### Low-Priority Risks (Score 1-2)

| Risk ID | Category | Description | Probability | Impact | Score | Action |
| ------- | -------- | ------------- | ----------- | ------ | ----- | ------- |
| R-007 | PERF | Client initialization overhead > 50ms (NFR1 violation) | 1 | 2 | 2 | Monitor |
| R-008 | TECH | mypy strict mode produces false positives on generated code | 1 | 2 | 2 | Monitor |

---

## Test Coverage Plan

### P0 (Critical) - Run on every commit

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ------------- | ---------- | --------- | ---------- | ----- | ------- |
| Generated models compile and import successfully | Unit | R-003 | 1 | DEV | Smoke test: `import src.client.models` |
| All required fields from OpenAPI spec are present in generated models | Unit | R-001 | 3 | QA | Test TestCase, SharedStep, Step models |
| Pydantic validation rejects invalid data per schema rules | Unit | R-002 | 2 | QA | Test missing required fields, invalid types |
| `mypy --strict` passes on `src/client/models.py` | Integration | R-003, R-004 | 1 | DEV | CI/CD gate |
| `mypy --strict` passes on `src/client/client.py` | Integration | R-003 | 1 | DEV | CI/CD gate |

**Total P0**: 8 tests, 16 hours

### P1 (High) - Run on PR to main

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ------------- | ---------- | --------- | ---------- | ----- | ------- |
| AllureClient initializes with env vars (ALLURE_ENDPOINT, ALLURE_TOKEN) | Integration | - | 1 | DEV | Default auth mode |
| AllureClient supports runtime token override via constructor | Integration | - | 1 | DEV | Dynamic context switching |
| Generated models handle optional fields correctly (None vs missing) | Unit | R-004 | 3 | QA | Test optional description, precondition |
| Client wrapper masks SecretStr tokens in all error paths | Unit | R-006 | 2 | QA | Inspect exception messages |
| E2E: Create TestCase via client, validate response matches model | E2E | R-001 | 1 | QA | Sandbox integration |
| E2E: Retrieve TestCase via client, validate all fields deserialize | E2E | R-001 | 1 | QA | Sandbox integration |
| Generated models support complex nested structures (Steps with Checks) | Unit | R-002 | 2 | QA | Test nested validation |
| Client error handling converts 4xx/5xx to AllureAPIError | Integration | - | 1 | DEV | Exception hierarchy |

**Total P1**: 12 tests, 12 hours

### P2 (Medium) - Run nightly/weekly

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ------------- | ---------- | --------- | ---------- | ----- | ------- |
| Model generation handles edge case: empty arrays, null values | Unit | R-002 | 3 | QA | Boundary testing |
| Client wrapper timeout configuration | Unit | - | 1 | DEV | httpx timeout settings |
| Generated models support all Pydantic v2 features (validators, computed fields) | Unit | R-004 | 2 | QA | Pydantic compliance |
| Spec drift detection: Compare generated models to known spec version | Integration | R-005 | 1 | DEV | CI check |
| Client initialization overhead < 50ms | Performance | R-007 | 1 | QA | NFR1 validation |

**Total P2**: 8 tests, 4 hours

### P3 (Low) - Run on-demand

| Requirement | Test Level | Test Count | Owner | Notes |
| ------------- | ---------- | ---------- | ----- | ------- |
| Exhaustive field validation: All OpenAPI schema constraints honored | Unit | 1 | QA | Exploratory |
| Code generation idempotency: Regenerating from same spec produces identical code | Integration | 1 | DEV | Diff-based check |

**Total P3**: 2 tests, 0.5 hours

---

## Execution Order

### Smoke Tests (<5 min)

- [ ] Import generated models module (30s)
- [ ] Instantiate AllureClient with valid config (20s)
- [ ] Run `mypy --strict` on client/ directory (2min)

### P0 Tests (<10 min)

- [ ] Generated models compile (Unit)
- [ ] Required fields present for TestCase model (Unit)
- [ ] Required fields present for SharedStep model (Unit)
- [ ] Required fields present for Step model (Unit)
- [ ] Pydantic rejects missing required field (Unit)
- [ ] Pydantic rejects invalid type (Unit)
- [ ] mypy strict passes on models.py (Integration)
- [ ] mypy strict passes on client.py (Integration)

### P1 Tests (<30 min)

- [ ] Client init with env vars (Integration)
- [ ] Client init with runtime override (Integration)
- [ ] Optional field: None vs missing (Unit, 3 variants)
- [ ] SecretStr masking in errors (Unit, 2 variants)
- [ ] E2E: Create TestCase (E2E)
- [ ] E2E: Retrieve TestCase (E2E)
- [ ] Nested structure validation (Unit, 2 variants)
- [ ] 4xx/5xx error conversion (Integration)

### P2/P3 Tests (<60 min)

- [ ] Edge cases: empty/null (Unit, 3 variants)
- [ ] Timeout configuration (Unit)
- [ ] Pydantic v2 features (Unit, 2 variants)
- [ ] Spec drift detection (Integration)
- [ ] Init overhead < 50ms (Performance)
- [ ] Exhaustive field validation (Unit)
- [ ] Code generation idempotency (Integration)

---

## Resource Estimates

| Priority | Count | Hours/Test | Total Hours | Notes |
| --------- | ----- | ---------- | ----------- | ----------------------- |
| P0 | 8 | 2.0 | 16 | Complex validation, schema compliance |
| P1 | 12 | 1.0 | 12 | Integration and E2E setup |
| P2 | 8 | 0.5 | 4 | Standard unit tests |
| P3 | 2 | 0.25 | 0.5 | Exploratory |
| **Total** | **30** | **-** | **32.5** | **~4 days** |

### Prerequisites

**Test Data:**
- `allure_openapi_spec.json` - Known-good OpenAPI 3.1 spec for Allure TestOps (fixture)
- `invalid_test_case_samples.json` - Edge cases for validation testing (factory)
- Sandbox Allure TestOps instance - For E2E integration tests

**Tooling:**
- `datamodel-code-generator` - CLI for model generation (locked version)
- `pytest` + `pytest-asyncio` - Test framework with async support
- `mypy` - Type checking validation
- `pytest-benchmark` - Performance testing (P2)

**Environment:**
- Python 3.14 interpreter
- Sandbox Allure TestOps API endpoint with valid credentials (env vars)
- CI/CD pipeline with mypy strict mode enforcement

---

## Quality Gate Criteria

### Pass/Fail Thresholds
- **P0 pass rate**: 100% (no exceptions)
- **P1 pass rate**: ≥95% (waivers required for failures)
- **P2/P3 pass rate**: ≥90% (informational)
- **High-risk mitigations**: 100% complete (R-001, R-002, R-003)

### Coverage Targets
- **Generated models**: 100% (all fields from OpenAPI spec)
- **Client wrapper**: ≥85% (NFR7)
- **Type safety**: 100% (mypy --strict must pass)
- **E2E validation**: 100% (schema compliance against sandbox)

### Non-Negotiable Requirements
- [ ] All P0 tests pass
- [ ] No high-risk (≥6) items unmitigated
- [ ] `mypy --strict` passes on all client code (NFR8)
- [ ] E2E tests validate schema fidelity (NFR4)

---

## Mitigation Plans

### R-001: Code Generation Mismatch (Score: 6)

**Mitigation Strategy:**  
Implement comprehensive E2E tests that create and retrieve Test Cases via the generated client against a sandbox Allure TestOps instance. Validate that all fields in the response deserialize correctly into the generated Pydantic models. Add CI/CD pipeline step that runs E2E tests on every build.

**Owner:** QA  
**Timeline:** Sprint 1  
**Status:** Planned  
**Verification:** E2E test suite passes in sandbox environment, no deserialization errors

### R-002: Schema Fidelity < 100% (Score: 6)

**Mitigation Strategy:**  
Create comprehensive unit test suite with edge cases (missing required fields, invalid types, boundary values). Enable Pydantic strict mode validation. Use `mypy --strict` to catch type mismatches at development time. Add pre-commit hook to run mypy.

**Owner:** QA  
**Timeline:** Sprint 1  
**Status:** Planned  
**Verification:** Unit tests cover >85% of edge cases, mypy strict mode enforced in CI

### R-003: Generator Tool Failure (Score: 6)

**Mitigation Strategy:**  
Lock `datamodel-code-generator` to a specific version in `pyproject.toml`. Add CI/CD step that validates generated code compiles (`python -m compileall src/client/models.py`). Create smoke test that imports the generated module. Document manual regeneration process in README.

**Owner:** DEV  
**Timeline:** Sprint 1  
**Status:** Planned  
**Verification:** CI pipeline catches non-compilable code, version lock prevents unexpected breakage

---

## Assumptions and Dependencies

### Assumptions
1. Allure TestOps OpenAPI 3.1 spec is available and up-to-date at project setup time
2. `datamodel-code-generator` supports Pydantic v2 and Python 3.14 syntax
3. Sandbox Allure TestOps instance is available for E2E testing with persistent credentials

### Dependencies
1. Allure TestOps OpenAPI spec file - Required before Sprint 1
2. Sandbox TestOps instance credentials (API token, endpoint) - Required before E2E test development
3. Python 3.14 environment setup - Required for all development

### Risks to Plan
- **Risk**: Allure TestOps OpenAPI spec is incomplete or incorrect
  - **Impact**: Generated models don't match actual API, E2E tests fail
  - **Contingency**: Manual schema inspection, iterative spec correction, fallback to manual model authoring for critical entities

- **Risk**: `datamodel-code-generator` doesn't support advanced Pydantic v2 features (computed fields, validators)
  - **Impact**: Need manual model customization, breaking automated regeneration
  - **Contingency**: Post-generation manual edits with clear documentation, explore alternative generators (e.g., openapi-python-client)

---

## Related Documents

- PRD: specs/prd.md
- Epic: specs/project-planning-artifacts/epics.md#L136-L148
- Architecture: specs/architecture.md
- Epic Test Design: specs/test-design-epic-1.md

---

**Generated by**: BMad TEA Agent - Test Architect Module  
**Workflow**: `_bmad/bmm/testarch/test-design`  
**Version**: 4.0 (BMad v6)
