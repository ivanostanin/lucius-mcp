---
title: "Address deferred Python compatibility follow-ups"
type: "refactor"
created: "2026-08-11"
status: "in-review"
baseline_commit: "947ee95cfb09358906448e635c5f71e27d30a27a"
context:
  - "{project-root}/docs/development.md"
  - "{project-root}/specs/implementation-artifacts/deferred-work.md"
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Story 10.4 left three reliability gaps: metadata tests can accept
comments or duplicate text, Python 3.10 test setup mutates public tool exports
globally, and MCPB verification relies on the caller's working directory and
narrow TOML regular expressions.

**Approach:** Use parsed project metadata for contract tests and MCPB runtime
verification, scope Python 3.10 module patching to the affected tests, and
make the verifier resolve every repository path from its own location.

## Boundaries & Constraints

**Always:** Preserve the Python 3.10–3.14 range, existing MCPB manifest
contracts, and test behavior outside the currently affected patch targets.
Keep the current staged/unstaged `deferred-work.md` state as the starting
record, removing entries only when their matching fix is verified.

**Ask First:** Any change to public tool exports, generated MCPB manifests,
package dependencies, or CI matrix coverage beyond the already-recorded work.

**Never:** Replace TOML parsing with another text/regex parser, weaken
metadata assertions, or alter unrelated documentation/release workflow logic.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
| --- | --- | --- | --- |
| Metadata contract | Comment/duplicate TOML text | Assertion reads the actual project table value | Fails on invalid parsed metadata |
| Python 3.10 patch | A test patches `src.tools.<tool>` | Only that patch target resolves as its implementation module | Other exports retain normal behavior |
| MCPB verifier | Invoked outside repository root | Finds `pyproject.toml` and bundles from script-derived root | Returns validation failure, not path/import errors |
| Runtime metadata | Valid TOML quoting/comments | Reads `[project].requires-python` through TOML parser | Raises a clear error for missing/invalid metadata |

</frozen-after-approval>

## Code Map

- `tests/docs/test_mcp_registry.py`, `tests/packaging/test_cli_python_versions_contract.py` — structured project metadata assertions.
- `tests/conftest.py` and affected tests — Python 3.10 mock-target resolution.
- `deployment/scripts/update_mcpb_runtime.py`, `deployment/scripts/verify_mcpb_bundles.py` — shared parsed metadata and repository-root resolution.
- `tests/packaging/test_mcpb_bundles.py`, `tests/packaging/test_mcpb_manifests.py` — verifier/runtime regressions.
- `specs/implementation-artifacts/deferred-work.md` — completed-item record.

## Tasks & Acceptance

**Execution:**

- [ ] Replace raw `pyproject.toml` substring assertions with parsed project metadata assertions.
- [ ] Replace the Python <3.11 autouse export remapping fixture with targeted patch resolution that leaves unrelated `src.tools` exports intact.
- [ ] Consolidate MCPB `requires-python` and version reads on TOML parsing; resolve paths/imports from the verifier's repository root.
- [ ] Add regression coverage for comments/quoted metadata, external-CWD verifier execution, and Python 3.10 patch isolation.
- [ ] Update the deferred record only for verified fixes.

**Acceptance Criteria:**

- Given commented or duplicated text outside `[project]`, when metadata tests run, then they assert the real parsed values.
- Given Python 3.10 and a mock target needing module resolution, when that test patches it, then the target resolves without globally changing other tool exports.
- Given the MCPB verifier starts outside the checkout, when bundle metadata is valid, then it validates against the root `pyproject.toml` without import/path errors.

## Verification

**Commands:**

- `uv run --python 3.10 --extra dev pytest tests/docs tests/packaging -q` — expected: affected contracts pass on the compatibility floor.
- `uv run --python 3.14 --extra dev pytest tests/docs tests/packaging -q` — expected: affected contracts pass without `tomli` installed.
- `uv run --python 3.10 --extra dev pytest tests/unit tests/integration -q` — expected: targeted mocking remains portable.
- `uv run --python 3.10 --extra dev ruff check tests deployment/scripts` — expected: no lint violations.
