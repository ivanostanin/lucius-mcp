---
title: 'Fix attachment disconnect test with Starlette 1.10'
type: 'bugfix'
created: '2026-11-05'
status: 'done'
route: 'one-shot'
---

# Fix attachment disconnect test with Starlette 1.10

## Intent

**Problem:** Starlette now handles an immediate ASGI disconnect before the test's simulated send failure, so the test expects an exception that never occurs.

**Approach:** Exercise both an older ASGI disconnect and a 2.4 send failure, verifying that each releases the cached attachment and its claim.

## Suggested Review Order

1. [Interrupted response test](../../tests/unit/test_attachment_download_service.py) — check both interruption paths and cleanup assertions.
