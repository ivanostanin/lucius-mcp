"""Unit coverage for the public launch attachment transfer tool."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.client.exceptions import AllureValidationError
from src.services.launch_attachment_service import LaunchAttachmentSummary
from src.services.launch_attachment_upload_service import PreparedLaunchAttachmentUpload
from src.tools.output_schemas import AttachFileToLaunchOutput
from src.utils.telemetry import _apply_mcp_output_contract


@pytest.mark.asyncio
async def test_attach_file_to_launch_push_prepares_a_redacted_one_use_url() -> None:
    from src.tools.launches import attach_file_to_launch

    prepared = PreparedLaunchAttachmentUpload(
        upload_url="https://lucius.example/launch-uploads/opaque-capability",
        expires_at=datetime(2026, 9, 22, 12, 0, tzinfo=timezone.utc),
        max_file_bytes=1024,
    )
    with (
        patch("src.tools.launches._launch_client_context") as client_context,
        patch(
            "src.tools.launches.LaunchAttachmentUploadService.prepare", new=AsyncMock(return_value=prepared)
        ) as prepare,
    ):
        output = await attach_file_to_launch(
            launch_id=17,
            name="evidence.json",
            transfer_mode="push",
            content_type="application/json",
        )

    payload = _apply_mcp_output_contract(output, AttachFileToLaunchOutput).structured_content
    assert payload == {
        "state": "awaiting_upload",
        "launch_id": 17,
        "name": "evidence.json",
        "content_type": "application/json",
        "upload_url": "https://lucius.example/launch-uploads/opaque-capability",
        "upload_method": "POST",
        "expires_at": "2026-09-22T12:00:00Z",
        "max_file_bytes": 1024,
        "attachment": None,
    }
    client_context.assert_not_called()
    prepare.assert_awaited_once()


@pytest.mark.asyncio
async def test_attach_file_to_launch_pull_delegates_secure_import_to_service() -> None:
    from src.tools.launches import attach_file_to_launch

    summary = LaunchAttachmentSummary(id=99, name="evidence.json", content_type="application/json", content_length=2)
    with (
        patch("src.tools.launches._launch_client_context") as client_context,
        patch("src.tools.launches.LaunchAttachmentService") as service_class,
    ):
        client = MagicMock()
        client_context.return_value.__aenter__ = AsyncMock(return_value=client)
        client_context.return_value.__aexit__ = AsyncMock(return_value=False)
        service_class.return_value.attach_from_path = AsyncMock(return_value=summary)

        output = await attach_file_to_launch(
            launch_id=17,
            name="evidence.json",
            transfer_mode="pull",
            source_path="evidence.json",
            project_id=7,
        )

    payload = _apply_mcp_output_contract(output, AttachFileToLaunchOutput).structured_content
    assert payload["state"] == "attached"
    assert payload["attachment"] == {
        "id": 99,
        "name": "evidence.json",
        "content_type": "application/json",
        "content_length": 2,
    }
    assert payload["upload_url"] is None
    client_context.assert_called_once_with(project_id=7)
    service_class.return_value.attach_from_path.assert_awaited_once()


@pytest.mark.asyncio
async def test_attach_file_to_launch_rejects_invalid_mode_specific_inputs() -> None:
    from src.tools.launches import attach_file_to_launch

    with pytest.raises(AllureValidationError, match="require content_type"):
        await attach_file_to_launch(launch_id=17, name="evidence.json")
    with pytest.raises(AllureValidationError, match="require source_path"):
        await attach_file_to_launch(launch_id=17, name="evidence.json", transfer_mode="pull")


def test_attach_file_to_launch_output_rejects_mixed_states() -> None:
    with pytest.raises(ValueError):
        AttachFileToLaunchOutput.model_validate(
            {
                "state": "attached",
                "launch_id": 17,
                "name": "evidence.json",
                "upload_url": "https://lucius.example/launch-uploads/opaque",
                "attachment": {"id": 99, "name": "evidence.json"},
            }
        )
