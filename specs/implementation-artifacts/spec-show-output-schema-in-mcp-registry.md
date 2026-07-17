---
title: 'Show output schemas in MCP registry'
type: 'bugfix'
created: '2026-07-17'
status: 'done'
route: 'one-shot'
---

# Show output schemas in MCP registry

## Intent

**Problem:** The registry page already binds `tool.outputSchema`, but GitHub Pages only deployed on releases or manual runs. Consequently, generated schemas committed to `main` could remain absent from the live site.

**Approach:** Publish Pages automatically when either registry asset changes on `main`, and lock the page binding and deployment trigger with focused documentation tests.

## Suggested Review Order

**Schema publication**

- Registers concrete serialization schemas with every FastMCP tool.
  [`main.py:35`](../../src/main.py#L35)

- Builds object-root contracts from fields declared beside each tool.
  [`output_schemas.py:266`](../../src/tools/output_schemas.py#L266)

- Confirms the generated manifest contains concrete output properties.
  [`mcp_manifest.json:209`](../../docs/mcp_manifest.json#L209)

**Registry delivery**

- Renders the selected tool's input and output schemas from the manifest.
  [`mcp-registry.html:831`](../../docs/mcp-registry.html#L831)

- Deploys updated registry assets from `main` without unrelated-site rebuilds.
  [`pages-manual.yml:3`](../../.github/workflows/pages-manual.yml#L3)

**Regression coverage**

- Verifies the manifest schema contracts, UI binding, and publication trigger.
  [`test_mcp_manifest.py:153`](../../tests/docs/test_mcp_manifest.py#L153)

- Verifies the registry page and Pages workflow remain connected.
  [`test_mcp_registry.py:131`](../../tests/docs/test_mcp_registry.py#L131)
