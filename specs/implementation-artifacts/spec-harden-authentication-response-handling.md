---
title: 'Harden authentication response handling'
type: 'bugfix'
created: '2026-07-17'
status: 'done'
baseline_commit: 'a3564f5db5af05b5a8c9da6ee46346caa9e3a0db'
context:
  - '{project-root}/docs/development.md'
  - '{project-root}/specs/project-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** A successful OAuth token-exchange response can contain invalid JSON or omit `access_token`. In those cases, `AllureClient._get_jwt_token()` currently leaks a decoder or key error instead of the client’s authentication error.

**Approach:** Treat malformed successful token responses as failed authentication exchanges. Preserve the existing transport and non-success HTTP error behavior while adding focused regression coverage.

## Boundaries & Constraints

**Always:** Raise `AllureAuthError` for invalid JSON or a missing `access_token` after a successful token-exchange HTTP response; retain useful response status/body metadata through the established exception API; use async `httpx` and `respx` test patterns.

**Ask First:** Broaden validation beyond the specified malformed JSON and missing-token cases (for example, rejecting an empty or non-string token value).

**Never:** Change OAuth request inputs, token-refresh timing, public API signatures, or unrelated authentication flows; expose the API token in errors or tests.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Valid exchange | HTTP 200 with JSON object containing `access_token` | Cache and return JWT as today | N/A |
| Invalid JSON | HTTP 200 token response with non-JSON body | Token exchange fails consistently | Raise `AllureAuthError`, retaining response metadata |
| Missing token | HTTP 200 with JSON object lacking `access_token` | Token exchange fails consistently | Raise `AllureAuthError`, retaining response metadata |
| HTTP failure | Non-2xx token response | Existing error behavior remains | Existing `AllureAuthError` behavior |

</frozen-after-approval>

## Code Map

- `src/client/client.py` -- performs OAuth API-token-to-JWT exchange and maps HTTP errors to typed client exceptions.
- `tests/unit/test_client.py` -- contains `respx`-backed OAuth exchange tests and shared client fixtures.
- `src/client/exceptions.py` -- defines the `AllureAuthError` used for authentication failures.

## Tasks & Acceptance

**Execution:**

- [x] `src/client/client.py` -- map JSON decoding and missing required token-field failures after status validation to `AllureAuthError`, carrying the successful response’s metadata -- prevents implementation-level exceptions from escaping the authentication boundary.
- [x] `tests/unit/test_client.py` -- add focused asynchronous `respx` tests for a non-JSON success response and a JSON success response without `access_token` -- locks in the typed-error contract.

**Acceptance Criteria:**

- Given a successful token exchange with invalid JSON, when a client initializes, then it raises `AllureAuthError` rather than a JSON decoding error.
- Given a successful token exchange whose JSON omits `access_token`, when a client initializes, then it raises `AllureAuthError` rather than `KeyError`.
- Given a valid token response or a non-success HTTP response, when token exchange runs, then its established behavior remains unchanged.

## Spec Change Log

## Verification

**Commands:**

- `uv run pytest tests/unit/test_client.py -q` -- expected: focused client unit tests pass.
- `uv run ruff check src/client/client.py tests/unit/test_client.py` -- expected: no lint violations in touched files.

## Suggested Review Order

**Authentication boundary**

- Convert malformed successful responses at the OAuth boundary into the client’s typed authentication error.
  [`client.py:454`](../../src/client/client.py#L454)

**Regression coverage**

- Exercise invalid JSON, a missing field, and a non-object JSON response through client initialization.
  [`test_client.py:261`](../../tests/unit/test_client.py#L261)
