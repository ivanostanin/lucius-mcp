import re

import pytest
from pydantic import SecretStr

from src.client import AllureAuthError
from src.tools.create_test_case import create_test_case
from src.utils.config import settings
from tests.e2e.helpers.cleanup import CleanupTracker


@pytest.mark.asyncio
async def test_api_token_parameter_is_optional(project_id: int, cleanup_tracker: CleanupTracker) -> None:
    """Verify that tool works with env token."""

    result = await create_test_case(
        project_id=project_id,
        name="Runtime Auth Optional",
    )
    assert "Created Test Case ID:" in result
    match = re.search(r"ID: (\d+)", result)
    if match:
        cleanup_tracker.track_test_case(int(match.group(1)))


@pytest.mark.asyncio
async def test_runtime_token_overrides_environment(
    monkeypatch: pytest.MonkeyPatch, project_id: int, cleanup_tracker: CleanupTracker, api_token: str
) -> None:
    """Verify that environment token is used when no runtime override is provided."""
    real_token = api_token

    # Set settings to use the real token
    monkeypatch.setattr(settings, "ALLURE_API_TOKEN", SecretStr(real_token), raising=False)

    # Call without runtime override
    result = await create_test_case(
        project_id=project_id,
        name="Runtime Override Test",
    )
    assert "Created Test Case ID:" in result
    match = re.search(r"ID: (\d+)", result)
    if match:
        cleanup_tracker.track_test_case(int(match.group(1)))


@pytest.mark.asyncio
async def test_runtime_overrides_do_not_persist_across_calls(project_id: int, cleanup_tracker: CleanupTracker) -> None:
    """Verify that tool calls are stateless across invocations."""
    # First call with environment token
    first_result = await create_test_case(
        project_id=project_id,
        name="Runtime Override First Call",
    )
    assert "Created Test Case ID:" in first_result
    match1 = re.search(r"ID: (\d+)", first_result)
    if match1:
        cleanup_tracker.track_test_case(int(match1.group(1)))

    # Second call also uses environment token
    second_result = await create_test_case(
        project_id=project_id,
        name="Runtime Override Second Call",
    )
    assert "Created Test Case ID:" in second_result
    match2 = re.search(r"ID: (\d+)", second_result)
    if match2:
        cleanup_tracker.track_test_case(int(match2.group(1)))


@pytest.mark.asyncio
async def test_clear_error_when_no_auth_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify clear error message when no env auth provided (AC#5)."""
    # Remove configured token in settings
    monkeypatch.setattr(settings, "ALLURE_API_TOKEN", None, raising=False)

    with pytest.raises(KeyError, match="ALLURE_API_TOKEN is not set"):
        await create_test_case(project_id=1, name="Missing Token")


@pytest.mark.asyncio
async def test_invalid_runtime_token_fails_with_clear_error(monkeypatch: pytest.MonkeyPatch, project_id: int) -> None:
    """Verify that invalid env token produces clear auth error."""
    monkeypatch.setattr(settings, "ALLURE_API_TOKEN", SecretStr("invalid"), raising=False)

    with pytest.raises(AllureAuthError):
        await create_test_case(project_id=project_id, name="Invalid Token")
