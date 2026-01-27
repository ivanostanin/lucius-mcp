# Story 4.5: set-up-act

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Developer,
I want to set up nektos/act environment to test github workflows locally,
so that I can ensure consistent local testing of CI/CD pipelines without polluting the repo or waiting for remote runners.

## Acceptance Criteria

1. **Install nektos/act**: Verify `act` is installed and available in the shell path.
2. **Configure Artifact Server**: Ensure `act` runs with the `--artifact-server-path $PWD/.artifacts` flag to correctly handle artifacts locally.
3. **Verify Local Execution**: Successfully run at least one existing GitHub workflow (e.g., CI or Build) using `act` locally.
4. **Documentation**: Add a section to `README.md` or a `docs/setup.md` explaining how to run workflows locally using `act`, covering the artifact path requirement.

## Tasks / Subtasks

- [ ] Task 1: Install and Verify act (AC: 1)
  - [ ] Subtask 1.1: Install `act` (e.g., via Homebrew on Mac).
  - [ ] Subtask 1.2: Verify version and run a smoke test (`act --version`).
- [ ] Task 2: Configure and Run Workflows (AC: 2, 3)
  - [ ] Subtask 2.1: Run a workflow with `--artifact-server-path $PWD/.artifacts`.
  - [ ] Subtask 2.2: Verify artifacts are created in `.artifacts` directory.
- [ ] Task 3: Documentation and Git Ignore (AC: 4)
  - [ ] Subtask 3.1: Add `.artifacts/` to `.gitignore`.
  - [ ] Subtask 3.2: Document usage instructions.

## Dev Notes

- **Reference**: [nektos/act Usage](https://nektosact.com/usage/index.html)
- **Artifact Server**: The `--artifact-server-path` argument is critical for testing workflows that use `actions/upload-artifact` or `download-artifact`.
- **Environment**: Ensure `.env` or `.secrets` files are handled correctly if the workflows require secrets.

### Project Structure Notes

- `.artifacts/` directory should be at the project root and ignored by git.
- Tests should be non-destructive.

### References

- [nektos/act](https://github.com/nektos/act)

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List

### File List
