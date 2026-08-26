"""Unit coverage for the authenticated, one-time attachment download broker."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.applications import Starlette

from src.client.exceptions import AllureNotFoundError, AllureValidationError
from src.services.attachment_download_gateway import LoopbackAttachmentDownloadGateway, attachment_download_route
from src.services.attachment_download_service import (
    AttachmentDownloadConfig,
    AttachmentDownloadRuntimeHolder,
    AttachmentDownloadService,
    AttachmentKind,
    AttachmentPreparationRequest,
)


def _service(
    tmp_path, client: object, holder: AttachmentDownloadRuntimeHolder | None = None
) -> AttachmentDownloadService:
    return AttachmentDownloadService(
        client,
        holder=holder or AttachmentDownloadRuntimeHolder(),
        config=AttachmentDownloadConfig(
            cache_parent=tmp_path,
            max_file_bytes=1024,
            max_entries=2,
            max_total_bytes=2048,
            ttl_seconds=60,
        ),
    )


@pytest.mark.asyncio
async def test_invalid_request_does_not_initialize_or_read_content(tmp_path) -> None:
    client = SimpleNamespace()
    holder = AttachmentDownloadRuntimeHolder()
    service = _service(tmp_path, client, holder)

    with pytest.raises(AllureValidationError, match="Attachment ID"):
        await service.prepare(
            AttachmentPreparationRequest(attachment_id=0, kind=AttachmentKind.TEST_RESULT, test_result_id=1),
            public_base_url="https://downloads.example",
        )

    assert not holder.is_initialized
    assert not any(tmp_path.iterdir())


@pytest.mark.asyncio
async def test_cross_owner_attachment_is_rejected_before_content_or_cache(tmp_path) -> None:
    client = SimpleNamespace(
        list_test_result_attachments=AsyncMock(return_value=SimpleNamespace(content=[SimpleNamespace(id=22)])),
        read_test_result_attachment=AsyncMock(),
    )
    holder = AttachmentDownloadRuntimeHolder()
    service = _service(tmp_path, client, holder)

    with pytest.raises(AllureNotFoundError, match="does not belong"):
        await service.prepare(
            AttachmentPreparationRequest(attachment_id=23, kind=AttachmentKind.TEST_RESULT, test_result_id=1),
            public_base_url="https://downloads.example",
        )

    client.read_test_result_attachment.assert_not_awaited()
    assert not holder.is_initialized
    assert not any(tmp_path.iterdir())


@pytest.mark.asyncio
async def test_verified_attachment_is_cached_once_and_consumed_once(tmp_path) -> None:
    client = SimpleNamespace(
        list_test_result_attachments=AsyncMock(
            return_value=SimpleNamespace(content=[SimpleNamespace(id=23, name="../../unsafe\nevidence.txt")])
        ),
        read_test_result_attachment=AsyncMock(
            return_value=SimpleNamespace(
                data=b"evidence", filename="../../unsafe\nevidence.txt", content_type="text/plain"
            )
        ),
    )
    service = _service(tmp_path, client)

    prepared = await service.prepare(
        AttachmentPreparationRequest(attachment_id=23, kind=AttachmentKind.TEST_RESULT, test_result_id=1),
        public_base_url="https://downloads.example/base/",
    )
    handle = prepared.download_url.rsplit("/", maxsplit=1)[-1]
    claimed = await service.claim(handle)

    assert prepared.download_url.startswith("https://downloads.example/base/downloads/")
    assert prepared.filename == "unsafeevidence.txt"
    assert prepared.content_type == "text/plain"
    assert prepared.byte_size == 8
    assert claimed is not None
    assert claimed.path.read_bytes() == b"evidence"
    assert await service.claim(handle) is None

    await service.complete(handle)
    assert not claimed.path.exists()


@pytest.mark.asyncio
async def test_concurrent_first_verified_preparations_share_one_runtime(tmp_path) -> None:
    client = SimpleNamespace(
        list_test_result_attachments=AsyncMock(
            return_value=SimpleNamespace(content=[SimpleNamespace(id=23, name="evidence.txt")])
        ),
        read_test_result_attachment=AsyncMock(
            return_value=SimpleNamespace(
                data=b"evidence",
                filename="evidence.txt",
                content_type="text/plain",
            )
        ),
    )
    holder = AttachmentDownloadRuntimeHolder()
    service = _service(tmp_path, client, holder)
    request = AttachmentPreparationRequest(attachment_id=23, kind=AttachmentKind.TEST_RESULT, test_result_id=1)

    prepared = await asyncio.gather(
        service.prepare(request, public_base_url="https://downloads.example"),
        service.prepare(request, public_base_url="https://downloads.example"),
    )

    assert holder.initialization_count == 1
    assert len({item.download_url for item in prepared}) == 2
    assert len(list(tmp_path.iterdir())) == 1


@pytest.mark.asyncio
async def test_kind_specific_owner_queries_and_content_readers(tmp_path) -> None:
    client = SimpleNamespace(
        get_test_result_fixture_attachments=AsyncMock(
            return_value=SimpleNamespace(content=[SimpleNamespace(id=31, name="fixture.log")])
        ),
        read_test_result_fixture_attachment=AsyncMock(
            return_value=SimpleNamespace(
                data=b"fixture",
                filename="fixture.log",
                content_type=None,
            )
        ),
        list_test_case_attachments=AsyncMock(
            return_value=SimpleNamespace(content=[SimpleNamespace(id=41, name="case.log")])
        ),
        read_test_case_attachment=AsyncMock(
            return_value=SimpleNamespace(
                data=b"case",
                filename="case.log",
                content_type="text/plain",
            )
        ),
    )
    service = _service(tmp_path, client)

    fixture = await service.prepare(
        AttachmentPreparationRequest(attachment_id=31, kind=AttachmentKind.FIXTURE_RESULT, test_result_id=7),
        public_base_url="https://downloads.example",
    )
    case = await service.prepare(
        AttachmentPreparationRequest(attachment_id=41, kind=AttachmentKind.TEST_CASE, test_case_id=8),
        public_base_url="https://downloads.example",
    )

    client.get_test_result_fixture_attachments.assert_awaited_once_with(7, page=0, size=100)
    client.read_test_result_fixture_attachment.assert_awaited_once_with(31)
    client.list_test_case_attachments.assert_awaited_once_with(8, page=0, size=100)
    client.read_test_case_attachment.assert_awaited_once_with(41)
    assert fixture.content_type == "application/octet-stream"
    assert case.content_type == "text/plain"


@pytest.mark.asyncio
async def test_expired_entries_are_not_claimable_and_are_removed(tmp_path) -> None:
    client = SimpleNamespace(
        list_test_result_attachments=AsyncMock(
            return_value=SimpleNamespace(content=[SimpleNamespace(id=23, name="evidence.txt")])
        ),
        read_test_result_attachment=AsyncMock(
            return_value=SimpleNamespace(
                data=b"evidence",
                filename="evidence.txt",
                content_type="text/plain",
            )
        ),
    )
    service = AttachmentDownloadService(
        client,
        config=AttachmentDownloadConfig(
            cache_parent=tmp_path,
            max_file_bytes=1024,
            max_entries=2,
            max_total_bytes=2048,
            ttl_seconds=0,
        ),
    )
    prepared = await service.prepare(
        AttachmentPreparationRequest(attachment_id=23, kind=AttachmentKind.TEST_RESULT, test_result_id=1),
        public_base_url="https://downloads.example",
    )

    assert await service.claim(prepared.download_url.rsplit("/", maxsplit=1)[-1]) is None
    assert not list(tmp_path.rglob("*.bin"))


@pytest.mark.asyncio
async def test_gateway_streams_a_claimed_entry_once_with_safe_headers(tmp_path) -> None:
    client = SimpleNamespace(
        list_test_result_attachments=AsyncMock(
            return_value=SimpleNamespace(content=[SimpleNamespace(id=23, name="evidence.txt")])
        ),
        read_test_result_attachment=AsyncMock(
            return_value=SimpleNamespace(
                data=b"evidence",
                filename="evidence.txt",
                content_type="text/plain",
            )
        ),
    )
    holder = AttachmentDownloadRuntimeHolder()
    service = _service(tmp_path, client, holder)
    prepared = await service.prepare(
        AttachmentPreparationRequest(attachment_id=23, kind=AttachmentKind.TEST_RESULT, test_result_id=1),
        public_base_url="https://downloads.example",
    )
    app = Starlette(routes=[attachment_download_route(holder)])
    handle = prepared.download_url.rsplit("/", maxsplit=1)[-1]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as http_client:
        response = await http_client.get(f"/downloads/{handle}")
        replay = await http_client.get(f"/downloads/{handle}")

    assert response.status_code == 200
    assert response.content == b"evidence"
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["content-disposition"].startswith("attachment;")
    assert replay.status_code == 404


@pytest.mark.asyncio
async def test_loopback_gateway_stays_live_until_the_one_time_fetch_completes(tmp_path) -> None:
    client = SimpleNamespace(
        list_test_result_attachments=AsyncMock(
            return_value=SimpleNamespace(content=[SimpleNamespace(id=23, name="evidence.txt")])
        ),
        read_test_result_attachment=AsyncMock(
            return_value=SimpleNamespace(
                data=b"evidence",
                filename="evidence.txt",
                content_type="text/plain",
            )
        ),
    )
    holder = AttachmentDownloadRuntimeHolder()
    gateway = LoopbackAttachmentDownloadGateway(holder)
    base_url = await gateway.start()
    service = _service(tmp_path, client, holder)
    try:
        prepared = await service.prepare(
            AttachmentPreparationRequest(attachment_id=23, kind=AttachmentKind.TEST_RESULT, test_result_id=1),
            public_base_url=base_url,
        )
        async with AsyncClient() as http_client:
            response = await http_client.get(prepared.download_url)
            replay = await http_client.get(prepared.download_url)
    finally:
        await gateway.close()

    assert response.status_code == 200
    assert response.content == b"evidence"
    assert replay.status_code == 404
