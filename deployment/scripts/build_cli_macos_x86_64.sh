#!/usr/bin/env bash
# Build CLI binary for macOS x86_64 (Intel)

set -e

# Resolve absolute paths to handle symlinks and relative invocation
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${PROJECT_ROOT}"

# Parse arguments
ONEFILE=true
CLEAN=true
JOBS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-onefile)
            ONEFILE=false
            echo "⚡  Fast build mode: --onefile disabled (faster, but produces bundle)"
            shift
            ;;
        --no-clean)
            CLEAN=false
            echo "📦  Skipping clean (reuse previous build artifacts)"
            shift
            ;;
        --jobs)
            JOBS="$2"
            echo "⚙️  Using $2 parallel jobs"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Building lucius CLI for macOS x86_64 (Intel)..."

# Check OS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: This script must be run on macOS"
    exit 1
fi

# Check CPU architecture
if [[ $(uname -m) != "x86_64" ]]; then
    echo "Warning: Not building on x86_64 (Intel) machine"
    echo "Current architecture: $(uname -m)"
fi

# Ensure uv is available
if ! command -v uv &> /dev/null; then
    echo "Error: uv not found. Install from https://astral.sh/uv"
    exit 1
fi

# Clean previous builds
if [ "$CLEAN" = true ]; then
    rm -rf dist/cli
fi

# Generate tool schemas for fast startup (build-time static data)
echo "Generating tool schemas..."
uv --quiet run python scripts/build_tool_schema.py

# Verify schema file exists
if [ ! -f "src/cli/data/tool_schemas.json" ]; then
    echo "Error: tool_schemas.json not found after generation"
    exit 1
fi

# Build Nuitka command
# Destination path: data/tool_schemas.json (relative to module location)
NUITKA_FLAGS="--standalone --assume-yes-for-downloads --macos-create-app-bundle --output-dir=dist/cli --output-filename=lucius-macos-x86_64 --include-data-files=src/cli/data/tool_schemas.json=data/tool_schemas.json"

if [ "$ONEFILE" = true ]; then
    NUITKA_FLAGS="$NUITKA_FLAGS --onefile"
fi

if [ -n "$JOBS" ]; then
    NUITKA_FLAGS="$NUITKA_FLAGS --jobs=$JOBS"
fi

# Use uv to run nuitka
uv run nuitka $NUITKA_FLAGS src/cli/cli_entry.py

echo "✓ Built: dist/cli/lucius-macos-x86_64"
echo "✓ macOS x86_64 build complete"
