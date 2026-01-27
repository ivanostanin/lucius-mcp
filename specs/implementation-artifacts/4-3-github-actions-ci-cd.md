# Story 4.3: GitHub Actions CI/CD

Status: done
Story Key: 4-3-github-actions-ci-cd

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Developer,
I want GitHub Actions workflows that run quality checks on PRs and build/push release artifacts,
so that CI/CD enforces code quality and ships reproducible Docker images and bundles.

## Acceptance Criteria

1. **PR Quality Gate:** Given a pull request, when CI runs, then it executes `ruff`, `mypy --strict`, and unit tests, failing the workflow on any error.
2. **PR Integration Tests:** Given a pull request, when CI runs, then it executes integration tests.
3. **PR Docker Build & Push:** Given a pull request, when CI runs, then it builds the Docker image with a feature tag and pushes it to the registry.
4. **Release Docker Build & Push:** Given a release tag, when CI runs, then it builds the Docker image and pushes it to the registry.
5. **Status Reporting:** Given any CI run on a pull request, then the workflow reports pass/fail status to the pull request.
6. **MCPB Manifest Verification:** Given a PR or release, when CI runs, then it verifies the MCP bundle manifests using `deployment/scripts/validate_mcpb.py`.
7. **MCPB Build & Verification:** Given a PR or release, when CI runs, then it builds and verifies MCP bundles using `deployment/scripts/build-mcpb.sh` and `deployment/scripts/verify_mcpb_bundles.py`.
8. **MCPB Release Publishing:** Given a release tag, when CI runs, then it publishes the built MCP bundles to the GitHub Release.

## Tasks / Subtasks

- [x] Task 1: Audit existing CI workflows and map to AC (AC: #1-#5)
  - [x] Review `.github/workflows/pr-quality-gate.yml` for lint/type/test steps and current artifact steps
  - [x] Review `.github/workflows/release.yml` for tag validation and release artifact steps
  - [x] Review `.github/workflows/e2e-tests.yml` gating on Allure secrets
  - [x] Identify gaps for Docker build/push on PR and release

- [x] Task 2: Add Docker build/push for PR workflow (AC: #3, #5)
  - [x] Ensure Dockerfile path and build context align with Story 4.1 (expected: `deployment/Dockerfile`)
  - [x] Add registry login using repository secrets or `GITHUB_TOKEN` (GHCR)
  - [x] Build image with feature tags (e.g., `pr-<number>`, `sha-<short>`) and push to registry

- [x] Task 3: Add Docker build/push for release workflow (AC: #4)
  - [x] Tag image with release version (from tag/pyproject) and push to registry after tests pass
  - [x] Keep existing mcpb bundle build/release steps intact

- [x] Task 4: Verify PR status reporting (AC: #5)
  - [x] Ensure all CI jobs report pass/fail back to the PR

- [x] Task 5: Implement MCPB verification and publishing (AC: #6-#8)
  - [x] Integrate `deployment/scripts/validate_mcpb.py` into `pr-quality-gate.yml` and `release.yml`
  - [x] Use `deployment/scripts/build-mcpb.sh` for bundle creation in both workflows
  - [x] Integrate `deployment/scripts/verify_mcpb_bundles.py` to validate bundles after build
  - [x] Ensure `release.yml` correctly publishes the bundles to GitHub Releases

## Dev Notes

### Developer Context

- CI/CD already exists for PR checks, E2E, and releases. Extend existing workflows instead of creating new ones.
  - PR quality gate: `.github/workflows/pr-quality-gate.yml` runs ruff/mypy/unit+integration tests and builds MCPB bundles. It does **not** build/push Docker images yet. [Source: .github/workflows/pr-quality-gate.yml:1-69]
  - E2E tests: `.github/workflows/e2e-tests.yml` runs only when Allure secrets are configured. [Source: .github/workflows/e2e-tests.yml:1-52]
  - Release: `.github/workflows/release.yml` validates tag version, runs tests/lint/type checks, and builds MCPB bundles for GitHub Releases. It does **not** build/push Docker images yet. [Source: .github/workflows/release.yml:1-106]
- Docker containerization (Story 4.1) is a dependency for CI Docker builds. Architecture expects a `deployment/Dockerfile`; none is currently present in the repo, so coordinate with Story 4.1 before wiring Docker build steps. [Source: specs/project-planning-artifacts/epics.md:328-340; specs/architecture.md:170-206]
- Keep MCPB packaging steps intact, but refine them to use official scripts. Bundles must be validated (`deployment/scripts/validate_mcpb.py`), built (`deployment/scripts/build-mcpb.sh`), and verified (`deployment/scripts/verify_mcpb_bundles.py`) before being released. [Source: .github/workflows/pr-quality-gate.yml:42-69; .github/workflows/release.yml:66-106]

### Technical Requirements

- Use `uv` for dependency management and Python 3.14 in CI; do not switch to pip/poetry. [Source: specs/project-context.md:13-21]
- PR quality gate must run:
  - `uv run ruff check .`
  - `uv run mypy .`
  - `uv run --env-file .env.test pytest tests/unit/ tests/integration/ -v`
  [Source: .github/workflows/pr-quality-gate.yml:25-33; specs/project-context.md:64-69]
- Release workflow must run tests/lint/type checks before publishing artifacts. [Source: .github/workflows/release.yml:49-57]

### Architecture Compliance

- Keep infrastructure automation in `.github/workflows/` and build scripts under `deployment/scripts/`. [Source: specs/architecture.md:170-207]
- Maintain the `deployment/` boundary for Docker and Helm assets. [Source: specs/architecture.md:170-177]

### Library / Framework Requirements

- Prefer official GitHub Actions for setup and Docker:
  - `actions/checkout`, `actions/setup-python`, `actions/setup-node`
  - `docker/login-action`, `docker/build-push-action` (if adding Docker build/push)
- Use `GITHUB_TOKEN` for GHCR when possible; otherwise use repo secrets for registry credentials. Do not hardcode tokens.

### File Structure Requirements

- Workflows to modify:
  - `.github/workflows/pr-quality-gate.yml`
  - `.github/workflows/release.yml`
  - `.github/workflows/e2e-tests.yml` (only if CI orchestration requires it)
- Docker build should point at `deployment/Dockerfile` per architecture, or document deviations if Story 4.1 uses a different path. [Source: specs/architecture.md:170-177]

### Testing Requirements

- PR CI must run unit + integration tests via `pytest` (same commands as current quality gate). [Source: .github/workflows/pr-quality-gate.yml:31-33]
- E2E tests should remain gated by Allure secrets and must not block CI when secrets are missing. [Source: .github/workflows/e2e-tests.yml:9-39]

### Open Questions

- Which container registry should be used for Docker image publishing (GHCR vs Docker Hub)?
- What image naming/tagging convention is required beyond `pr-<number>` and release version tags?

### Project Context Reference

- Use `uv` and Python 3.14; keep strict `ruff` and `mypy --strict` checks. [Source: specs/project-context.md:13-22]
- Follow project workflow guidance for tests (`pytest` with `respx` for HTTP mocking). [Source: specs/project-context.md:64-69]

### Story Completion Status

- Status: done
- Completion note: Ultimate context engine analysis completed. CI/CD workflows implemented and verified via code review (Permissions fixed).

### References

- Story definition and ACs: `specs/project-planning-artifacts/epics.md:356-370`
- PRD phase-2 ops scope (Docker/Helm/CI/CD): `specs/prd.md:76-81`
- Architecture deployment boundary: `specs/architecture.md:170-207`
- Project context (uv, ruff, mypy, testing): `specs/project-context.md:13-22` and `specs/project-context.md:64-69`
- Existing workflows:
  - PR quality gate: `.github/workflows/pr-quality-gate.yml:1-69`
  - E2E tests: `.github/workflows/e2e-tests.yml:1-52`
  - Release: `.github/workflows/release.yml:1-106`

## Dev Agent Record

### Agent Model Used

gpt-5.2-codex

### Debug Log References

- [Review Fix] Added `permissions: packages: write` to `pr-quality-gate.yml` and `release.yml` to authorize GHCR image pushes.
- Verified logic for Docker build/push and MCPB bundle verification steps.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Added Docker build and push steps to `pr-quality-gate.yml` (ghcr.io).
- Added Docker build and push steps to `release.yml` (ghcr.io).
- Integrated `verify_mcpb_bundles.py` into both workflows to ensure bundle validity.
- Note: Docker build steps depend on `deployment/Dockerfile` (Story 4.1).

### File List

- .github/workflows/pr-quality-gate.yml
- .github/workflows/release.yml

