---
title: 'Fix Python 3.10 attachment-download test compatibility'
type: 'bugfix'
created: '2026-08-28'
status: 'done'
route: 'one-shot'
---

# Fix Python 3.10 attachment-download test compatibility

## Intent

**Problem:** PR #357 imports `datetime.UTC`, which is unavailable in Python 3.10 and stops unit-test collection in the supported CI matrix.

**Approach:** Use the portable `datetime.timezone.utc` constant in the UTC-aware fixture while preserving its serialized output and test behavior.

## Suggested Review Order

- Use the standard UTC timezone API supported by Python 3.10 through 3.14.
  [`test_attachment_download_tools.py:5`](../../tests/unit/test_attachment_download_tools.py#L5)

- Keep the fixture's aware timestamp and expected `Z` serialization unchanged.
  [`test_attachment_download_tools.py:22`](../../tests/unit/test_attachment_download_tools.py#L22)
