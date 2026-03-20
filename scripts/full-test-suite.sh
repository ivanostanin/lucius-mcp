#!/bin/bash

set -euo pipefail

cleanup_cli_dist=true

for arg in "$@"; do
  case "$arg" in
    --no-cleanup)
      cleanup_cli_dist=false
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      echo "Usage: $0 [--no-cleanup]" >&2
      exit 1
      ;;
  esac
done

uv run ruff format scripts src tests deployment
uv run ruff check scripts src tests deployment --fix --unsafe-fixes
uv run mypy src
uv run pytest tests/unit tests/integration tests/cli
uv run pytest tests/docs

if [[ -f .env.test ]]; then
  uv run --env-file .env.test pytest tests/e2e -n auto -rs
else
  echo "Skipping E2E tests: .env.test not found"
fi

if [[ "$cleanup_cli_dist" == true ]]; then
  mkdir -p dist/cli
  shopt -s nullglob
  cli_binaries=(dist/cli/lucius-*)
  if (( ${#cli_binaries[@]} > 0 )); then
    rm -f "${cli_binaries[@]}"
  fi
  shopt -u nullglob
else
  echo "Skipping dist/cli cleanup (--no-cleanup)"
fi

uv run pytest tests/packaging
