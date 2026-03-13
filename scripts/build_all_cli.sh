#!/usr/bin/env bash
# Compatibility wrapper for the canonical build-all script location.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -P)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd -P)"

exec bash "${PROJECT_ROOT}/deployment/scripts/build_all_cli.sh" "$@"
