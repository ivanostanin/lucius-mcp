"""ASGI coverage for one-time raw launch-attachment uploads."""

from __future__ import annotations

import httpx
import pytest
from starlette.applications import Starlette

from src.services.launch_attachment_service import LaunchAttachmentSummary
from src.services.launch_attachment_upload_gateway import launch_attachment_upload_route
from src.services.launch_attachment_upload_service import (
    LaunchAttachmentUploadConfig,
    LaunchAttachmentUploadRuntimeHolder,
)


@pytest.mark.asyncio
async def test_gateway_consumes_capability_once_and_returns_only_safe_summary(tmp_path) -> None:
    holder = LaunchAttachmentUploadRuntimeHolder()
    runtime = await holder.get_or_create(
        LaunchAttachmentUploadConfig(temp_parent=tmp_path, max_file_bytes=10, ttl_seconds=60)
    )
    prepared = await runtime.prepare(launch_id=17, name="evidence.json", content_type="application/json")
    received: list[tuple[int, str, bytes]] = []

    async def attach(launch_id: int, name: str, content: bytes) -> LaunchAttachmentSummary:
        received.append((launch_id, name, content))
        return LaunchAttachmentSummary(id=99, name=name, content_type="application/json", content_length=len(content))

    app = Starlette(routes=[launch_attachment_upload_route(holder, attach=attach)])
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="https://lucius.example") as client:
            response = await client.post(
                f"/launch-uploads/{prepared.handle}",
                content=b"{}",
                headers={"Content-Type": "application/json"},
            )
            replay = await client.post(
                f"/launch-uploads/{prepared.handle}",
                content=b"{}",
                headers={"Content-Type": "application/json"},
            )

        assert response.status_code == 201
        assert response.json() == {
            "id": 99,
            "name": "evidence.json",
            "content_type": "application/json",
            "content_length": 2,
        }
        assert received == [(17, "evidence.json", b"{}")]
        assert replay.status_code == 404
    finally:
        await holder.close()


@pytest.mark.asyncio
async def test_gateway_rejects_wrong_type_and_oversize_without_upstream_upload(tmp_path) -> None:
    holder = LaunchAttachmentUploadRuntimeHolder()
    runtime = await holder.get_or_create(
        LaunchAttachmentUploadConfig(temp_parent=tmp_path, max_file_bytes=1, ttl_seconds=60)
    )
    wrong_type = await runtime.prepare(launch_id=17, name="evidence.json", content_type="application/json")
    too_large = await runtime.prepare(launch_id=17, name="evidence.json", content_type="application/json")

    async def attach(_: int, __: str, ___: bytes) -> LaunchAttachmentSummary:
        raise AssertionError("The gateway must reject invalid payloads before the upstream upload")

    app = Starlette(routes=[launch_attachment_upload_route(holder, attach=attach)])
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="https://lucius.example") as client:
            wrong = await client.post(
                f"/launch-uploads/{wrong_type.handle}", content=b"x", headers={"Content-Type": "text/plain"}
            )
            oversized = await client.post(
                f"/launch-uploads/{too_large.handle}", content=b"xx", headers={"Content-Type": "application/json"}
            )

        assert wrong.status_code == 400
        assert oversized.status_code == 413
    finally:
        await holder.close()
