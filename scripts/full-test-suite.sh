#!/bin/bash

uv run ruff format . && \
uv run ruff check . --fix --unsafe-fixes && \
uv run mypy src && \
uv run pytest tests/unit tests/integration && \
uv run --env-file .env.test pytest tests/e2e -n auto && \
uv run pytest tests/docs && \
uv run pytest tests/packaging
