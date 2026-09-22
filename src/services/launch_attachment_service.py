"""Application service for native launch-level attachment operations."""

from __future__ import annotations

import asyncio
import errno
import mimetypes
import os
import re
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

from src.client import AllureClient, LaunchAttachmentRowDto
from src.client.exceptions import (
    AllureAPIError,
    AllureAuthError,
    AllureNotFoundError,
    AllureValidationError,
    LaunchNotFoundError,
)

_CONTENT_TYPE_PATTERN = re.compile(r"^[^\s/;]+/[^\s;]+(?:\s*;\s*[^\s;=]+=[^\s;]+)*$")
_READ_CHUNK_BYTES = 64 * 1024


@dataclass(frozen=True)
class LaunchAttachmentSummary:
    """Safe attachment metadata returned after TestOps accepts an upload."""

    id: int
    name: str
    content_type: str | None
    content_length: int | None


class LaunchAttachmentService:
    """Validate native launch attachments and map upstream rows to safe summaries."""

    def __init__(self, client: AllureClient) -> None:
        self._client = client

    async def attach(self, launch_id: int, name: str, content: bytes) -> LaunchAttachmentSummary:
        """Attach one bounded, already-validated file to an existing launch."""
        self._validate_attachment_metadata(launch_id, name)
        if not isinstance(content, bytes):
            raise AllureValidationError("Attachment content must be bytes")

        try:
            rows = await self._client.create_launch_attachment(launch_id, (name, content))
        except AllureNotFoundError as exc:
            raise LaunchNotFoundError(launch_id, status_code=exc.status_code) from exc
        except AllureAuthError as exc:
            raise AllureAuthError(
                "TestOps rejected the configured API token for launch attachments", status_code=exc.status_code
            ) from exc
        except AllureValidationError as exc:
            raise AllureValidationError(
                "TestOps rejected the launch attachment metadata or file content", status_code=exc.status_code
            ) from exc
        except AllureAPIError as exc:
            raise AllureAPIError(
                "TestOps could not attach the file to this launch", status_code=exc.status_code
            ) from exc

        if len(rows) != 1:
            raise AllureAPIError("TestOps returned an unexpected launch attachment response")
        return self._summary_from_row(rows[0])

    async def attach_from_path(
        self,
        launch_id: int,
        name: str,
        source_path: str | Path,
        *,
        import_root: Path | None,
        max_file_bytes: int,
        content_type: str | None = None,
    ) -> LaunchAttachmentSummary:
        """Read one safe import-root file asynchronously and attach it to a launch.

        The native generated client determines the multipart part type from the
        supplied filename.  Resolve and validate ``content_type`` here so callers
        receive the documented inference and invalid values are rejected before
        any file is read or upstream request is made.
        """
        self._validate_attachment_metadata(launch_id, name)
        self._resolve_content_type(name, content_type)
        configured_import_root = self._validate_import_configuration(import_root, max_file_bytes)
        content = await asyncio.to_thread(
            _read_import_file,
            configured_import_root,
            source_path,
            max_file_bytes,
        )
        return await self.attach(launch_id, name, content)

    @staticmethod
    def _validate_attachment_metadata(launch_id: int, name: str) -> None:
        if not isinstance(launch_id, int) or isinstance(launch_id, bool) or launch_id <= 0:
            raise AllureValidationError("Launch ID must be a positive integer")
        if not isinstance(name, str) or not name.strip():
            raise AllureValidationError("Attachment filename must be non-empty")

    @staticmethod
    def _validate_import_configuration(import_root: Path | None, max_file_bytes: int) -> Path:
        if import_root is None:
            raise AllureValidationError("LAUNCH_ATTACHMENT_IMPORT_ROOT is not configured")
        if not isinstance(max_file_bytes, int) or isinstance(max_file_bytes, bool) or max_file_bytes <= 0:
            raise AllureValidationError("Launch attachment file limit must be a positive integer")
        return import_root

    @staticmethod
    def _resolve_content_type(name: str, content_type: str | None) -> str:
        resolved = mimetypes.guess_type(name)[0] if content_type is None else content_type
        resolved = resolved or "application/octet-stream"
        if not isinstance(resolved, str) or not _CONTENT_TYPE_PATTERN.fullmatch(resolved):
            raise AllureValidationError("Attachment content type must be a valid media type")
        return resolved

    @staticmethod
    def _summary_from_row(row: LaunchAttachmentRowDto) -> LaunchAttachmentSummary:
        """Validate the endpoint's implicit launch owner and project safe fields."""
        if row.entity != "launch":
            raise AllureAPIError("TestOps returned an unexpected attachment owner")
        if not isinstance(row.id, int) or row.id <= 0 or not isinstance(row.name, str) or not row.name:
            raise AllureAPIError("TestOps returned incomplete launch attachment metadata")
        return LaunchAttachmentSummary(
            id=row.id,
            name=row.name,
            content_type=row.content_type,
            content_length=row.content_length,
        )


def _read_import_file(import_root: Path, source_path: str | Path, max_file_bytes: int) -> bytes:
    """Read a bounded regular file without allowing import-root escape or links."""
    root = _resolve_import_root(import_root)
    relative_source = _relative_import_source(source_path, root)
    if os.name == "nt":
        return _read_import_file_portably(root, relative_source, max_file_bytes)
    return _read_import_file_posix(root, relative_source, max_file_bytes)


def _resolve_import_root(import_root: Path) -> Path:
    try:
        root = import_root.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise AllureValidationError("Configured launch attachment import root is unavailable") from exc
    if not root.is_dir():
        raise AllureValidationError("Configured launch attachment import root is not a directory")
    return root


def _relative_import_source(source_path: str | Path, root: Path) -> Path:
    try:
        candidate = Path(source_path)
    except TypeError as exc:
        raise AllureValidationError("Attachment source path must be a path") from exc
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        relative = candidate.relative_to(root)
    except ValueError as exc:
        raise AllureValidationError("Attachment source path is outside the configured import root") from exc
    if not relative.parts or any(part in {".", ".."} for part in relative.parts):
        raise AllureValidationError("Attachment source path is outside the configured import root")
    return relative


def _read_import_file_posix(root: Path, relative_source: Path, max_file_bytes: int) -> bytes:
    """Use descriptor-relative opens so a symlink swap cannot escape the root."""
    directory_fds: list[int] = []
    file_fd: int | None = None
    try:
        file_fd, directory_fds = _open_regular_import_file(root, relative_source, max_file_bytes)
        return _read_open_file(file_fd, max_file_bytes)
    except FileNotFoundError as exc:
        raise AllureValidationError("Attachment source file does not exist") from exc
    except PermissionError as exc:
        raise AllureValidationError("Attachment source file is not readable") from exc
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise AllureValidationError("Attachment source path must not contain symlinks") from exc
        raise AllureValidationError("Attachment source file cannot be read safely") from exc
    finally:
        if file_fd is not None:
            os.close(file_fd)
        _close_file_descriptors(directory_fds)


def _open_regular_import_file(root: Path, relative_source: Path, max_file_bytes: int) -> tuple[int, list[int]]:
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    directory_fds = [os.open(root, directory_flags)]
    try:
        for part in relative_source.parts[:-1]:
            _reject_symlink_component(directory_fds[-1], part)
            directory_fd = os.open(part, directory_flags, dir_fd=directory_fds[-1])
            directory_fds.append(directory_fd)
            if not stat.S_ISDIR(os.fstat(directory_fd).st_mode):
                raise AllureValidationError("Attachment source path contains a non-directory component")
        _reject_symlink_component(directory_fds[-1], relative_source.name)
        file_fd = os.open(relative_source.name, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory_fds[-1])
        file_info = os.fstat(file_fd)
        if not stat.S_ISREG(file_info.st_mode):
            os.close(file_fd)
            raise AllureValidationError("Attachment source must be a regular file")
        if file_info.st_size > max_file_bytes:
            os.close(file_fd)
            raise AllureValidationError("Attachment exceeds Lucius's configured attachment file limit")
        return file_fd, directory_fds
    except BaseException:
        _close_file_descriptors(directory_fds)
        raise


def _reject_symlink_component(directory_fd: int, name: str) -> None:
    if stat.S_ISLNK(os.stat(name, dir_fd=directory_fd, follow_symlinks=False).st_mode):
        raise AllureValidationError("Attachment source path must not contain symlinks")


def _close_file_descriptors(file_descriptors: list[int]) -> None:
    for file_descriptor in reversed(file_descriptors):
        try:
            os.close(file_descriptor)
        except OSError:
            pass


def _read_import_file_portably(root: Path, relative_source: Path, max_file_bytes: int) -> bytes:
    """Use lstat checks where descriptor-relative, no-follow opens are unavailable."""
    path = root
    for part in relative_source.parts:
        path /= part
        try:
            info = path.lstat()
        except FileNotFoundError as exc:
            raise AllureValidationError("Attachment source file does not exist") from exc
        except PermissionError as exc:
            raise AllureValidationError("Attachment source file is not readable") from exc
        if stat.S_ISLNK(info.st_mode):
            raise AllureValidationError("Attachment source path must not contain symlinks")
    if not stat.S_ISREG(path.stat().st_mode):
        raise AllureValidationError("Attachment source must be a regular file")
    if path.stat().st_size > max_file_bytes:
        raise AllureValidationError("Attachment exceeds Lucius's configured attachment file limit")
    try:
        with path.open("rb") as source:
            return _read_chunks(source, max_file_bytes)
    except PermissionError as exc:
        raise AllureValidationError("Attachment source file is not readable") from exc


def _read_open_file(file_fd: int, max_file_bytes: int) -> bytes:
    with os.fdopen(file_fd, "rb", closefd=False) as source:
        return _read_chunks(source, max_file_bytes)


def _read_chunks(source: BinaryIO, max_file_bytes: int) -> bytes:
    chunks: list[bytes] = []
    byte_count = 0
    while True:
        chunk = source.read(min(_READ_CHUNK_BYTES, max_file_bytes - byte_count + 1))
        if not chunk:
            break
        byte_count += len(chunk)
        if byte_count > max_file_bytes:
            raise AllureValidationError("Attachment exceeds Lucius's configured attachment file limit")
        chunks.append(chunk)
    return b"".join(chunks)


__all__ = ["LaunchAttachmentService", "LaunchAttachmentSummary"]
