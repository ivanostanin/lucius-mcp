---
title: 'Restore token-free test-result unit test'
type: 'bugfix'
created: '2026-08-25'
status: 'done'
route: 'one-shot'
---

# Restore token-free test-result unit test

## Intent

**Problem:** The unit test mocked an obsolete client factory, allowing `_launch_client_context` to require Allure credentials.

**Approach:** Restore the test to unit coverage, mock the active context manager, and clear inherited Allure settings in the test.

## Suggested Review Order

- The active client-context boundary is mocked, so authentication settings are never resolved.
  [`test_test_result_tools.py:19`](../../tests/unit/test_test_result_tools.py#L19)

- Exact context, service, and result-ID forwarding remain covered without a live TestOps dependency.
  [`test_test_result_tools.py:52`](../../tests/unit/test_test_result_tools.py#L52)
