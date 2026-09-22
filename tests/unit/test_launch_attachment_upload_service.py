"""Unit coverage for the single-replica launch upload capability runtime."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from src.client.exceptions import AllureValidationError
from src.services.launch_attachment_upload_service import (
    LaunchAttachmentUploadConfig,
    LaunchAttachmentUploadRuntime,
    LaunchAttachmentUploadRuntimeHolder,
    LaunchAttachmentUploadService,
)


@pytest.mark.asyncio
async def test_capability_is_opaque_one_use_and_claimed_atomically(tmp_path) -> None:
    runtime = await LaunchAttachmentUploadRuntime.create(
        LaunchAttachmentUploadConfig(temp_parent=tmp_path, max_file_bytes=10, ttl_seconds=60)
    )
    try:
        prepared = await runtime.prepare(launch_id=17, name="evidence.json", content_type="application/json")

        assert len(prepared.handle) >= 32
        assert await runtime.claim(prepared.handle) is not None
        assert await runtime.claim(prepared.handle) is None

        await runtime.complete(prepared.handle)
        assert await runtime.claim(prepared.handle) is None
    finally:
        await runtime.close()


@pytest.mark.asyncio
async def test_capability_expiry_and_metadata_are_enforced(tmp_path) -> None:
    runtime = await LaunchAttachmentUploadRuntime.create(
        LaunchAttachmentUploadConfig(temp_parent=tmp_path, max_file_bytes=10, ttl_seconds=60)
    )
    try:
        with pytest.raises(AllureValidationError, match="filename must be non-empty"):
            await runtime.prepare(launch_id=17, name=" ", content_type="application/json")
        with pytest.raises(AllureValidationError, match="Content type is invalid"):
            await runtime.prepare(launch_id=17, name="evidence.json", content_type="not a type")

        prepared = await runtime.prepare(launch_id=17, name="evidence.json", content_type="application/json")
        runtime._entries[prepared.handle] = runtime._entries[prepared.handle].__class__(
            **{
                **runtime._entries[prepared.handle].__dict__,
                "expires_at": datetime.now(timezone.utc) - timedelta(seconds=1),
            }
        )
        assert await runtime.claim(prepared.handle) is None
    finally:
        await runtime.close()


@pytest.mark.asyncio
async def test_preparation_returns_only_a_public_url_and_bounded_metadata(tmp_path) -> None:
    holder = LaunchAttachmentUploadRuntimeHolder()
    service = LaunchAttachmentUploadService(
        holder=holder,
        config=LaunchAttachmentUploadConfig(temp_parent=tmp_path, max_file_bytes=10, ttl_seconds=60),
    )
    try:
        prepared = await service.prepare(
            launch_id=17,
            name="evidence.json",
            content_type="Application/Json",
            public_base_url="https://lucius.example/",
        )

        assert prepared.upload_url.startswith("https://lucius.example/launch-uploads/")
        assert prepared.max_file_bytes == 10
        assert not hasattr(prepared, "handle")
        handle = prepared.upload_url.rsplit("/", maxsplit=1)[1]
        runtime = await holder.get()
        assert runtime is not None
        entry = await runtime.claim(handle)
        assert entry is not None
        assert entry.content_type == "application/json"
    finally:
        await holder.close()
