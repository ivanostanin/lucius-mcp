#!/bin/bash
# Master build script for lucius CLI - builds all 6 platform binaries

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${PROJECT_ROOT}"

echo "==========================================================================="
echo "Building lucius CLI for all platforms"
echo "==========================================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v uv &> /dev/null; then
    echo -e "${RED}Error: uv not found${NC}"
    echo "Install from https://astral.sh/uv"
    exit 1
fi

if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}Error: Python not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites met${NC}"

normalize_platform() {
    case "$1" in
        Linux) echo "linux" ;;
        Darwin) echo "macos" ;;
        MINGW*|MSYS*|CYGWIN*) echo "windows" ;;
        *) echo "$1" | tr '[:upper:]' '[:lower:]' ;;
    esac
}

normalize_arch() {
    case "$1" in
        aarch64|arm64) echo "arm64" ;;
        x86_64|amd64) echo "x86_64" ;;
        *) echo "$1" ;;
    esac
}

# Clean previous builds
echo ""
echo "Cleaning previous builds..."
rm -rf dist/cli
mkdir -p dist/cli
echo -e "${GREEN}✓ Cleaned dist/cli${NC}"

# Generate tool schemas
echo ""
echo "Generating tool schemas..."
uv run python scripts/build_tool_schema.py
echo -e "${GREEN}✓ Tool schemas generated${NC}"

# Generate shell completions
echo ""
echo "Generating shell completions..."
uv run python deployment/scripts/generate_completions.py
echo -e "${GREEN}✓ Shell completions generated${NC}"

# Count successful builds
successful_builds=0
failed_builds=0

# Define build matrix (platform, arch, script_name)
declare -a BUILD_MATRIX=(
    "linux arm64 build_cli_linux_arm64.sh"
    "linux x86_64 build_cli_linux_x86_64.sh"
    "macos arm64 build_cli_macos_arm64.sh"
    "macos x86_64 build_cli_macos_x86_64.sh"
)

# Run Unix builds
echo ""
current_platform="$(normalize_platform "$(uname -s)")"
current_arch="$(normalize_arch "$(uname -m)")"

if [[ "$current_platform" == "windows" ]]; then
    echo ""
    echo "---------------------------------------------------------------------------"
    echo "Building for windows-${current_arch}..."
    echo "---------------------------------------------------------------------------"

    win_arch_env="$(echo "${PROCESSOR_ARCHITECTURE:-}" | tr '[:lower:]' '[:upper:]')"
    win_arch_wow="$(echo "${PROCESSOR_ARCHITEW6432:-}" | tr '[:lower:]' '[:upper:]')"
    if [[ "$win_arch_env" == "ARM64" || "$win_arch_wow" == "ARM64" ]]; then
        windows_arch="arm64"
        windows_script="build_cli_windows_arm64.bat"
    else
        windows_arch="x86_64"
        windows_script="build_cli_windows_x86_64.bat"
    fi

    if ! command -v cmd &> /dev/null; then
        echo -e "${RED}Error: Windows cmd executable not found in PATH${NC}"
        exit 1
    fi

    if cmd /c "deployment\\scripts\\${windows_script}"; then
        echo -e "${GREEN}✓ windows-${windows_arch} build successful${NC}"
        ((successful_builds++))
    else
        echo -e "${RED}✗ windows-${windows_arch} build failed${NC}"
        ((failed_builds++))
    fi
else
    echo "Building Unix binaries..."
    echo "==========================================================================="

    for entry in "${BUILD_MATRIX[@]}"; do
        read -r platform arch script <<< "$entry"

        echo ""
        echo "---------------------------------------------------------------------------"
        echo "Building for ${platform}-${arch}..."
        echo "---------------------------------------------------------------------------"

        # Skip cross-platform builds (only build for current platform in dev mode)
        # CI/CD systems should run this script on each target platform
        if [[ "${CI:-}" != "true" ]]; then
            # In development mode, only build for current architecture
            if [[ "$current_platform" != "$platform" ]]; then
                echo -e "${YELLOW}⚠ Skipping $platform-$arch (not current platform in dev mode)${NC}"
                echo "  Run in CI/CD or on specific platform to build"
                continue
            fi

            if [[ "$current_arch" == "arm64" && "$arch" != "arm64" ]]; then
                echo -e "${YELLOW}⚠ Skipping $platform-$arch (ARM64 can't build x86_64 natively)${NC}"
                echo "  Use cross-compilation or CI/CD"
                continue
            fi

            if [[ "$current_arch" == "x86_64" && "$arch" != "x86_64" ]]; then
                echo -e "${YELLOW}⚠ Skipping $platform-$arch (x86_64 can't build ARM64 natively)${NC}"
                echo "  Use cross-compilation or CI/CD"
                continue
            fi
        fi

        # Run build script
        if bash deployment/scripts/"$script"; then
            echo -e "${GREEN}✓ ${platform}-${arch} build successful${NC}"
            ((successful_builds++))
        else
            echo -e "${RED}✗ ${platform}-${arch} build failed${NC}"
            ((failed_builds++))
        fi
    done

    # Note: Windows builds need to be run on Windows with .bat scripts
    echo ""
    echo "---------------------------------------------------------------------------"
    echo "Windows builds:"
    echo "---------------------------------------------------------------------------"
    echo -e "${YELLOW}Note: Windows builds must be run on Windows using:${NC}"
    echo "  - build_cli_windows_x86_64.bat"
    echo "  - build_cli_windows_arm64.bat"
    echo ""
    echo "These .bat files are in deployment/scripts/"
fi

# Summary
echo ""
echo "==========================================================================="
echo "Build Summary"
echo "==========================================================================="
echo ""
echo "Successful builds: $successful_builds"
echo "Failed builds:     $failed_builds"
echo ""

if [[ $successful_builds -gt 0 ]]; then
    echo -e "${GREEN}Built binaries:${NC}"
    for binary in dist/cli/lucius-*; do
        if [[ -f "$binary" ]]; then
            size=$(du -h "$binary" | cut -f1)
            echo "  ✓ $(basename "$binary") ($size)"
        fi
    done
    echo ""
fi

if [[ $successful_builds -gt 0 ]]; then
    echo -e "${GREEN}✓ Build process complete${NC}"
    echo ""
    echo "Binaries are in: dist/cli/"
    echo ""
    echo "To verify no HTTP components are bundled:"
    echo "  python deployment/scripts/verify_no_http.py"
    echo ""
    echo "To test binaries:"
    echo "  pytest tests/packaging/test_cli_binaries.py -v"
    echo ""

    if [[ $failed_builds -gt 0 ]]; then
        echo -e "${YELLOW}⚠ Some builds failed. See output above for details.${NC}"
        exit 1
    else
        exit 0
    fi
else
    echo -e "${RED}✗ No successful builds${NC}"
    echo ""
    echo "Tip: Run this script on each target platform to build all binaries."
    echo "CI/CD can run this matrix-style across platforms."
    exit 1
fi
