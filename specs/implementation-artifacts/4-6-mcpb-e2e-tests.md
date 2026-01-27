# Story 4.6: mcpb-e2e-tests

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Developer,
I want to add E2E tests that verify the specific `mcpb` lifecycle (manifests, bundles, execution),
so that I can ensure the packaging and distribution pipeline is robust and that generated bundles actually work.

## Acceptance Criteria

1.  **Verify Manifests**: Test must validate `mcpb` manifests against the schema (reuse logic from `deployment/scripts/validate_mcpb.py`).
2.  **Build Bundles**: Test must successfully build a bundle from the manifests (reuse or call `deployment/scripts/build-mcpb.sh`).
3.  **Verify Bundle Contents**: Test must inspect the generated bundle (zip/archive) and verify key files exist (reuse `verify_manifest` and `verify_python_bundle_contents` logic from `deployment/scripts/verify_mcpb_bundles.py`).
4.  **Unpack and Run**: Test must unpack the bundle and attempt to start the server from the unpacked content.
5.  **Server Startup Verification**: Verify that the server from the unpacked bundle starts up correctly and responds to initialization or health checks.

## Tasks / Subtasks

- [ ] Task 1: Create E2E Test Suite for mcpb (AC: 1, 2, 3)
    - [ ] Subtask 1.1: Implement test to validate `mcpb.yaml` / manifests, reusing logic from `validate_mcpb.py`.
    - [ ] Subtask 1.2: Implement test to build the bundle, either by calling `build-mcpb.sh` or porting its logic to Python.
    - [ ] Subtask 1.3: Implement verification of the output bundle structure, porting/reusing logic from `verify_mcpb_bundles.py`.
- [ ] Task 2: Runtime Verification (AC: 4, 5)
    - [ ] Subtask 2.1: Implement logic to unpack the bundle to a temporary location.
    - [ ] Subtask 2.2: Implement execution test that runs the server (e.g., using `subprocess` or `uv run`) from the unpacked location and performs a connection handshake/ping.

## Dev Notes

- **Existing Scripts**: 
  - `deployment/scripts/validate_mcpb.py`: Manifest validation and entry point checking.
  - `deployment/scripts/verify_mcpb_bundles.py`: Bundle content verification.
  - `deployment/scripts/build-mcpb.sh`: Build process (vendor dependencies, pack).
- **Environment**: These tests might take longer to run; ensure they are marked appropriately (e.g., `@pytest.mark.e2e`).
- **Isolation**: Use `tempfile` for unpacking and building to avoid polluting the workspace.

### Project Structure Notes

- Tests should go in `tests/e2e/`.

### References

- `mcpb` documentation/readme.
- Existing CI/CD scripts.

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List

### File List
