# Use a multi-stage build to keep the final image minimal
FROM python:3.14-slim-bookworm AS builder

# Install uv
# distinct layer to cache uv installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy dependency definition files
COPY pyproject.toml uv.lock ./

# Sync dependencies
# --frozen: use uv.lock strictly
# --no-dev: exclude dev dependencies
# --no-install-project: only install dependencies, not the project itself yet (caching)
RUN uv sync --frozen --no-dev --no-install-project

# Copy the rest of the application
COPY src/ src/
COPY README.md .

# Install the project itself
RUN uv sync --frozen --no-dev

# Final stage
FROM python:3.14-slim-bookworm

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY --from=builder /app/README.md /app/README.md

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"
# Add /app to PYTHONPATH so imports from 'src' work
ENV PYTHONPATH="/app"

# Environment variables defaults
ENV ALLURE_ENDPOINT="" \
    ALLURE_PROJECT_ID="" \
    ALLURE_API_TOKEN="" \
    LOG_LEVEL="INFO" \
    HOST="0.0.0.0" \
    PORT="8000" \
    MCP_MODE="http"

# Expose the default port
EXPOSE 8000

# Entrypoint
# This uses the 'lucius-mcp' script installed by uv in the venv
CMD ["lucius-mcp"]
