#!/usr/bin/env bash
set -euo pipefail

# Regenerate the manifest when tool contracts or FastMCP registration change.
if ! git diff --cached --name-only --diff-filter=ACMRD -- src/tools src/main.py | grep -q .; then
    exit 0
fi

echo "Detected staged tool-contract or registration changes; regenerating docs/mcp_manifest.json"

if command -v fastmcp >/dev/null 2>&1; then
    fastmcp inspect src/main.py --format mcp -o docs/mcp_manifest.json
else
    uv run fastmcp inspect src/main.py --format mcp -o docs/mcp_manifest.json
fi

git add docs/mcp_manifest.json
