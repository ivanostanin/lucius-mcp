---
title: 'Sync MCP manifest during release'
type: 'chore'
created: '2026-07-17'
status: 'done'
route: 'one-shot'
baseline_commit: 'bf78a09cdc519f6842588192b740b33409e49060'
---

# Sync MCP manifest during release

## Intent

**Problem:** Release version bumps can leave the published MCP documentation manifest stale because the existing hook only runs for staged tool changes.

**Approach:** Make manifest regeneration an explicit, locked release step, refresh the current generated artifact, and verify its version against package metadata.

## Suggested Review Order

**Release workflow**

- Regenerate and verify published MCP metadata after release dependency synchronization.
  [`prepare-release.md:34`](../../scripts/prepare-release.md#L34)

**Regression protection**

- Compare manifest server version directly with the project release version.
  [`test_mcp_manifest.py:153`](../../tests/docs/test_mcp_manifest.py#L153)

**Generated release metadata**

- Confirm the checked-in manifest reflects the current dependency and server versions.
  [`mcp_manifest.json:1`](../../docs/mcp_manifest.json#L1)
