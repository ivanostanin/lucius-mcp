"""Starlette route for one-use raw launch-attachment uploads."""

from __future__ import annotations

import asyncio
import os
import secrets
from collections.abc import Awaitable, Callable
from pathlib import Path

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from src.client.exceptions import AllureAPIError, AllureValidationError
from src.services.launch_attachment_service import LaunchAttachmentSummary
from src.services.launch_attachment_upload_service import (
    LaunchAttachmentUploadRuntimeHolder,
)

Attach = Callable[[int, str, bytes], Awaitable[LaunchAttachmentSummary]]


class _PayloadTooLargeError(Exception):
    """Internal signal for a bounded raw upload stream."""


def launch_attachment_upload_route(
    holder: LaunchAttachmentUploadRuntimeHolder,
    *,
    attach: Attach | None = None,
) -> Route:
    """Create the lazy raw-upload route that precedes the FastMCP mount."""

    async def upload(request: Request) -> Response:
        runtime = await holder.get()
        if runtime is None:
            return Response(status_code=404, headers={"Cache-Control": "no-store"})
        entry = await runtime.claim(request.path_params["handle"])
        if entry is None:
            return Response(status_code=404, headers={"Cache-Control": "no-store"})
        try:
            if _request_content_type(request) != entry.content_type:
                return Response(status_code=400, headers={"Cache-Control": "no-store"})
            path = runtime.temp_root / f"{secrets.token_hex(24)}.upload"
            try:
                content = await _store_and_read_bounded(request, path, runtime.max_file_bytes)
                summary = await (attach or _attach_with_configured_client)(entry.launch_id, entry.name, content)
            finally:
                await asyncio.to_thread(path.unlink, missing_ok=True)
            return JSONResponse(
                {
                    "id": summary.id,
                    "name": summary.name,
                    "content_type": summary.content_type,
                    "content_length": summary.content_length,
                },
                status_code=201,
                headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
            )
        except _PayloadTooLargeError:
            return Response(status_code=413, headers={"Cache-Control": "no-store"})
        except (AllureValidationError, AllureAPIError, OSError):
            return Response(status_code=422, headers={"Cache-Control": "no-store"})
        except Exception:
            return Response(status_code=500, headers={"Cache-Control": "no-store"})
        finally:
            await runtime.complete(entry.handle)

    return Route("/launch-uploads/{handle}", upload, methods=["POST"])


def _request_content_type(request: Request) -> str | None:
    value = request.headers.get("content-type")
    return None if value is None else value.split(";", maxsplit=1)[0].strip().lower()


async def _store_and_read_bounded(request: Request, path: Path, max_file_bytes: int) -> bytes:
    written = 0
    file = await asyncio.to_thread(path.open, "xb")
    try:
        await asyncio.to_thread(os.chmod, path, 0o600)
        async for chunk in request.stream():
            if not isinstance(chunk, bytes):
                raise AllureValidationError("Launch attachment upload stream is invalid")
            written += len(chunk)
            if written > max_file_bytes:
                raise _PayloadTooLargeError
            await asyncio.to_thread(file.write, chunk)
        await asyncio.to_thread(file.flush)
    finally:
        await asyncio.to_thread(file.close)
    return await _read_bounded(path, max_file_bytes)


async def _read_bounded(path: Path, max_file_bytes: int) -> bytes:
    file = await asyncio.to_thread(path.open, "rb")
    try:
        chunks: list[bytes] = []
        total = 0
        while chunk := await asyncio.to_thread(file.read, 64 * 1024):
            total += len(chunk)
            if total > max_file_bytes:
                raise _PayloadTooLargeError
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        await asyncio.to_thread(file.close)


async def _attach_with_configured_client(launch_id: int, name: str, content: bytes) -> LaunchAttachmentSummary:
    """Authenticate only after a capability was claimed and its stream was bounded."""
    from src.client import AllureClient
    from src.services.launch_attachment_service import LaunchAttachmentService

    async with AllureClient.from_env(require_project=False) as client:
        return await LaunchAttachmentService(client).attach(launch_id, name, content)


__all__ = ["launch_attachment_upload_route"]
