#!/usr/bin/env bash
# Build CLI binary for Linux x86_64

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${PROJECT_ROOT}"

echo "Building lucius CLI for Linux x86_64..."

# Ensure uv is available
if ! command -v uv &> /dev/null; then
    echo "Error: uv not found. Install from https://astral.sh/uv"
    exit 1
fi

# Clean previous builds
rm -rf dist/cli

# Generate tool schemas for fast startup (build-time static data)
echo "Generating tool schemas..."
uv --quiet run python scripts/build_tool_schema.py

# Verify schema file exists
if [ ! -f "src/cli/data/tool_schemas.json" ]; then
    echo "Error: tool_schemas.json not found after generation"
    exit 1
fi

# Use uv to run nuitka
# Note: This assumes building on a Linux x86_64 machine
# Excluding HTTP components - CLI uses stdio transport only
uv run nuitka \
    --standalone \
    --onefile \
    --assume-yes-for-downloads \
    --output-dir=dist/cli \
    --output-filename=lucius-linux-x86_64 \
    --include-data-files=src/cli/data/tool_schemas.json=data/tool_schemas.json \
    src/cli/cli_entry.py

echo "✓ Built: dist/cli/lucius-linux-x86_64"
echo "✓ Linux x86_64 build complete"
