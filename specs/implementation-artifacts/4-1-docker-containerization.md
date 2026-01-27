# Story 4.1: Docker Containerization

Status: ready-for-dev
Story Key: 4-1-docker-containerization

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a DevOps Engineer,
I want the lucius-mcp server packaged as a Docker image,
so that it can be deployed consistently in containerized environments.

## Acceptance Criteria

1. **Buildable Image:** Given the lucius-mcp source code, when `docker build` runs, then it produces a runnable image without errors.
2. **Server Startup:** Given the built image, when the container starts, then the Starlette/FastMCP server launches and listens on the configured port.
3. **Configuration via Env:** Given runtime env vars (e.g., `ALLURE_ENDPOINT`, `ALLURE_API_TOKEN`, `ALLURE_PROJECT_ID`), when the container starts, then the server reads them correctly.
4. **Reproducible Runtime:** Given the image build, then dependencies are installed in a reproducible way aligned with `uv`/`pyproject.toml` and lock file.
5. **Container Entry Point:** Given the container, then the entry point runs the MCP server in stdio or HTTP mode as configured by env (no manual shell steps).
6. **No Secrets in Image:** Given the build, then no secrets are baked into the image or Dockerfile (env-only at runtime).

## Tasks / Subtasks

- [ ] Task 1: Define Docker build strategy (AC: #1, #4, #5, #6)
  - [ ] Confirm base image choice compatible with Python 3.14 and `uv`
  - [ ] Decide entrypoint command (`lucius-mcp`) and env defaults
  - [ ] Confirm runtime mode handling (`MCP_MODE=http|stdio`) and exposed port

- [ ] Task 2: Implement Dockerfile under `deployment/` (AC: #1-#5)
  - [ ] Add `deployment/Dockerfile` using a multi-stage build and `uv.lock`
  - [ ] Ensure dependencies are installed reproducibly and app code is copied once
  - [ ] Set entrypoint to run the MCP server without manual shell steps

- [ ] Task 3: Build/run verification (AC: #1-#3, #5)
  - [ ] `docker build -f deployment/Dockerfile -t lucius-mcp:local .`
  - [ ] `docker run` starts server and reads env vars (`ALLURE_*`, `HOST`, `PORT`, `MCP_MODE`)

## Dev Notes

### Developer Context

- No Dockerfile exists yet in the repo; this story is responsible for creating `deployment/Dockerfile` aligned with architecture decisions. [Source: specs/architecture.md:170-207]
- CI/CD workflows for PR and release currently exist, but do **not** build Docker images. Story 4.3 will wire Docker build/push once this Dockerfile exists. [Source: .github/workflows/pr-quality-gate.yml:1-69; .github/workflows/release.yml:1-106]
- The app is launched via the console script `lucius-mcp` (entry point: `src.main:start`). The Docker entrypoint should use this to avoid duplicating run logic. [Source: pyproject.toml:21-22]

### Technical Requirements

- **Python:** 3.14 (managed by `uv`), no pip/poetry. [Source: specs/project-context.md:13-21]
- **Dependencies:** Use `pyproject.toml` and `uv.lock` for reproducible builds. [Source: pyproject.toml:1-29]
- **Runtime config:** Environment variables used by the app include `ALLURE_ENDPOINT`, `ALLURE_PROJECT_ID`, `ALLURE_API_TOKEN`, `LOG_LEVEL`, `HOST`, `PORT`, `MCP_MODE`. [Source: README.md:18-27]
- **Entry point:** `lucius-mcp` CLI starts the server (default HTTP mode). `MCP_MODE=stdio` switches to stdio mode. [Source: README.md:63-73]

### Architecture Compliance

- Keep deployment artifacts under `deployment/` and avoid root-level build scripts. [Source: specs/architecture.md:170-207]
- Follow the "Thin Tool / Fat Service" and global error handling conventions (no impact on Dockerfile but must not break runtime). [Source: specs/project-context.md:25-37]

### Library / Framework Requirements

- Use Docker best practices: multi-stage builds, minimal final image, no secrets in layers. [Source: https://docs.docker.com/build/building/best-practices/]

### File Structure Requirements

- `deployment/Dockerfile` (new)
- `deployment/.dockerignore` if needed to keep build context clean (prefer reusing existing `.dockerignore` if present)

### Testing Requirements

- Build and run locally to confirm the container launches and honors env vars. Use `MCP_MODE=http` (default) or `MCP_MODE=stdio` for stdio runs.

### Open Questions

- Should the Docker image target GHCR, Docker Hub, or another registry? (Used by Story 4.3 for CI push)
- Should the image expose a default port (e.g., 8000) or rely solely on `PORT` env?

### Project Context Reference

- `uv` + Python 3.14 + Starlette + FastMCP stack. [Source: specs/project-context.md:13-21]
- Use `uv run` for local dev; container can invoke the entrypoint directly (`lucius-mcp`). [Source: README.md:63-73]

### Story Completion Status

- Status: ready-for-dev
- Completion note: Ultimate context engine analysis completed - comprehensive developer guide created.

### References

- Story definition and ACs: `specs/project-planning-artifacts/epics.md:328-370`
- Architecture deployment boundary: `specs/architecture.md:170-207`
- Project context (stack, rules): `specs/project-context.md:13-37`
- CLI entrypoint: `pyproject.toml:21-22`
- Runtime env vars: `README.md:18-27`

## Dev Agent Record

### Agent Model Used

gpt-5.2-codex

### Debug Log References

- N/A (context generation only)

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.

### File List

- deployment/Dockerfile
- deployment/.dockerignore (if needed)
- pyproject.toml
- uv.lock
- README.md
