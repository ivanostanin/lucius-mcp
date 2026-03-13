#!/usr/bin/env bash
# Build CLI binary for Unix platforms (Linux/macOS) and architectures.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -P)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${PROJECT_ROOT}"

normalize_platform() {
    case "$1" in
        Linux|linux) echo "linux" ;;
        Darwin|darwin|macos) echo "macos" ;;
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

TARGET_PLATFORM="$(normalize_platform "$(uname -s)")"
TARGET_ARCH="$(normalize_arch "$(uname -m)")"
ONEFILE=true
CLEAN=true
JOBS=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --platform)
            if [[ $# -lt 2 ]]; then
                echo "Error: --platform requires a value"
                exit 1
            fi
            TARGET_PLATFORM="$(normalize_platform "$2")"
            shift 2
            ;;
        --arch)
            if [[ $# -lt 2 ]]; then
                echo "Error: --arch requires a value"
                exit 1
            fi
            TARGET_ARCH="$(normalize_arch "$2")"
            shift 2
            ;;
        --no-onefile)
            ONEFILE=false
            shift
            ;;
        --no-clean)
            CLEAN=false
            shift
            ;;
        --jobs)
            if [[ $# -lt 2 ]]; then
                echo "Error: --jobs requires a value"
                exit 1
            fi
            JOBS="$2"
            shift 2
            ;;
        --help|-h)
            cat <<'EOF'
Usage: deployment/scripts/build_cli_unix.sh [OPTIONS]

Options:
  --platform <linux|macos>  Target platform (default: current platform)
  --arch <arm64|x86_64>     Target architecture (default: current architecture)
  --no-onefile              Disable --onefile mode
  --no-clean                Do not remove previous target artifacts
  --jobs <N>                Number of Nuitka jobs
  --help, -h                Show help
EOF
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [[ "${TARGET_PLATFORM}" != "linux" && "${TARGET_PLATFORM}" != "macos" ]]; then
    echo "Error: Unsupported --platform '${TARGET_PLATFORM}'. Use linux or macos."
    exit 1
fi

if [[ "${TARGET_ARCH}" != "arm64" && "${TARGET_ARCH}" != "x86_64" ]]; then
    echo "Error: Unsupported --arch '${TARGET_ARCH}'. Use arm64 or x86_64."
    exit 1
fi

CURRENT_PLATFORM="$(normalize_platform "$(uname -s)")"
CURRENT_ARCH="$(normalize_arch "$(uname -m)")"
if [[ "${CURRENT_PLATFORM}" != "${TARGET_PLATFORM}" ]]; then
    echo "Error: This host is '${CURRENT_PLATFORM}' but target platform is '${TARGET_PLATFORM}'."
    exit 1
fi
if [[ "${CURRENT_ARCH}" != "${TARGET_ARCH}" ]]; then
    echo "Warning: Building ${TARGET_PLATFORM}-${TARGET_ARCH} on ${CURRENT_ARCH} may require cross-compilation support."
fi

if ! command -v uv >/dev/null 2>&1; then
    echo "Error: uv not found. Install from https://astral.sh/uv"
    exit 1
fi

OUTPUT_DIR="dist/cli"
OUTPUT_BASENAME="lucius-${TARGET_PLATFORM}-${TARGET_ARCH}"
OUTPUT_FILE="${OUTPUT_DIR}/${OUTPUT_BASENAME}"

echo "Building lucius CLI for ${TARGET_PLATFORM} ${TARGET_ARCH}..."

if [[ "${CLEAN}" == true ]]; then
    mkdir -p "${OUTPUT_DIR}"
    shopt -s nullglob
    target_artifacts=("${OUTPUT_DIR}/${OUTPUT_BASENAME}"*)
    if (( ${#target_artifacts[@]} > 0 )); then
        rm -rf "${target_artifacts[@]}"
    fi
    shopt -u nullglob
fi

echo "Generating tool schemas..."
uv --quiet run --python 3.13 --extra dev python scripts/build_tool_schema.py

if [[ ! -f "src/cli/data/tool_schemas.json" ]]; then
    echo "Error: tool_schemas.json not found after generation"
    exit 1
fi

nuitka_args=(
    --standalone
    --assume-yes-for-downloads
    --output-dir="${OUTPUT_DIR}"
    --output-filename="${OUTPUT_BASENAME}"
    --include-package=rich._unicode_data
    --include-data-files=src/cli/data/tool_schemas.json=data/tool_schemas.json
)

if [[ "${TARGET_PLATFORM}" == "macos" ]]; then
    nuitka_args+=(--macos-create-app-bundle)
fi

if [[ "${ONEFILE}" == true ]]; then
    nuitka_args+=(--onefile)
fi

if [[ -n "${JOBS}" ]]; then
    nuitka_args+=(--jobs="${JOBS}")
fi

uv run --python 3.13 --extra dev nuitka "${nuitka_args[@]}" src/cli/cli_entry.py

echo "Built: ${OUTPUT_FILE}"
echo "${TARGET_PLATFORM} ${TARGET_ARCH} build complete"
