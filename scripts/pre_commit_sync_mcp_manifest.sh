#!/usr/bin/env bash
set -euo pipefail

# Regenerate MCP manifest only when staged changes include src/tools.
if ! git diff --cached --name-only --diff-filter=ACMRD -- src/tools | grep -q .; then
    exit 0
fi

echo "Detected staged changes in src/tools; regenerating docs/mcp_manifest.json"

if command -v fastmcp >/dev/null 2>&1; then
    fastmcp inspect src/main.py --format mcp -o docs/mcp_manifest.json
else
    uv run fastmcp inspect src/main.py --format mcp -o docs/mcp_manifest.json
fi

git add docs/mcp_manifest.json
