# Test Design: Epic 3 - Search & Contextual Access (Story 3.4)

**Date:** 2026-01-21
**Author:** Ivan Ostanin
**Status:** Draft

---

## Executive Summary

**Scope:** full test design for Epic 3, Story 3.4 (Runtime Authentication Override)

**Risk Summary:**

- Total risks identified: 6
- High-priority risks (≥6): 2
- Critical categories: SEC, DATA

**Coverage Summary:**

- P0 scenarios: 6 (12.0 hours)
- P1 scenarios: 8 (8.0 hours)
- P2/P3 scenarios: 7 (3.25 hours)
- **Total effort**: 23.25 hours (~2.9 days)

---

## Risk Assessment

### High-Priority Risks (Score ≥6)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner | Timeline |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ---------- | ----- | -------- |
| R-001 | SEC | Runtime API token override allows unauthorized access if token masking/logging is bypassed or token is leaked. | 2 | 3 | 6 | Enforce SecretStr masking + scrub logs; add unit tests for log masking; ensure error messages never echo token. | DEV | 2026-01-31 |
| R-002 | DATA | Cross-project operations due to incorrect project_id override usage could update/search wrong project. | 3 | 2 | 6 | Validate runtime project_id precedence and add regression tests for per-call isolation. | QA | 2026-01-31 |

### Medium-Priority Risks (Score 3-4)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ---------- | ----- |
| R-003 | TECH | AuthContext/override propagation inconsistent across services/tools. | 2 | 2 | 4 | Add unit tests per service to ensure context is passed and used. | DEV |
| R-004 | OPS | Missing or unclear error hints when no auth configured, causing agent confusion. | 2 | 2 | 4 | Standardize AuthenticationError messages, ensure surfaced by global handler. | DEV |

### Low-Priority Risks (Score 1-2)

| Risk ID | Category | Description | Probability | Impact | Score | Action |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ------ |
| R-005 | PERF | Added per-call auth context creation introduces minor latency. | 1 | 2 | 2 | Monitor |
| R-006 | BUS | Tool docs may omit override guidance for some tools. | 1 | 1 | 1 | Monitor |

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
| Runtime api_token override takes precedence for a tool call | Integration | R-001 | 2 | QA | AuthContext precedence + masking verification |
| Runtime project_id override applies per call and does not persist | Integration | R-002 | 2 | QA | Cross-call isolation |
| Missing runtime+env auth returns clear error hint | Unit | R-004 | 2 | DEV | AuthenticationError message content |

**Total P0**: 6 tests, 12.0 hours

### P1 (High) - Run on PR to main

**Criteria**: Important features + Medium risk (3-4) + Common workflows

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ----------- | ---------- | --------- | ---------- | ----- | ----- |
| All tools accept optional api_token/project_id overrides | Unit | R-003 | 3 | DEV | Signature + context pass-through |
| Env fallback when runtime overrides absent | Unit | R-004 | 2 | DEV | get_auth_context fallback |
| Token masking in logs for runtime token | Unit | R-001 | 3 | DEV | __repr__/logging scrub |

**Total P1**: 8 tests, 8.0 hours

### P2 (Medium) - Run nightly/weekly

**Criteria**: Secondary features + Low risk (1-2) + Edge cases

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ----------- | ---------- | --------- | ---------- | ----- | ----- |
| Runtime overrides honored across SearchService/CaseService | Integration | R-003 | 3 | QA | Service-level coverage |
| Error hint text includes remediation guidance | Unit | R-004 | 2 | DEV | Error copy |

**Total P2**: 5 tests, 2.5 hours

### P3 (Low) - Run on-demand

**Criteria**: Nice-to-have + Exploratory + Performance benchmarks

| Requirement | Test Level | Test Count | Owner | Notes |
| ----------- | ---------- | ---------- | ----- | ----- |
| Minor perf regression check for auth context creation | Unit | 2 | DEV | Simple timing assertion (best effort) |

**Total P3**: 2 tests, 0.5 hours

---

## Execution Order

### Smoke Tests (<5 min)

**Purpose**: Fast feedback, catch build-breaking issues

- [ ] get_auth_context returns runtime token when provided (Unit)
- [ ] get_auth_context falls back to env (Unit)
- [ ] AuthenticationError message present when missing auth (Unit)

**Total**: 3 scenarios

### P0 Tests (<10 min)

**Purpose**: Critical path validation

- [ ] Runtime api_token override precedence (Integration)
- [ ] Runtime project_id override per-call isolation (Integration)
- [ ] Missing auth error hint (Unit)

**Total**: 6 scenarios

### P1 Tests (<30 min)

**Purpose**: Important feature coverage

- [ ] Tool signatures include optional api_token/project_id (Unit)
- [ ] Token masking in logs / repr (Unit)
- [ ] Env fallback behavior (Unit)

**Total**: 8 scenarios

### P2/P3 Tests (<60 min)

**Purpose**: Full regression coverage

- [ ] Service-level override propagation (Integration)
- [ ] Error hint remediation guidance (Unit)
- [ ] Auth context perf smoke (Unit)

**Total**: 7 scenarios

---

## Resource Estimates

### Test Development Effort

| Priority | Count | Hours/Test | Total Hours | Notes |
| -------- | ----- | ---------- | ----------- | ----- |
| P0 | 6 | 2.0 | 12.0 | Auth override + isolation tests |
| P1 | 8 | 1.0 | 8.0 | Signature + masking + fallback |
| P2 | 5 | 0.5 | 2.5 | Service coverage + errors |
| P3 | 2 | 0.25 | 0.5 | Best-effort perf checks |
| **Total** | **21** | **-** | **23.0** | **~2.9 days** |

### Prerequisites

**Test Data:**

- AuthContext fixtures (env + runtime overrides)
- Sandbox project IDs for e2e (if available)

**Tooling:**

- pytest + existing test harness
- structlog masking verification

**Environment:**

- ALLURE_ENDPOINT + ALLURE_API_TOKEN for e2e
- Optional sandbox project ID for cross-project validation

---

## Quality Gate Criteria

### Pass/Fail Thresholds

- **P0 pass rate**: 100% (no exceptions)
- **P1 pass rate**: ≥95% (waivers required for failures)
- **P2/P3 pass rate**: ≥90% (informational)
- **High-risk mitigations**: 100% complete or approved waivers

### Coverage Targets

- **Critical paths**: ≥80%
- **Security scenarios**: 100%
- **Business logic**: ≥70%
- **Edge cases**: ≥50%

### Non-Negotiable Requirements

- [ ] All P0 tests pass
- [ ] No high-risk (≥6) items unmitigated
- [ ] Security tests (SEC category) pass 100%
- [ ] Performance targets met (PERF category)

---

## Mitigation Plans

### R-001: Token leakage via runtime override (Score: 6)

**Mitigation Strategy:** Enforce SecretStr masking, scrub logs, and add unit tests validating masked output.
**Owner:** DEV
**Timeline:** 2026-01-31
**Status:** Planned
**Verification:** Unit tests assert token not present in logs or string repr.

### R-002: Cross-project data access due to override misuse (Score: 6)

**Mitigation Strategy:** Validate project_id override precedence per tool call and add integration tests to verify isolation.
**Owner:** QA
**Timeline:** 2026-01-31
**Status:** Planned
**Verification:** Integration tests confirm per-call override and no persistence.

---

## Assumptions and Dependencies

### Assumptions

1. Runtime overrides are optional and should never persist beyond a single call.
2. Tools expose `api_token` and (where relevant) `project_id` parameters.
3. Global error handler surfaces AuthenticationError as user-facing hints.

### Dependencies

1. AuthContext + get_auth_context implemented in src/utils/auth.py
2. Services accept AuthContext and pass it into AllureClient

### Risks to Plan

- **Risk**: Missing sandbox credentials for E2E validation
  - **Impact**: E2E coverage reduced to unit/integration only
  - **Contingency**: Skip E2E tests when credentials absent and document

---

## Follow-on Workflows (Manual)

- Run `*atdd` to generate failing P0 tests (separate workflow; not auto-run).
- Run `*automate` for broader coverage once implementation exists.

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
- Epic: specs/project-planning-artifacts/epics.md#Epic-3-Search-Contextual-Access
- Architecture: specs/architecture.md
- Story: specs/implementation-artifacts/3-4-runtime-authentication-override.md

---

**Generated by**: BMad TEA Agent - Test Architect Module
**Workflow**: `_bmad/bmm/testarch/test-design`
**Version**: 4.0 (BMad v6)
