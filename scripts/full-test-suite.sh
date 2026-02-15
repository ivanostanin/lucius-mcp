#!/bin/bash

uv run ruff format scripts src tests deployment && \
uv run ruff check scripts src tests deployment --fix --unsafe-fixes && \
uv run mypy src && \
uv run pytest tests/unit tests/integration && \
uv run --env-file .env.test pytest tests/e2e -n auto -rs && \
uv run pytest tests/docs && \
uv run pytest tests/packaging
