"""Authenticated, one-time attachment delivery without exposing Allure credentials."""

from __future__ import annotations

import asyncio
import os
import re
import secrets
import tempfile
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Protocol
from urllib.parse import urlsplit

from src.client import AllureClient
from src.client.exceptions import AllureNotFoundError, AllureValidationError
from src.utils.config import settings

DEFAULT_MAX_FILE_BYTES = 100 * 1024 * 1024
DEFAULT_MAX_ENTRIES = 32
DEFAULT_MAX_TOTAL_BYTES = 512 * 1024 * 1024
DEFAULT_TTL_SECONDS = 300
_HANDLE_PATTERN = re.compile(r"^[A-Za-z0-9_-]{32,}$")
_CONTENT_TYPE_PATTERN = re.compile(r"^[A-Za-z0-9!#$&^_.+-]+/[A-Za-z0-9!#$&^_.+-]+$")
_UNSPECIFIED_HOST = ".".join(("0",) * 4)


class AttachmentKind(str, Enum):
    """Upstream attachment collections that can safely be prepared."""

    TEST_RESULT = "test_result"
    FIXTURE_RESULT = "fixture_result"
    TEST_CASE = "test_case"


@dataclass(frozen=True)
class AttachmentPreparationRequest:
    """Caller-supplied IDs used to establish an attachment's ownership."""

    attachment_id: int
    kind: AttachmentKind
    test_result_id: int | None = None
    test_case_id: int | None = None

    def validate(self) -> None:
        _validate_positive(self.attachment_id, "Attachment ID")
        if self.kind in (AttachmentKind.TEST_RESULT, AttachmentKind.FIXTURE_RESULT):
            _validate_positive(self.test_result_id, "Test Result ID")
            if self.test_case_id is not None:
                raise AllureValidationError("Test case context is not valid for result attachments")
        elif self.kind is AttachmentKind.TEST_CASE:
            _validate_positive(self.test_case_id, "Test Case ID")
            if self.test_result_id is not None:
                raise AllureValidationError("Test result context is not valid for test-case attachments")
        else:  # pragma: no cover - protects callers that bypass enum validation
            raise AllureValidationError("Attachment kind must be test_result, fixture_result, or test_case")


@dataclass(frozen=True)
class AttachmentDownloadConfig:
    """Bounded private-cache settings; directories are created only on first use."""

    cache_parent: Path
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES
    max_entries: int = DEFAULT_MAX_ENTRIES
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES
    ttl_seconds: int = DEFAULT_TTL_SECONDS

    def validate(self) -> None:
        for value, name in (
            (self.max_file_bytes, "Attachment download file limit"),
            (self.max_entries, "Attachment download entry limit"),
            (self.max_total_bytes, "Attachment download byte limit"),
            (self.ttl_seconds, "Attachment download TTL"),
        ):
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise AllureValidationError(f"{name} must be a non-negative integer")
        if self.max_total_bytes < self.max_file_bytes:
            raise AllureValidationError("Attachment download byte limit cannot be lower than the file limit")


@dataclass(frozen=True)
class PreparedAttachmentDownload:
    """Safe broker output intended for the future public preparation tool."""

    download_url: str
    expires_at: datetime
    filename: str
    content_type: str
    byte_size: int


@dataclass(frozen=True)
class CachedAttachmentDownload:
    """Internal gateway record; this is never returned through MCP."""

    handle: str
    path: Path
    filename: str
    content_type: str
    byte_size: int
    expires_at: datetime


@dataclass(frozen=True)
class _VerifiedAttachment:
    attachment_id: int
    kind: AttachmentKind
    filename: str
    content_type: str
    declared_size: int | None


class _AttachmentContentStream(Protocol):
    @property
    def filename(self) -> str: ...

    @property
    def content_type(self) -> str: ...

    @property
    def content_length(self) -> int | None: ...

    def iter_bytes(self) -> AsyncIterator[bytes]: ...


class _DownloadClient(Protocol):
    async def list_test_result_attachments(self, test_result_id: int, *, page: int, size: int) -> object: ...

    async def get_test_result_fixture_attachments(self, test_result_id: int, *, page: int, size: int) -> object: ...

    async def list_test_case_attachments(self, test_case_id: int, *, page: int, size: int) -> object: ...

    def stream_test_result_attachment(
        self, attachment_id: int, *, inline: bool = False
    ) -> AbstractAsyncContextManager[_AttachmentContentStream]: ...

    def stream_test_result_fixture_attachment(
        self, attachment_id: int, *, inline: bool = False
    ) -> AbstractAsyncContextManager[_AttachmentContentStream]: ...

    def stream_test_case_attachment(
        self, attachment_id: int, *, inline: bool = False
    ) -> AbstractAsyncContextManager[_AttachmentContentStream]: ...


class AttachmentDownloadRuntime:
    """Mutable cache state owned by one server/gateway runtime."""

    def __init__(self, config: AttachmentDownloadConfig, cache_root: Path) -> None:
        self._config = config
        self._cache_root = cache_root
        self._entries: dict[str, CachedAttachmentDownload] = {}
        self._claimed: set[str] = set()
        self._reserved_bytes = 0
        self._pending_stores = 0
        self._lock = asyncio.Lock()
        self._closed = False
        self._sweeper = asyncio.create_task(self._sweep(), name="lucius-attachment-download-expiry")

    @classmethod
    async def create(cls, config: AttachmentDownloadConfig) -> AttachmentDownloadRuntime:
        config.validate()
        cache_root = await asyncio.to_thread(_create_private_cache_root, config.cache_parent)
        return cls(config, cache_root)

    async def store_stream(
        self,
        *,
        filename: str,
        content_type: str,
        content_length: int | None,
        chunks: AsyncIterator[bytes],
    ) -> CachedAttachmentDownload:
        if content_length is not None and content_length > self._config.max_file_bytes:
            raise AllureValidationError("Attachment exceeds Lucius's configured download file limit")

        # ``Content-Length`` is upstream metadata, not a trustworthy capacity
        # reservation.  Reserve the bounded worst case until the stream has
        # completed so a short or misleading header cannot overcommit disk.
        reservation = self._config.max_file_bytes
        async with self._lock:
            if self._closed:
                raise AllureValidationError("Lucius attachment download broker is shutting down")
            await self._remove_expired_locked()
            if len(self._entries) + self._pending_stores >= self._config.max_entries:
                raise AllureValidationError("Lucius's attachment download cache is full; wait for an entry to expire")
            if self._total_bytes() + self._reserved_bytes + reservation > self._config.max_total_bytes:
                raise AllureValidationError("Attachment exceeds Lucius's remaining download cache budget")
            self._reserved_bytes += reservation
            self._pending_stores += 1

        handle = secrets.token_urlsafe(32)
        path = self._cache_root / f"{secrets.token_hex(24)}.bin"
        try:
            byte_size = await _write_stream_atomically(path, chunks, self._config.max_file_bytes)
        except OSError as exc:
            raise AllureValidationError("Lucius could not securely cache the verified attachment") from exc
        finally:
            async with self._lock:
                self._reserved_bytes -= reservation
                self._pending_stores -= 1

        entry = CachedAttachmentDownload(
            handle=handle,
            path=path,
            filename=_sanitize_filename(filename),
            content_type=_safe_content_type(content_type),
            byte_size=byte_size,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=self._config.ttl_seconds),
        )
        async with self._lock:
            if self._closed:
                await _remove_path(path)
                await asyncio.to_thread(_remove_cache_root, self._cache_root)
                raise AllureValidationError("Lucius attachment download broker is shutting down")
            self._entries[handle] = entry
        return entry

    async def claim(self, handle: str) -> CachedAttachmentDownload | None:
        if not _HANDLE_PATTERN.fullmatch(handle):
            return None
        async with self._lock:
            if self._closed:
                return None
            await self._remove_expired_locked()
            if handle in self._claimed:
                return None
            entry = self._entries.get(handle)
            if entry is None:
                return None
            self._claimed.add(handle)
            return entry

    async def complete(self, handle: str) -> None:
        async with self._lock:
            entry = self._entries.pop(handle, None)
            self._claimed.discard(handle)
            if entry is not None:
                await _remove_path(entry.path)

    async def close(self) -> None:
        if self._closed:
            return
        async with self._lock:
            if self._closed:
                return
            self._closed = True
        self._sweeper.cancel()
        try:
            await self._sweeper
        except asyncio.CancelledError:
            pass
        async with self._lock:
            entries = tuple(self._entries.values())
            self._entries.clear()
            self._claimed.clear()
            self._reserved_bytes = 0
        for entry in entries:
            await _remove_path(entry.path)
        await asyncio.to_thread(_remove_cache_root, self._cache_root)

    async def _sweep(self) -> None:
        interval = max(1, min(self._config.ttl_seconds or 1, 60))
        try:
            while True:
                await asyncio.sleep(interval)
                async with self._lock:
                    await self._remove_expired_locked()
        except asyncio.CancelledError:
            raise

    async def _remove_expired_locked(self) -> None:
        now = datetime.now(timezone.utc)
        expired = [
            handle for handle, entry in self._entries.items() if entry.expires_at <= now and handle not in self._claimed
        ]
        for handle in expired:
            entry = self._entries.pop(handle)
            self._claimed.discard(handle)
            await _remove_path(entry.path)

    def _total_bytes(self) -> int:
        return sum(entry.byte_size for entry in self._entries.values())


class AttachmentDownloadRuntimeHolder:
    """Concurrency-safe lazy owner for a broker runtime, without cache state at import time."""

    def __init__(self) -> None:
        self._runtime: AttachmentDownloadRuntime | None = None
        self._lock = asyncio.Lock()
        self._initialization_count = 0
        self._closed = False

    @property
    def is_initialized(self) -> bool:
        return self._runtime is not None

    @property
    def initialization_count(self) -> int:
        return self._initialization_count

    async def get_or_create(self, config: AttachmentDownloadConfig) -> AttachmentDownloadRuntime:
        async with self._lock:
            if self._closed:
                raise AllureValidationError("Lucius attachment download broker is shutting down")
            if self._runtime is None:
                runtime = await AttachmentDownloadRuntime.create(config)
                self._runtime = runtime
                self._initialization_count += 1
            return self._runtime

    async def get(self) -> AttachmentDownloadRuntime | None:
        async with self._lock:
            return None if self._closed else self._runtime

    async def close(self) -> None:
        async with self._lock:
            if self._closed:
                return
            self._closed = True
            runtime = self._runtime
            self._runtime = None
        if runtime is not None:
            await runtime.close()


class AttachmentDownloadService:
    """Verify, fetch, cache, and consume authenticated attachment content."""

    def __init__(
        self,
        client: AllureClient,
        *,
        holder: AttachmentDownloadRuntimeHolder | None = None,
        config: AttachmentDownloadConfig | None = None,
    ) -> None:
        self._client: _DownloadClient = client
        self._holder = holder or AttachmentDownloadRuntimeHolder()
        self._config = config or AttachmentDownloadConfig(
            cache_parent=settings.ATTACHMENT_DOWNLOAD_CACHE_DIR or Path(tempfile.gettempdir()) / "lucius-mcp-downloads",
            max_file_bytes=settings.ATTACHMENT_DOWNLOAD_MAX_FILE_BYTES,
            max_entries=settings.ATTACHMENT_DOWNLOAD_MAX_ENTRIES,
            max_total_bytes=settings.ATTACHMENT_DOWNLOAD_MAX_TOTAL_BYTES,
            ttl_seconds=settings.ATTACHMENT_DOWNLOAD_TTL_SECONDS,
        )

    async def prepare(
        self,
        request: AttachmentPreparationRequest,
        *,
        public_base_url: str,
    ) -> PreparedAttachmentDownload:
        """Return a short-lived local capability only after ownership verification succeeds."""
        request.validate()
        base_url = _validate_public_base_url(public_base_url)
        verified = await self._verify_ownership(request)
        runtime = await self._holder.get_or_create(self._config)
        async with self._stream_verified_content(verified) as content:
            entry = await runtime.store_stream(
                filename=content.filename or verified.filename,
                content_type=content.content_type or verified.content_type,
                content_length=content.content_length,
                chunks=content.iter_bytes(),
            )
        return PreparedAttachmentDownload(
            download_url=f"{base_url}/downloads/{entry.handle}",
            expires_at=entry.expires_at,
            filename=entry.filename,
            content_type=entry.content_type,
            byte_size=entry.byte_size,
        )

    async def claim(self, handle: str) -> CachedAttachmentDownload | None:
        """Claim an entry for one gateway response without initializing a runtime."""
        runtime = await self._holder.get()
        return None if runtime is None else await runtime.claim(handle)

    async def complete(self, handle: str) -> None:
        """Delete an entry after the gateway has completed its response."""
        runtime = await self._holder.get()
        if runtime is not None:
            await runtime.complete(handle)

    async def close(self) -> None:
        """Close only state that a valid preparation request initialized."""
        await self._holder.close()

    async def _verify_ownership(self, request: AttachmentPreparationRequest) -> _VerifiedAttachment:
        if request.kind is AttachmentKind.TEST_RESULT:
            if request.test_result_id is None:  # pragma: no cover - request.validate guards this
                raise AllureValidationError("Test Result ID must be a positive integer")
            attachments = await self._collect_pages(self._client.list_test_result_attachments, request.test_result_id)
        elif request.kind is AttachmentKind.FIXTURE_RESULT:
            if request.test_result_id is None:  # pragma: no cover - request.validate guards this
                raise AllureValidationError("Test Result ID must be a positive integer")
            attachments = await self._collect_pages(
                self._client.get_test_result_fixture_attachments, request.test_result_id
            )
        else:
            if request.test_case_id is None:  # pragma: no cover - request.validate guards this
                raise AllureValidationError("Test Case ID must be a positive integer")
            attachments = await self._collect_pages(self._client.list_test_case_attachments, request.test_case_id)

        matches = [item for item in attachments if _attachment_id(item) == request.attachment_id]
        if len(matches) != 1:
            raise AllureNotFoundError(
                "Attachment does not belong to the supplied owner",
                suggestions=[
                    "Refresh the result or test-case attachment list",
                    "Use the attachment ID from that owner only",
                ],
            )
        match = matches[0]
        return _VerifiedAttachment(
            attachment_id=request.attachment_id,
            kind=request.kind,
            filename=_sanitize_filename(_string_attr(match, "name") or "attachment"),
            content_type=_safe_content_type(_string_attr(match, "content_type")),
            declared_size=_int_attr(match, "content_length"),
        )

    def _stream_verified_content(
        self, verified: _VerifiedAttachment
    ) -> AbstractAsyncContextManager[_AttachmentContentStream]:
        if verified.declared_size is not None and verified.declared_size > self._config.max_file_bytes:
            raise AllureValidationError("Attachment exceeds Lucius's configured download file limit")
        if verified.kind is AttachmentKind.TEST_RESULT:
            return self._client.stream_test_result_attachment(verified.attachment_id)
        if verified.kind is AttachmentKind.FIXTURE_RESULT:
            return self._client.stream_test_result_fixture_attachment(verified.attachment_id)
        return self._client.stream_test_case_attachment(verified.attachment_id)

    @staticmethod
    async def _collect_pages(fetch: Callable[..., Awaitable[object]], owner_id: int) -> list[object]:
        attachments: list[object] = []
        for page in range(100):
            result = await fetch(owner_id, page=page, size=100)
            content = getattr(result, "content", None)
            if isinstance(content, list):
                attachments.extend(content)
            if getattr(result, "last", True) is not False:
                return attachments
        raise AllureValidationError("Attachment ownership check exceeded Lucius's page limit")


def _validate_positive(value: int | None, label: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise AllureValidationError(f"{label} must be a positive integer")


def _validate_public_base_url(value: str) -> str:
    parsed = urlsplit(value)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.netloc
        or parsed.hostname in {_UNSPECIFIED_HOST, "::"}
        or parsed.query
        or parsed.fragment
    ):
        raise AllureValidationError(
            "Attachment downloads require an explicit reachable public base URL",
            suggestions=["Set ATTACHMENT_DOWNLOAD_PUBLIC_BASE_URL to the externally reachable server URL"],
        )
    return value.rstrip("/")


def _sanitize_filename(value: str) -> str:
    cleaned = value.replace("\\", "").replace("/", "")
    cleaned = re.sub(r"[^A-Za-z0-9._ -]", "", cleaned)
    cleaned = cleaned.lstrip(".").strip()[:180]
    return cleaned or "attachment"


def _safe_content_type(value: str | None) -> str:
    return value if isinstance(value, str) and _CONTENT_TYPE_PATTERN.fullmatch(value) else "application/octet-stream"


def _attachment_id(value: object) -> int | None:
    return _int_attr(value, "id")


def _int_attr(value: object, name: str) -> int | None:
    candidate = getattr(value, name, None)
    return candidate if isinstance(candidate, int) and not isinstance(candidate, bool) else None


def _string_attr(value: object, name: str) -> str | None:
    candidate = getattr(value, name, None)
    return candidate if isinstance(candidate, str) else None


def _create_private_cache_root(parent: Path) -> Path:
    parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    parent.chmod(0o700)
    root = Path(tempfile.mkdtemp(prefix="broker-", dir=parent))
    root.chmod(0o700)
    return root


async def _write_stream_atomically(path: Path, chunks: AsyncIterator[bytes], max_file_bytes: int) -> int:
    temporary = path.with_name(f".{path.name}.{secrets.token_hex(8)}.tmp")
    file = None
    byte_size = 0
    completed = False
    try:
        file = await asyncio.to_thread(temporary.open, "xb")
        await asyncio.to_thread(os.chmod, temporary, 0o600)
        async for chunk in chunks:
            if not isinstance(chunk, bytes):
                raise AllureValidationError("Authenticated attachment content had an unsupported response format")
            byte_size += len(chunk)
            if byte_size > max_file_bytes:
                raise AllureValidationError("Attachment exceeds Lucius's configured download file limit")
            await asyncio.to_thread(file.write, chunk)
        await asyncio.to_thread(file.flush)
        await asyncio.to_thread(os.fsync, file.fileno())
        await asyncio.to_thread(os.replace, temporary, path)
        await asyncio.to_thread(os.chmod, path, 0o600)
        completed = True
        return byte_size
    finally:
        if file is not None:
            await asyncio.to_thread(file.close)
        await asyncio.to_thread(temporary.unlink, missing_ok=True)
        if not completed:
            await asyncio.to_thread(path.unlink, missing_ok=True)


async def _remove_path(path: Path) -> None:
    await asyncio.to_thread(path.unlink, missing_ok=True)


def _remove_cache_root(path: Path) -> None:
    try:
        path.rmdir()
    except OSError:
        pass


__all__ = [
    "AttachmentDownloadConfig",
    "AttachmentDownloadRuntimeHolder",
    "AttachmentDownloadService",
    "AttachmentKind",
    "AttachmentPreparationRequest",
    "CachedAttachmentDownload",
    "PreparedAttachmentDownload",
]
