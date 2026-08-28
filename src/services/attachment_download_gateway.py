"""Starlette adapter for the transport-independent attachment download broker."""

from __future__ import annotations

import asyncio
import socket
from collections.abc import Awaitable, Callable, Mapping, Sequence
from os import PathLike
from pathlib import Path

from starlette.requests import Request
from starlette.responses import FileResponse, Response
from starlette.routing import Route
from starlette.types import Receive, Scope, Send

from src.client.exceptions import AllureValidationError
from src.services.attachment_download_service import AttachmentDownloadRuntimeHolder


class _CleanupFileResponse(FileResponse):
    """Run capability cleanup even when file streaming raises or is cancelled."""

    def __init__(
        self,
        path: str | PathLike[str],
        *,
        cleanup: Callable[[], Awaitable[None]],
        media_type: str,
        filename: str,
        content_disposition_type: str,
        headers: Mapping[str, str],
    ) -> None:
        super().__init__(
            path,
            media_type=media_type,
            filename=filename,
            content_disposition_type=content_disposition_type,
            headers=headers,
        )
        self._cleanup = cleanup

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        try:
            await super().__call__(scope, receive, send)
        finally:
            await self._cleanup()


def attachment_download_route(holder: AttachmentDownloadRuntimeHolder) -> Route:
    """Create a lazy GET route without allocating broker state during registration."""

    async def download(request: Request) -> Response:
        runtime = await holder.get()
        if runtime is None:
            return Response(status_code=404)
        handle = request.path_params["handle"]
        entry = await runtime.claim(handle)
        if entry is None:
            return Response(status_code=404)
        return _CleanupFileResponse(
            entry.path,
            media_type=entry.content_type,
            filename=entry.filename,
            content_disposition_type="attachment",
            headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
            cleanup=lambda: runtime.complete(entry.handle),
        )

    return Route("/downloads/{handle}", download, methods=["GET"])


class LoopbackAttachmentDownloadGateway:
    """A small persistent-stdio gateway that never imports HTTP code from ``src.cli``."""

    def __init__(self, holder: AttachmentDownloadRuntimeHolder) -> None:
        self._holder = holder
        self._server: asyncio.AbstractServer | None = None
        self._base_url: str | None = None
        self._lock = asyncio.Lock()

    @property
    def base_url(self) -> str:
        if self._base_url is None:
            raise AllureValidationError("Loopback attachment gateway has not started")
        return self._base_url

    async def start(self) -> str:
        """Bind one ephemeral loopback port and wait until it is accepting connections."""
        async with self._lock:
            if self._server is not None:
                return self.base_url
            try:
                server = await asyncio.start_server(self._handle_connection, host="127.0.0.1", port=0)
            except OSError as exc:
                raise AllureValidationError(
                    "Lucius could not start its local attachment delivery gateway",
                    suggestions=["Check that loopback networking is available on this host"],
                ) from exc
            sockets: Sequence[socket.socket] = server.sockets or []
            if not sockets:  # pragma: no cover - asyncio guarantees a socket after a successful bind
                server.close()
                await server.wait_closed()
                raise AllureValidationError("Lucius local attachment gateway did not report a bound port")
            address = sockets[0].getsockname()
            if not isinstance(address, tuple) or not isinstance(address[1], int):  # pragma: no cover - IPv4 bind above
                server.close()
                await server.wait_closed()
                raise AllureValidationError("Lucius local attachment gateway returned an unsupported address")
            self._server = server
            self._base_url = f"http://127.0.0.1:{address[1]}"
            return self._base_url

    async def close(self) -> None:
        """Stop accepting local delivery requests; broker cleanup remains lifecycle-owned."""
        async with self._lock:
            if self._server is None:
                return
            server = self._server
            self._server = None
            self._base_url = None
        server.close()
        await server.wait_closed()

    async def _handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            request = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), timeout=10)
            request_line = request.split(b"\r\n", maxsplit=1)[0].decode("ascii", errors="ignore")
            parts = request_line.split(" ")
            if len(parts) != 3 or parts[0] != "GET" or not parts[1].startswith("/downloads/"):
                await self._write_status(writer, 404)
                return
            handle = parts[1].removeprefix("/downloads/")
            if "/" in handle or "?" in handle:
                await self._write_status(writer, 404)
                return
            runtime = await self._holder.get()
            entry = None if runtime is None else await runtime.claim(handle)
            if entry is None or runtime is None:
                await self._write_status(writer, 404)
                return
            try:
                await self._write_attachment(writer, entry.path, entry.filename, entry.content_type, entry.byte_size)
            finally:
                await runtime.complete(entry.handle)
        except (asyncio.IncompleteReadError, asyncio.LimitOverrunError, TimeoutError):
            await self._write_status(writer, 404)
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except (ConnectionError, OSError):
                pass

    @staticmethod
    async def _write_status(writer: asyncio.StreamWriter, status: int) -> None:
        response = (
            f"HTTP/1.1 {status} Not Found\r\nContent-Length: 0\r\nCache-Control: no-store\r\nConnection: close\r\n\r\n"
        )
        writer.write(response.encode())
        await writer.drain()

    @staticmethod
    async def _write_attachment(
        writer: asyncio.StreamWriter,
        path: Path,
        filename: str,
        content_type: str,
        byte_size: int,
    ) -> None:
        headers = (
            "HTTP/1.1 200 OK\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Content-Length: {byte_size}\r\n"
            f'Content-Disposition: attachment; filename="{filename}"\r\n'
            "Cache-Control: no-store\r\n"
            "X-Content-Type-Options: nosniff\r\n"
            "Connection: close\r\n\r\n"
        )
        writer.write(headers.encode("ascii"))
        await writer.drain()
        file = await asyncio.to_thread(path.open, "rb")
        try:
            while chunk := await asyncio.to_thread(file.read, 64 * 1024):
                writer.write(chunk)
                await writer.drain()
        finally:
            await asyncio.to_thread(file.close)


__all__ = ["LoopbackAttachmentDownloadGateway", "attachment_download_route"]
