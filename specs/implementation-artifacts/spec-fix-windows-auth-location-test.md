---
title: 'Fix Windows auth-location test'
type: 'bugfix'
created: '2026-09-01'
status: 'done'
route: 'one-shot'
---

# Fix Windows auth-location test

## Intent

**Problem:** The auth import-boundary test assumed POSIX path rendering, so it failed on Windows where `pathlib.Path` displays backslashes.

**Approach:** Reuse the mocked `Path` in the assertion so the expected CLI output follows the active platform while preserving native path rendering.

## Suggested Review Order

- Assert against the same platform-native path object supplied to the CLI.
  [`test_cli_auth.py:375`](../../tests/cli/test_cli_auth.py#L375)
