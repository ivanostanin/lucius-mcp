---
title: "Simplify project-version fallback"
type: "refactor"
created: "2026-08-11"
status: "done"
route: "one-shot"
---

# Simplify project-version fallback

## Intent

**Problem:** The Python-version TOML fallback contained a type-only protocol
and private wrapper that obscured its small runtime purpose.

**Approach:** Select `tomllib` or `tomli` explicitly by Python version, retain
the public parser and its invalid-project error behavior, and inline the sole
private-wrapper call site.

## Suggested Review Order

- The import branch documents the supported Python policy without runtime type scaffolding.
  [`version.py:3`](../../src/version.py#L3)

- The public reader retains explicit validation for missing, blank, and malformed project tables.
  [`version.py:13`](../../src/version.py#L13)

- Focused tests cover source fallback and malformed TOML project data.
  [`test_remaining_coverage.py:292`](../../tests/unit/test_remaining_coverage.py#L292)
