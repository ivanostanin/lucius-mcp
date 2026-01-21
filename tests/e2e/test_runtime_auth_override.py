import os

import pytest

from src.client import AllureAuthError
from src.tools.create_test_case import create_test_case


def _sandbox_configured() -> bool:
    return bool(os.getenv("ALLURE_ENDPOINT") and os.getenv("ALLURE_API_TOKEN"))


@pytest.mark.asyncio
async def test_runtime_auth_override_optional(project_id: int) -> None:
    if not _sandbox_configured():
        pytest.skip("Sandbox credentials not configured (ALLURE_ENDPOINT/TOKEN)")

    api_token = os.environ["ALLURE_API_TOKEN"]

    result = await create_test_case(
        project_id=project_id,
        name="Runtime Auth Optional",
        api_token=api_token,
    )
    assert "Created Test Case ID:" in result


@pytest.mark.asyncio
async def test_runtime_auth_override_uses_runtime_token(project_id: int) -> None:
    if not _sandbox_configured():
        pytest.skip("Sandbox credentials not configured (ALLURE_ENDPOINT/TOKEN)")

    api_token = os.environ["ALLURE_API_TOKEN"]

    result = await create_test_case(
        project_id=project_id,
        name="Runtime Auth Override",
        api_token=api_token,
    )
    assert "Created Test Case ID:" in result


@pytest.mark.asyncio
async def test_runtime_auth_override_does_not_persist(project_id: int) -> None:
    if not _sandbox_configured():
        pytest.skip("Sandbox credentials not configured (ALLURE_ENDPOINT/TOKEN)")

    api_token = os.environ["ALLURE_API_TOKEN"]

    override = await create_test_case(
        project_id=project_id,
        name="Runtime Override First",
        api_token=api_token,
    )
    assert "Created Test Case ID:" in override

    follow_up = await create_test_case(
        project_id=project_id,
        name="Runtime Override Second",
        api_token=api_token,
    )
    assert "Created Test Case ID:" in follow_up


@pytest.mark.asyncio
async def test_runtime_auth_override_missing_token_error(monkeypatch: pytest.MonkeyPatch) -> None:
    if not _sandbox_configured():
        pytest.skip("Sandbox credentials not configured (ALLURE_ENDPOINT/TOKEN)")

    api_token = os.environ["ALLURE_API_TOKEN"]
    monkeypatch.delenv("ALLURE_API_TOKEN", raising=False)

    with pytest.raises(AllureAuthError):
        await create_test_case(project_id=1, name="Missing Token", api_token=None)

    os.environ["ALLURE_API_TOKEN"] = api_token


@pytest.mark.asyncio
async def test_runtime_auth_override_invalid_token(project_id: int) -> None:
    if not _sandbox_configured():
        pytest.skip("Sandbox credentials not configured (ALLURE_ENDPOINT/TOKEN)")

    with pytest.raises(AllureAuthError):
        await create_test_case(project_id=project_id, name="Invalid Token", api_token="invalid")  # noqa: S106
