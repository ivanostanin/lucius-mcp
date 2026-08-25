---
title: 'Move test-result tool test to E2E'
type: 'chore'
created: '2026-08-25'
status: 'done'
route: 'one-shot'
---

# Move test-result tool test to E2E

## Intent

**Problem:** The exact test-result tool test depends on Allure TestOps credentials but was included in the unit-test suite.

**Approach:** Relocate the test, unchanged, to the existing TestOps result-detail E2E module and remove the now-empty unit-test module.

## Suggested Review Order

- Confirms the token-dependent tool test now runs with the result-detail E2E coverage.
  [`test_test_result_detail.py:24`](../../tests/e2e/test_test_result_detail.py#L24)

- The standalone unit module is intentionally removed after relocation.
