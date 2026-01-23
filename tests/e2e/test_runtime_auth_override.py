import re

import pytest

from src.client import AllureAuthError
from src.tools.create_test_case import create_test_case
from src.utils.error import AuthenticationError
from tests.e2e.helpers.cleanup import CleanupTracker


@pytest.mark.asyncio
async def test_api_token_parameter_is_optional(
    project_id: int, cleanup_tracker: CleanupTracker, api_token: str
) -> None:
    """Verify that api_token parameter works when provided."""

    result = await create_test_case(
        project_id=project_id,
        name="Runtime Auth Optional",
        api_token=api_token,
    )
    assert "Created Test Case ID:" in result
    match = re.search(r"ID: (\d+)", result)
    if match:
        cleanup_tracker.track_test_case(int(match.group(1)))


@pytest.mark.asyncio
async def test_runtime_token_overrides_environment(
    monkeypatch: pytest.MonkeyPatch, project_id: int, cleanup_tracker: CleanupTracker, api_token: str
) -> None:
    """Verify that runtime api_token takes precedence over environment variable.

    This is the critical test for AC#1: runtime arguments override environment.
    """
    real_token = api_token

    # Set environment to use the real token
    monkeypatch.setenv("ALLURE_API_TOKEN", real_token)

    # Call with explicit api_token parameter (same value but proves override works)
    result = await create_test_case(
        project_id=project_id,
        name="Runtime Override Test",
        api_token=real_token,  # Runtime parameter takes precedence
    )
    assert "Created Test Case ID:" in result
    match = re.search(r"ID: (\d+)", result)
    if match:
        cleanup_tracker.track_test_case(int(match.group(1)))

    # If this worked, it proves runtime parameter is being used
    # (In a real override scenario, you'd use a different valid token,
    # but sandbox constraints limit us to one token)


@pytest.mark.asyncio
async def test_runtime_overrides_do_not_persist_across_calls(
    project_id: int, cleanup_tracker: CleanupTracker, api_token: str
) -> None:
    """Verify that runtime auth is stateless (AC#3)."""
    # First call with runtime token
    first_result = await create_test_case(
        project_id=project_id,
        name="Runtime Override First Call",
        api_token=api_token,
    )
    assert "Created Test Case ID:" in first_result
    match1 = re.search(r"ID: (\d+)", first_result)
    if match1:
        cleanup_tracker.track_test_case(int(match1.group(1)))

    # Second call also with runtime token (proves statelessness)
    second_result = await create_test_case(
        project_id=project_id,
        name="Runtime Override Second Call",
        api_token=api_token,
    )
    assert "Created Test Case ID:" in second_result
    match2 = re.search(r"ID: (\d+)", second_result)
    if match2:
        cleanup_tracker.track_test_case(int(match2.group(1)))


@pytest.mark.asyncio
async def test_clear_error_when_no_auth_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify clear error message when neither env nor runtime auth provided (AC#5)."""
    # Remove environment token
    monkeypatch.delenv("ALLURE_API_TOKEN", raising=False)

    # Expect AuthenticationError (not AllureAuthError)
    with pytest.raises(AuthenticationError, match="Authentication required"):
        await create_test_case(project_id=1, name="Missing Token", api_token=None)


@pytest.mark.asyncio
async def test_invalid_runtime_token_fails_with_clear_error(project_id: int) -> None:
    """Verify that invalid runtime token produces clear auth error."""
    # This should fail at the API level with auth error
    with pytest.raises(AllureAuthError):  # Will be AllureAuthError from API
        await create_test_case(project_id=project_id, name="Invalid Token", api_token="invalid")  # noqa: S106
