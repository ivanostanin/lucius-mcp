"""Unit coverage for the public attachment download preparation tool."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

from src.client.exceptions import AllureValidationError
from src.services.attachment_download_service import PreparedAttachmentDownload
from src.tools.output_schemas import PreparedAttachmentDownloadOutput
from src.utils.telemetry import _apply_mcp_output_contract


@pytest.mark.asyncio
async def test_prepare_attachment_download_validates_then_delegates_and_redacts_private_delivery_state() -> None:
    from src.tools.attachments import prepare_attachment_download

    prepared = PreparedAttachmentDownload(
        download_url="http://127.0.0.1:43210/downloads/opaque-capability",
        expires_at=datetime(2026, 8, 26, 12, 0, tzinfo=timezone.utc),
        filename="evidence.txt",
        content_type="text/plain",
        byte_size=8,
    )
    with (
        patch("src.tools.attachments._attachment_client_context") as client_context,
        patch("src.tools.attachments.AttachmentDownloadService") as service_class,
        patch(
            "src.tools.attachments.attachment_download_runtime.get_attachment_download_public_base_url",
            new=AsyncMock(return_value="http://127.0.0.1:43210"),
        ) as public_base_url,
    ):
        client = MagicMock()
        client_context.return_value.__aenter__ = AsyncMock(return_value=client)
        client_context.return_value.__aexit__ = AsyncMock(return_value=False)
        service_class.return_value.prepare = AsyncMock(return_value=prepared)

        output = await prepare_attachment_download(
            attachment_id=22,
            attachment_kind="test_result",
            test_result_id=10,
            project_id=7,
        )
        plain = await prepare_attachment_download(
            attachment_id=22,
            attachment_kind="test_result",
            test_result_id=10,
            project_id=7,
            output_format="plain",
        )

    validated = _apply_mcp_output_contract(output, PreparedAttachmentDownloadOutput)
    payload = validated.structured_content
    assert payload == {
        "attachment_id": 22,
        "attachment_kind": "test_result",
        "test_result_id": 10,
        "test_case_id": None,
        "download_url": "http://127.0.0.1:43210/downloads/opaque-capability",
        "expires_at": "2026-08-26T12:00:00Z",
        "name": "evidence.txt",
        "content_type": "text/plain",
        "content_length": 8,
    }
    assert "GET" in plain
    assert "one-time" in plain
    assert "Allure bearer token" in plain
    assert "cache" not in str(payload).lower()
    assert "testops" not in str(payload).lower()
    assert client_context.call_args_list == [call(project_id=7), call(project_id=7)]
    public_base_url.assert_not_awaited()
    assert service_class.return_value.prepare.await_count == 2
    request = service_class.return_value.prepare.await_args_list[0].args[0]
    assert request.attachment_id == 22
    assert request.kind.value == "test_result"
    assert request.test_result_id == 10
    assert service_class.return_value.prepare.await_args_list[0].kwargs["public_base_url"].func is public_base_url


@pytest.mark.asyncio
async def test_prepare_attachment_download_rejects_invalid_owner_context_before_client_or_broker_initialization() -> (
    None
):
    from src.tools.attachments import prepare_attachment_download

    with (
        patch("src.tools.attachments._attachment_client_context") as client_context,
        patch("src.tools.attachments.AttachmentDownloadService") as service_class,
        patch(
            "src.tools.attachments.attachment_download_runtime.get_attachment_download_public_base_url", new=AsyncMock()
        ) as public_base_url,
    ):
        with pytest.raises(AllureValidationError, match="Test case context is not valid"):
            await prepare_attachment_download(
                attachment_id=22,
                attachment_kind="test_result",
                test_result_id=10,
                test_case_id=11,
            )
        with pytest.raises(AllureValidationError, match="Attachment ID must be a positive integer"):
            await prepare_attachment_download(
                attachment_id=0,
                attachment_kind="test_case",
                test_case_id=11,
            )

    client_context.assert_not_called()
    service_class.assert_not_called()
    public_base_url.assert_not_awaited()


def test_prepared_attachment_download_output_rejects_private_or_incompatible_public_data() -> None:
    with pytest.raises(ValueError):
        PreparedAttachmentDownloadOutput.model_validate(
            {
                "attachment_id": 22,
                "attachment_kind": "test_case",
                "test_result_id": 10,
                "download_url": "https://lucius.example/downloads/opaque",
                "expires_at": "2026-08-26T12:00:00Z",
                "name": "evidence.txt",
                "content_type": "text/plain",
                "content_length": 8,
                "cache_path": "/private/cache/evidence.txt",
            }
        )
