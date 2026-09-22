"""Single-replica, one-use capability state for launch attachment uploads."""

from __future__ import annotations

import asyncio
import re
import secrets
import tempfile
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.client.exceptions import AllureValidationError

_HANDLE_PATTERN = re.compile(r"^[A-Za-z0-9_-]{32,}$")
_CONTENT_TYPE_PATTERN = re.compile(r"^[A-Za-z0-9!#$&^_.+-]+/[A-Za-z0-9!#$&^_.+-]+$")


@dataclass(frozen=True)
class LaunchAttachmentUploadConfig:
    """Validated bounds and private temporary directory for one HTTP replica."""

    temp_parent: Path
    max_file_bytes: int
    ttl_seconds: int

    def validate(self) -> None:
        if (
            not isinstance(self.max_file_bytes, int)
            or isinstance(self.max_file_bytes, bool)
            or self.max_file_bytes <= 0
        ):
            raise AllureValidationError("Launch attachment upload file limit must be a positive integer")
        if not isinstance(self.ttl_seconds, int) or isinstance(self.ttl_seconds, bool) or self.ttl_seconds <= 0:
            raise AllureValidationError("Launch attachment upload TTL must be a positive integer")


@dataclass(frozen=True)
class PreparedLaunchAttachmentUpload:
    """Safe public preparation response for a one-use raw upload capability."""

    upload_url: str
    expires_at: datetime
    max_file_bytes: int


@dataclass(frozen=True)
class _PreparedLaunchAttachmentCapability:
    """Internal prepared state; its opaque handle is never returned by the service."""

    handle: str
    expires_at: datetime


@dataclass(frozen=True)
class PendingLaunchAttachmentUpload:
    """Claimed metadata retained only inside the local server runtime."""

    handle: str
    launch_id: int
    name: str
    content_type: str
    expires_at: datetime


class LaunchAttachmentUploadRuntime:
    """Capability state for one Lucius HTTP process; not safe for multiple replicas."""

    def __init__(self, config: LaunchAttachmentUploadConfig, temp_root: Path) -> None:
        self._config = config
        self._temp_root = temp_root
        self._entries: dict[str, PendingLaunchAttachmentUpload] = {}
        self._claimed: set[str] = set()
        self._lock = asyncio.Lock()
        self._closed = False
        self._sweeper = asyncio.create_task(self._sweep(), name="lucius-launch-attachment-upload-expiry")

    @classmethod
    async def create(cls, config: LaunchAttachmentUploadConfig) -> LaunchAttachmentUploadRuntime:
        config.validate()
        temp_root = await asyncio.to_thread(_create_private_temp_root, config.temp_parent)
        return cls(config, temp_root)

    @property
    def max_file_bytes(self) -> int:
        return self._config.max_file_bytes

    @property
    def temp_root(self) -> Path:
        return self._temp_root

    async def prepare(self, *, launch_id: int, name: str, content_type: str) -> _PreparedLaunchAttachmentCapability:
        """Create opaque one-use state after validating only safe caller metadata."""
        _validate_positive(launch_id, "Launch ID")
        _validate_name(name)
        _validate_content_type(content_type)
        handle = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=self._config.ttl_seconds)
        entry = PendingLaunchAttachmentUpload(
            handle=handle,
            launch_id=launch_id,
            name=name,
            content_type=content_type.lower(),
            expires_at=expires_at,
        )
        async with self._lock:
            if self._closed:
                raise AllureValidationError("Lucius launch attachment upload broker is shutting down")
            await self._remove_expired_locked()
            self._entries[handle] = entry
        return _PreparedLaunchAttachmentCapability(handle=handle, expires_at=expires_at)

    async def claim(self, handle: str) -> PendingLaunchAttachmentUpload | None:
        """Atomically consume a capability; failures remain consumed to prevent replays."""
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
        """Permanently remove consumed state after every gateway outcome."""
        async with self._lock:
            self._entries.pop(handle, None)
            self._claimed.discard(handle)

    async def close(self) -> None:
        """Stop expiry handling and remove private bridge files."""
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
            self._entries.clear()
            self._claimed.clear()
        await asyncio.to_thread(_remove_private_temp_root, self._temp_root)

    async def _sweep(self) -> None:
        try:
            while True:
                await asyncio.sleep(min(self._config.ttl_seconds, 60))
                async with self._lock:
                    await self._remove_expired_locked()
        except asyncio.CancelledError:
            raise

    async def _remove_expired_locked(self) -> None:
        now = datetime.now(timezone.utc)
        for handle in [
            handle for handle, entry in self._entries.items() if entry.expires_at <= now and handle not in self._claimed
        ]:
            self._entries.pop(handle, None)


class LaunchAttachmentUploadRuntimeHolder:
    """Lazy lifecycle owner for the single-replica upload runtime."""

    def __init__(self) -> None:
        self._runtime: LaunchAttachmentUploadRuntime | None = None
        self._lock = asyncio.Lock()
        self._closed = False

    async def get_or_create(self, config: LaunchAttachmentUploadConfig) -> LaunchAttachmentUploadRuntime:
        async with self._lock:
            if self._closed:
                raise AllureValidationError("Lucius launch attachment upload broker is shutting down")
            if self._runtime is None:
                self._runtime = await LaunchAttachmentUploadRuntime.create(config)
            return self._runtime

    async def get(self) -> LaunchAttachmentUploadRuntime | None:
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


class LaunchAttachmentUploadService:
    """Prepare public upload URLs while keeping capability handles process-private."""

    def __init__(self, *, holder: LaunchAttachmentUploadRuntimeHolder, config: LaunchAttachmentUploadConfig) -> None:
        self._holder = holder
        self._config = config

    async def prepare(
        self,
        *,
        launch_id: int,
        name: str,
        content_type: str,
        public_base_url: str | Callable[[], Awaitable[str]],
    ) -> PreparedLaunchAttachmentUpload:
        resolved_public_base_url = await public_base_url() if callable(public_base_url) else public_base_url
        base_url = _validate_public_base_url(resolved_public_base_url)
        runtime = await self._holder.get_or_create(self._config)
        capability = await runtime.prepare(launch_id=launch_id, name=name, content_type=content_type)
        return PreparedLaunchAttachmentUpload(
            upload_url=f"{base_url}/launch-uploads/{capability.handle}",
            expires_at=capability.expires_at,
            max_file_bytes=runtime.max_file_bytes,
        )


def _create_private_temp_root(parent: Path) -> Path:
    parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix="lucius-launch-uploads-", dir=parent))


def _remove_private_temp_root(root: Path) -> None:
    if root.exists():
        for path in root.iterdir():
            if path.is_file() or path.is_symlink():
                path.unlink(missing_ok=True)
        root.rmdir()


def _validate_positive(value: int, label: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise AllureValidationError(f"{label} must be a positive integer")


def _validate_name(value: str) -> None:
    if not isinstance(value, str) or not value.strip() or "/" in value or "\\" in value or "\x00" in value:
        raise AllureValidationError("Attachment filename must be non-empty and must not contain a path")


def _validate_content_type(value: str) -> None:
    if not isinstance(value, str) or not _CONTENT_TYPE_PATTERN.fullmatch(value):
        raise AllureValidationError("Content type is invalid")


def _validate_public_base_url(value: str) -> str:
    from urllib.parse import urlsplit

    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.netloc or parsed.query or parsed.fragment:
        raise AllureValidationError("Launch attachment uploads require an explicit reachable HTTPS public base URL")
    return value.rstrip("/")


__all__ = [
    "LaunchAttachmentUploadConfig",
    "LaunchAttachmentUploadRuntime",
    "LaunchAttachmentUploadRuntimeHolder",
    "LaunchAttachmentUploadService",
    "PendingLaunchAttachmentUpload",
    "PreparedLaunchAttachmentUpload",
]
