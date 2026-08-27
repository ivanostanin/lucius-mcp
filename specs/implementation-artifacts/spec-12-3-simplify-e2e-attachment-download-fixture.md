---
title: 'Simplify E2E Attachment Download Fixture'
type: 'refactor'
created: '2026-08-27'
status: 'done'
route: 'one-shot'
---

# Simplify E2E Attachment Download Fixture

## Intent

**Problem:** The attachment E2E test embedded a separate Python program solely to prepare and retrieve a download, obscuring the test’s real behavior.

**Approach:** Use a small fixture to select Lucius’s real stdio delivery mode, then call the preparation tool and fetch its one-time URL directly in the test.

## Suggested Review Order

- Select the supported delivery mode without replacing runtime objects.
  [`test_test_result_detail.py:23`](../../tests/e2e/test_test_result_detail.py#L23)

- Verify preparation, one-time retrieval, and refresh in readable test code.
  [`test_test_result_detail.py:218`](../../tests/e2e/test_test_result_detail.py#L218)
