#!/usr/bin/env bash
# Build CLI binary for macOS ARM64 (Apple Silicon)

set -e

# Resolve absolute paths without GNU-only `readlink -f` (portable to macOS)
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -P)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${PROJECT_ROOT}"

echo "Project root: ${PROJECT_ROOT}"
echo "Entry point: ${PROJECT_ROOT}/src/cli/cli_entry.py"

# Verify entry point exists
if [ ! -f "src/cli/cli_entry.py" ]; then
    echo "Error: src/cli/cli_entry.py not found in ${PROJECT_ROOT}"
    echo "Current directory: $(pwd)"
    exit 1
fi

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
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Build lucius CLI for macOS ARM64 (Apple Silicon)"
            echo ""
            echo "Options:"
            echo "  --no-onefile      Disable onefile mode (faster iteration, produces bundle)"
            echo "  --no-clean        Skip cleaning previous build artifacts"
            echo "  --jobs N          Use N parallel jobs for compilation"
            echo "  --help, -h        Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Standard build (slow, single file)"
            echo "  $0 --no-onefile       # Fast build (bundle, not single file)"
            echo "  $0 --no-onefile --jobs 8  # Faster parallel build"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "Building lucius CLI for macOS ARM64 (Apple Silicon)..."


# Check OS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: This script must be run on macOS"
    exit 1
fi

# Check CPU architecture
if [[ $(uname -m) != "arm64" ]]; then
    echo "Warning: Not building on ARM64 (Apple Silicon) machine"
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
# Excluding HTTP components - CLI uses stdio transport only
# Including static tool schemas for fast startup
# Destination path: data/tool_schemas.json (relative to module location)
NUITKA_FLAGS="--standalone --assume-yes-for-downloads --macos-create-app-bundle --output-dir=dist/cli --output-filename=lucius-macos-arm64
  --include-package=rich._unicode_data
  --include-data-files=src/cli/data/tool_schemas.json=data/tool_schemas.json"

if [ "$ONEFILE" = true ]; then
    NUITKA_FLAGS="$NUITKA_FLAGS --onefile"
fi

if [ -n "$JOBS" ]; then
    NUITKA_FLAGS="$NUITKA_FLAGS --jobs=$JOBS"
fi

# Use uv to run nuitka
uv run nuitka $NUITKA_FLAGS src/cli/cli_entry.py

echo "✓ Built: dist/cli/lucius-macos-arm64"
echo "✓ macOS ARM64 build complete"
