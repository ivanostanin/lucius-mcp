#!/bin/bash

set -euo pipefail

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

rm -rf dist/cli
uv run pytest tests/packaging
