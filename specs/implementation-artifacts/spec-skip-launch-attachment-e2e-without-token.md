---
title: 'Skip launch-attachment E2E without a token'
type: 'bugfix'
created: '2026-09-22'
status: 'done'
route: 'one-shot'
---

# Skip launch-attachment E2E without a token

## Intent

**Problem:** The native launch-attachment E2E constructs its client directly and raises `KeyError` when `ALLURE_API_TOKEN` is absent, instead of following the suite's credential skip policy.

**Approach:** Request the shared `api_token` fixture so missing credentials skip the test before client construction, while leaving the authenticated test path unchanged.

## Suggested Review Order

- The shared fixture gates execution on configured API credentials.
  [`test_launch_attachments.py:18`](../../tests/e2e/test_launch_attachments.py#L18)
