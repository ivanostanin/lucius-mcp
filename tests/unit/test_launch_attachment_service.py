"""Unit coverage for native launch-attachment service behavior."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.client.exceptions import AllureNotFoundError, AllureValidationError, LaunchNotFoundError
from src.client.generated.models.launch_attachment_row_dto import LaunchAttachmentRowDto
from src.services.launch_attachment_service import LaunchAttachmentService


def _native_attachment_row(
    *, name: str = "evidence.bin", content_type: str = "application/octet-stream"
) -> LaunchAttachmentRowDto:
    return LaunchAttachmentRowDto.model_construct(
        id=88,
        name=name,
        content_type=content_type,
        content_length=2,
        entity="launch",
    )


@pytest.mark.asyncio
async def test_attach_maps_native_row_to_safe_application_summary() -> None:
    client = MagicMock()
    client.create_launch_attachment = AsyncMock(
        return_value=[_native_attachment_row(name="evidence.json", content_type="application/json")]
    )
    service = LaunchAttachmentService(client)

    summary = await service.attach(17, "evidence.json", b"{}")

    assert summary.id == 88
    assert summary.name == "evidence.json"
    assert summary.content_type == "application/json"
    assert summary.content_length == 2
    client.create_launch_attachment.assert_awaited_once_with(17, ("evidence.json", b"{}"))


@pytest.mark.asyncio
async def test_attach_rejects_invalid_metadata_before_client_call() -> None:
    client = MagicMock()
    service = LaunchAttachmentService(client)

    with pytest.raises(AllureValidationError, match="Launch ID must be a positive integer"):
        await service.attach(0, "evidence.txt", b"x")
    with pytest.raises(AllureValidationError, match="Attachment filename must be non-empty"):
        await service.attach(17, " ", b"x")

    client.create_launch_attachment.assert_not_called()


@pytest.mark.asyncio
async def test_attach_translates_missing_launch_without_raw_upstream_detail() -> None:
    client = MagicMock()
    client.create_launch_attachment = AsyncMock(
        side_effect=AllureNotFoundError("launch unavailable at upstream URL", status_code=404)
    )
    service = LaunchAttachmentService(client)

    with pytest.raises(LaunchNotFoundError) as error:
        await service.attach(17, "evidence.txt", b"x")

    assert "upstream URL" not in str(error.value)


@pytest.mark.asyncio
async def test_attach_from_path_reads_a_regular_file_beneath_import_root(tmp_path: Path) -> None:
    import_root = tmp_path / "imports"
    import_root.mkdir()
    source = import_root / "evidence.json"
    source.write_bytes(b"{}")
    client = MagicMock()
    client.create_launch_attachment = AsyncMock(return_value=[_native_attachment_row(content_type="application/json")])

    summary = await LaunchAttachmentService(client).attach_from_path(
        17,
        "evidence.json",
        source,
        import_root=import_root,
        max_file_bytes=2,
    )

    assert summary.content_type == "application/json"
    client.create_launch_attachment.assert_awaited_once_with(17, ("evidence.json", b"{}"))
    assert source.read_bytes() == b"{}"


@pytest.mark.asyncio
@pytest.mark.parametrize("source_name", ["../outside.txt", "link.txt", "linked/nested.txt"])
async def test_attach_from_path_rejects_traversal_and_symlinks(tmp_path: Path, source_name: str) -> None:
    import_root = tmp_path / "imports"
    import_root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("secret")
    if source_name == "link.txt":
        os.symlink(outside, import_root / source_name)
    if source_name == "linked/nested.txt":
        outside_parent = tmp_path / "outside-parent"
        outside_parent.mkdir()
        (outside_parent / "nested.txt").write_text("secret")
        os.symlink(outside_parent, import_root / "linked")
    client = MagicMock()
    service = LaunchAttachmentService(client)

    with pytest.raises(AllureValidationError, match=r"outside|symlink"):
        await service.attach_from_path(
            17,
            "evidence.txt",
            source_name,
            import_root=import_root,
            max_file_bytes=1024,
        )

    client.create_launch_attachment.assert_not_called()


@pytest.mark.asyncio
async def test_attach_from_path_rejects_invalid_supplied_content_type_before_reading(tmp_path: Path) -> None:
    import_root = tmp_path / "imports"
    import_root.mkdir()
    client = MagicMock()

    with pytest.raises(AllureValidationError, match="valid media type"):
        await LaunchAttachmentService(client).attach_from_path(
            17,
            "evidence.txt",
            "missing.txt",
            import_root=import_root,
            max_file_bytes=1024,
            content_type="not a media type",
        )

    client.create_launch_attachment.assert_not_called()


@pytest.mark.asyncio
async def test_attach_from_path_rejects_non_regular_files_before_client_call(tmp_path: Path) -> None:
    import_root = tmp_path / "imports"
    import_root.mkdir()
    (import_root / "directory").mkdir()
    client = MagicMock()
    service = LaunchAttachmentService(client)

    with pytest.raises(AllureValidationError, match="regular file"):
        await service.attach_from_path(
            17,
            "directory",
            "directory",
            import_root=import_root,
            max_file_bytes=1024,
        )

    client.create_launch_attachment.assert_not_called()


@pytest.mark.asyncio
async def test_attach_from_path_infers_unknown_extension_as_octet_stream(tmp_path: Path, mocker) -> None:
    import_root = tmp_path / "imports"
    import_root.mkdir()
    (import_root / "evidence.unknown").write_bytes(b"{}")
    client = MagicMock()
    client.create_launch_attachment = AsyncMock(return_value=[_native_attachment_row()])
    guess_type = mocker.patch("src.services.launch_attachment_service.mimetypes.guess_type", return_value=(None, None))

    summary = await LaunchAttachmentService(client).attach_from_path(
        17,
        "evidence.unknown",
        "evidence.unknown",
        import_root=import_root,
        max_file_bytes=2,
    )

    assert summary.content_type == "application/octet-stream"
    guess_type.assert_called_once_with("evidence.unknown")


@pytest.mark.asyncio
async def test_attach_from_path_enforces_the_limit_before_client_call(tmp_path: Path) -> None:
    import_root = tmp_path / "imports"
    import_root.mkdir()
    (import_root / "large.bin").write_bytes(b"abc")
    client = MagicMock()
    service = LaunchAttachmentService(client)

    with pytest.raises(AllureValidationError, match="configured attachment file limit"):
        await service.attach_from_path(
            17,
            "large.bin",
            "large.bin",
            import_root=import_root,
            max_file_bytes=2,
        )

    client.create_launch_attachment.assert_not_called()
