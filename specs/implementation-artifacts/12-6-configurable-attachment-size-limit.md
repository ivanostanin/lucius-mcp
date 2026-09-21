---
title: 'Story 12.6: Configurable attachment upload size limit'
type: 'feature'
created: '2026-09-21'
status: 'done'
baseline_commit: '36b82c2'
context:
  - '../../docs/development.md'
  - '../../docs/setup.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Attachment uploads are capped by a source-level constant of 10 MiB, so deployments that need a different limit must modify and rebuild the application.

**Approach:** Add a validated `ATTACHMENT_MAX_FILE_BYTES` application setting, defaulting to the existing 10 MiB behavior, and use it for test-case, test-result, step, and fixture attachment uploads. Document the variable and its default.

## Boundaries & Constraints

**Always:** Preserve the current default and reject non-positive configured values during settings validation. Apply the limit to decoded Base64 content and downloaded URL content before sending it to Allure TestOps. Keep the existing MIME allowlist and error behavior.

**Ask First:** None; the environment variable name and default are part of this story.

**Never:** Do not change attachment download-cache limits, MIME support, upload APIs, or the separate launch result-file upload behavior. Do not silently raise the default limit.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Default | Variable omitted | Upload limit remains 10 MiB | N/A |
| Custom limit | `ATTACHMENT_MAX_FILE_BYTES=104857600` | Attachments up to 100 MiB are eligible for upload | N/A |
| Invalid limit | Zero, negative, or non-integer value | Settings cannot be constructed | Pydantic validation error |
| Oversized Base64 | Decoded content exceeds configured bytes | Upload is rejected before the Allure request | Existing validation error identifies the configured limit |
| Oversized URL | Downloaded content exceeds configured bytes | Download/upload is rejected | Existing validation error identifies the configured limit |

</frozen-after-approval>

## Code Map

- `src/utils/config.py` -- application settings loaded from environment and `.env`.
- `src/services/attachment_service.py` -- shared attachment upload limit used by test-case uploads.
- `src/services/launch_service.py` -- test-result, step, and fixture attachment validation.
- `docs/setup.md` -- documented environment variables and defaults.
- `tests/unit/test_config.py` -- environment parsing and positive-value validation coverage.
- `tests/unit/test_attachment_service.py` -- configured limit enforcement for upload content.

## Tasks & Acceptance

**Execution:**
- [x] `src/utils/config.py` -- add `ATTACHMENT_MAX_FILE_BYTES` with a positive integer validator and 10 MiB default -- expose the limit through the existing settings mechanism.
- [x] `src/services/attachment_service.py` -- source the shared upload limit from application settings -- preserve existing consumers and validation messages.
- [x] `docs/setup.md` -- document the new variable, units, default, and Base64/URL upload scope -- make deployment configuration discoverable.
- [x] `tests/unit/test_config.py` -- cover default, custom environment value, and invalid values -- prevent regressions in settings parsing.
- [x] `tests/unit/test_attachment_service.py` -- cover configured-limit acceptance and rejection -- verify enforcement before client upload.

**Acceptance Criteria:**
- Given no `ATTACHMENT_MAX_FILE_BYTES` is configured, when the application starts, then the effective upload limit is 10 MiB.
- Given `ATTACHMENT_MAX_FILE_BYTES=104857600`, when an attachment is validated, then content up to 100 MiB is accepted by Lucius' size guard.
- Given an invalid or non-positive value, when settings are loaded, then startup/configuration fails with a validation error.
- Given decoded Base64 or downloaded URL content larger than the configured limit, when an upload is attempted, then Lucius rejects it before calling the Allure upload client.

## Spec Change Log

## Design Notes

The setting is read at process startup through `pydantic-settings`, matching the existing application configuration model. The shared service-level value is intentionally reused by launch attachment paths so all attachment upload entry points enforce the same configured limit.

## Verification

**Commands:**
- `uv run pytest tests/unit/test_config.py tests/unit/test_attachment_service.py tests/unit/test_launch_service.py -q` -- expected: all focused configuration and attachment tests pass.
- `uv run ruff check src/utils/config.py src/services/attachment_service.py src/services/launch_service.py tests/unit/test_config.py tests/unit/test_attachment_service.py` -- expected: no lint errors.
- `uv run mypy --strict src` -- expected: type checking succeeds.

## Suggested Review Order

**Configuration boundary**

- The setting preserves the existing default while validating deployment overrides.
  [`config.py:34`](../../src/utils/config.py#L34)

- The shared upload service consumes the startup-resolved limit for test-case uploads.
  [`attachment_service.py:14`](../../src/services/attachment_service.py#L14)

- The existing decoded/downloaded content guard now uses that shared configured value.
  [`attachment_service.py:64`](../../src/services/attachment_service.py#L64)

**Deployment surface**

- The setup reference documents units and the unchanged 10 MiB default.
  [`setup.md:72`](../../docs/setup.md#L72)

- The example environment file shows the deployable configuration explicitly.
  [`.env.example:11`](../../.env.example#L11)

**Verification**

- Settings tests cover default, environment override, and invalid values.
  [`test_config.py:7`](../../tests/unit/test_config.py#L7)

- Upload tests cover rejection above and acceptance at the configured boundary.
  [`test_attachment_service.py:11`](../../tests/unit/test_attachment_service.py#L11)
