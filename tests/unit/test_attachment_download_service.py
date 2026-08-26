"""Unit coverage for the authenticated, one-time attachment download broker."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.applications import Starlette
from starlette.requests import Request

from src.client.exceptions import AllureNotFoundError, AllureValidationError
from src.services.attachment_download_gateway import LoopbackAttachmentDownloadGateway, attachment_download_route
from src.services.attachment_download_service import (
    AttachmentDownloadConfig,
    AttachmentDownloadRuntime,
    AttachmentDownloadRuntimeHolder,
    AttachmentDownloadService,
    AttachmentKind,
    AttachmentPreparationRequest,
    _validate_public_base_url,
)


def _install_streaming_fakes(client: object) -> None:
    """Adapt legacy byte-reader mocks to the broker's bounded stream contract."""

    for stream_name, reader_name in (
        ("stream_test_result_attachment", "read_test_result_attachment"),
        ("stream_test_result_fixture_attachment", "read_test_result_fixture_attachment"),
        ("stream_test_case_attachment", "read_test_case_attachment"),
    ):
        reader = getattr(client, reader_name, None)
        if reader is None:
            continue

        @asynccontextmanager
        async def stream(attachment_id: int, *, inline: bool = False, reader=reader):
            content = await reader(attachment_id, inline=inline)

            async def chunks():
                yield content.data

            yield SimpleNamespace(
                filename=content.filename,
                content_type=content.content_type,
                content_length=len(content.data),
                iter_bytes=chunks,
            )

        setattr(client, stream_name, stream)


def _service(
    tmp_path, client: object, holder: AttachmentDownloadRuntimeHolder | None = None
) -> AttachmentDownloadService:
    _install_streaming_fakes(client)
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
    client.read_test_result_fixture_attachment.assert_awaited_once_with(31, inline=False)
    client.list_test_case_attachments.assert_awaited_once_with(8, page=0, size=100)
    client.read_test_case_attachment.assert_awaited_once_with(41, inline=False)
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
    _install_streaming_fakes(client)
    prepared = await service.prepare(
        AttachmentPreparationRequest(attachment_id=23, kind=AttachmentKind.TEST_RESULT, test_result_id=1),
        public_base_url="https://downloads.example",
    )

    assert await service.claim(prepared.download_url.rsplit("/", maxsplit=1)[-1]) is None
    assert not list(tmp_path.rglob("*.bin"))


@pytest.mark.asyncio
async def test_streaming_rejects_over_limit_content_without_a_declared_size(tmp_path) -> None:
    @asynccontextmanager
    async def oversized_stream(_attachment_id: int, *, inline: bool = False):
        async def chunks():
            yield b"a" * 600
            yield b"b" * 500

        yield SimpleNamespace(
            filename="evidence.bin",
            content_type="application/octet-stream",
            content_length=None,
            iter_bytes=chunks,
        )

    client = SimpleNamespace(
        list_test_result_attachments=AsyncMock(
            return_value=SimpleNamespace(content=[SimpleNamespace(id=23, name="evidence.bin")])
        ),
        stream_test_result_attachment=oversized_stream,
    )
    service = _service(tmp_path, client)

    with pytest.raises(AllureValidationError, match="file limit"):
        await service.prepare(
            AttachmentPreparationRequest(attachment_id=23, kind=AttachmentKind.TEST_RESULT, test_result_id=1),
            public_base_url="https://downloads.example",
        )

    assert not list(tmp_path.rglob("*.bin"))


@pytest.mark.asyncio
async def test_misleading_content_length_cannot_overcommit_the_total_cache_budget(tmp_path) -> None:
    runtime = await AttachmentDownloadRuntime.create(
        AttachmentDownloadConfig(
            cache_parent=tmp_path,
            max_file_bytes=1024,
            max_entries=2,
            max_total_bytes=1024,
            ttl_seconds=60,
        )
    )
    first_started = asyncio.Event()
    release_first = asyncio.Event()

    async def blocked_chunks():
        first_started.set()
        await release_first.wait()
        yield b"a" * 1024

    async def full_chunks():
        yield b"b" * 1024

    first_store = asyncio.create_task(
        runtime.store_stream(
            filename="first.bin",
            content_type="application/octet-stream",
            content_length=1,
            chunks=blocked_chunks(),
        )
    )
    try:
        await first_started.wait()
        with pytest.raises(AllureValidationError, match="remaining download cache budget"):
            await runtime.store_stream(
                filename="second.bin",
                content_type="application/octet-stream",
                content_length=1,
                chunks=full_chunks(),
            )
    finally:
        release_first.set()
        await first_store
        await runtime.close()


def test_public_base_url_rejects_unusable_addresses_and_suffixes() -> None:
    for base_url in ("http://[::]:8000", "https://downloads.example/base?proxy=true", "https://downloads.example/#x"):
        with pytest.raises(AllureValidationError, match="reachable public base URL"):
            _validate_public_base_url(base_url)


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
async def test_interrupted_starlette_response_releases_the_claimed_entry(tmp_path) -> None:
    client = SimpleNamespace(
        list_test_result_attachments=AsyncMock(
            return_value=SimpleNamespace(content=[SimpleNamespace(id=23, name="evidence.txt")])
        ),
        read_test_result_attachment=AsyncMock(
            return_value=SimpleNamespace(data=b"evidence", filename="evidence.txt", content_type="text/plain")
        ),
    )
    holder = AttachmentDownloadRuntimeHolder()
    service = _service(tmp_path, client, holder)
    prepared = await service.prepare(
        AttachmentPreparationRequest(attachment_id=23, kind=AttachmentKind.TEST_RESULT, test_result_id=1),
        public_base_url="https://downloads.example",
    )
    handle = prepared.download_url.rsplit("/", maxsplit=1)[-1]
    route = attachment_download_route(holder)
    scope = {
        "type": "http",
        "method": "GET",
        "path": f"/downloads/{handle}",
        "raw_path": f"/downloads/{handle}".encode(),
        "root_path": "",
        "scheme": "http",
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 1234),
        "server": ("testserver", 80),
        "extensions": {},
        "path_params": {"handle": handle},
    }
    response = await route.endpoint(Request(scope))

    async def receive() -> dict[str, str]:
        return {"type": "http.disconnect"}

    async def failing_send(message: dict[str, object]) -> None:
        if message["type"] == "http.response.body":
            raise RuntimeError("connection dropped")

    with pytest.raises(RuntimeError, match="connection dropped"):
        await response(scope, receive, failing_send)

    assert not list(tmp_path.rglob("*.bin"))
    await holder.close()


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


@pytest.mark.asyncio
async def test_concurrent_loopback_start_uses_one_listener(mocker) -> None:
    holder = AttachmentDownloadRuntimeHolder()
    gateway = LoopbackAttachmentDownloadGateway(holder)
    original_start_server = asyncio.start_server
    first_start_entered = asyncio.Event()
    release_start = asyncio.Event()
    start_calls = 0

    async def delayed_start_server(*args, **kwargs):
        nonlocal start_calls
        start_calls += 1
        first_start_entered.set()
        await release_start.wait()
        return await original_start_server(*args, **kwargs)

    mocker.patch("src.services.attachment_download_gateway.asyncio.start_server", side_effect=delayed_start_server)
    first = asyncio.create_task(gateway.start())
    await first_start_entered.wait()
    second = asyncio.create_task(gateway.start())
    await asyncio.sleep(0)
    release_start.set()

    try:
        assert len(set(await asyncio.gather(first, second))) == 1
        assert start_calls == 1
    finally:
        await gateway.close()


@pytest.mark.asyncio
async def test_holder_does_not_reinitialize_after_shutdown(tmp_path) -> None:
    holder = AttachmentDownloadRuntimeHolder()
    config = AttachmentDownloadConfig(
        cache_parent=tmp_path,
        max_file_bytes=1024,
        max_entries=1,
        max_total_bytes=1024,
        ttl_seconds=60,
    )
    await holder.get_or_create(config)
    await holder.close()

    with pytest.raises(AllureValidationError, match="shutting down"):
        await holder.get_or_create(config)
