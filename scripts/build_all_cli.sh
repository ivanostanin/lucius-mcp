#!/usr/bin/env bash
# Master build script for all platform CLI binaries

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

echo "=================================="
echo "Building lucius CLI for all platforms"
echo "=================================="
echo ""

# Tracking results
BUILT=()
FAILED=()

# Function to build a platform
build_platform() {
    local platform=$1
    local script=$2

    echo "Building $platform..."
    if bash "$script"; then
        BUILT+=("$platform")
        echo "✓ $platform build succeeded"
    else
        FAILED+=("$platform")
        echo "✗ $platform build failed"
        echo ""
    fi
    echo ""
}

# Detect current platform
CURRENT_OS="$(uname -s)"
CURRENT_ARCH="$(uname -m)"

echo "Current platform: $CURRENT_OS $CURRENT_ARCH"
echo ""

# Build based on current platform
case "$CURRENT_OS" in
    Linux)
        case "$CURRENT_ARCH" in
            aarch64|arm64)
                build_platform "Linux ARM64" "deployment/scripts/build_cli_linux_arm64.sh"
                ;;
            x86_64)
                build_platform "Linux x86_64" "deployment/scripts/build_cli_linux_x86_64.sh"
                ;;
            *)
                echo "Warning: Unknown architecture $CURRENT_ARCH"
                ;;
        esac
        ;;
    Darwin)
        case "$CURRENT_ARCH" in
            arm64)
                build_platform "macOS ARM64" "deployment/scripts/build_cli_macos_arm64.sh"
                ;;
            x86_64)
                build_platform "macOS x86_64" "deployment/scripts/build_cli_macos_x86_64.sh"
                ;;
            *)
                echo "Warning: Unknown architecture $CURRENT_ARCH"
                ;;
        esac
        ;;
    MINGW*|MSYS*|CYGWIN*)
        # Windows - try to detect architecture
        if [ "$PROCESSOR_ARCHITECTURE" = "ARM64" ] || [ "$PROCESSOR_ARCHITEW6432" = "ARM64" ]; then
            build_platform "Windows ARM64" "deployment/scripts/build_cli_windows_arm64.bat"
        else
            build_platform "Windows x86_64" "deployment/scripts/build_cli_windows_x86_64.bat"
        fi
        ;;
    *)
        echo "Warning: Unknown OS $CURRENT_OS"
        ;;
esac

# Summary
echo "=================================="
echo "Build Summary"
echo "=================================="
echo ""

if [ ${#BUILT[@]} -gt 0 ]; then
    echo "Succeeded (${#BUILT[@]}):"
    for platform in "${BUILT[@]}"; do
        echo "  ✓ $platform"
    done
fi
echo ""

if [ ${#FAILED[@]} -gt 0 ]; then
    echo "Failed (${#FAILED[@]}):"
    for platform in "${FAILED[@]}"; do
        echo "  ✗ $platform"
    done
    echo ""
    exit 1
fi

echo "✓ All builds completed successfully!"
echo ""

# List built binaries
echo "Built binaries:"
find dist/cli -type f -name "lucius-*" 2>/dev/null | sort
