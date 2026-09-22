"""Configuration checks for HTTP-only launch attachment upload URLs."""

from __future__ import annotations

import pytest
from pytest_mock import MockerFixture

from src.client.exceptions import AllureValidationError
from src.services.launch_attachment_upload_runtime import get_launch_attachment_upload_public_base_url
from src.utils.config import settings


@pytest.mark.asyncio
async def test_push_upload_requires_external_https_url(mocker: MockerFixture) -> None:
    mocker.patch.object(settings, "MCP_MODE", "http")
    for value in (None, "http://lucius.example", "https://localhost:8000", "https://127.0.0.1:8000"):
        mocker.patch.object(settings, "LAUNCH_ATTACHMENT_UPLOAD_PUBLIC_BASE_URL", value)
        with pytest.raises(AllureValidationError):
            await get_launch_attachment_upload_public_base_url()


@pytest.mark.asyncio
async def test_push_upload_returns_normalized_external_https_url(mocker: MockerFixture) -> None:
    mocker.patch.object(settings, "MCP_MODE", "http")
    mocker.patch.object(settings, "LAUNCH_ATTACHMENT_UPLOAD_PUBLIC_BASE_URL", "https://lucius.example/")

    assert await get_launch_attachment_upload_public_base_url() == "https://lucius.example"


@pytest.mark.asyncio
async def test_push_upload_is_unavailable_from_stdio(mocker: MockerFixture) -> None:
    mocker.patch.object(settings, "MCP_MODE", "stdio")
    with pytest.raises(AllureValidationError, match="persistent HTTP MCP server"):
        await get_launch_attachment_upload_public_base_url()
