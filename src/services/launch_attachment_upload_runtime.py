"""Runtime-owned configuration for HTTP-only launch attachment uploads.

This interim broker is intentionally process-local.  Horizontally scaled
deployments must keep the route disabled until deferred task D-12-7 supplies a
shared capability provider with atomic claim semantics.
"""

from __future__ import annotations

import ipaddress
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

from src.client.exceptions import AllureValidationError
from src.services.launch_attachment_upload_service import (
    LaunchAttachmentUploadConfig,
    LaunchAttachmentUploadRuntimeHolder,
)
from src.utils.config import settings
from src.utils.direct_cli_context import is_direct_cli_attachment_request

launch_attachment_upload_runtime_holder = LaunchAttachmentUploadRuntimeHolder()


def launch_attachment_upload_config() -> LaunchAttachmentUploadConfig:
    """Build bounded private-storage configuration only when a capability is prepared."""
    return LaunchAttachmentUploadConfig(
        temp_parent=settings.LAUNCH_ATTACHMENT_UPLOAD_TEMP_DIR
        or Path(tempfile.gettempdir()) / "lucius-mcp-launch-uploads",
        max_file_bytes=settings.LAUNCH_ATTACHMENT_UPLOAD_MAX_FILE_BYTES,
        ttl_seconds=settings.LAUNCH_ATTACHMENT_UPLOAD_TTL_SECONDS,
    )


async def get_launch_attachment_upload_public_base_url() -> str:
    """Resolve the ingress URL; push is deliberately unavailable outside HTTP mode."""
    if is_direct_cli_attachment_request() or settings.MCP_MODE != "http":
        raise AllureValidationError(
            "Launch attachment push uploads require a persistent HTTP MCP server",
            suggestions=["Use transfer_mode='pull' with LAUNCH_ATTACHMENT_IMPORT_ROOT, or deploy HTTP MCP over HTTPS"],
        )
    value = settings.LAUNCH_ATTACHMENT_UPLOAD_PUBLIC_BASE_URL
    if not value:
        raise AllureValidationError(
            "Launch attachment push uploads require LAUNCH_ATTACHMENT_UPLOAD_PUBLIC_BASE_URL",
            suggestions=["Set it to the externally reachable HTTPS server URL"],
        )
    if not _is_external_https_url(value):
        raise AllureValidationError(
            "Launch attachment push uploads require a non-loopback HTTPS public base URL",
            suggestions=["Set LAUNCH_ATTACHMENT_UPLOAD_PUBLIC_BASE_URL to the externally reachable HTTPS server URL"],
        )
    return value.rstrip("/")


def _is_external_https_url(value: str) -> bool:
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.query
        or parsed.fragment
        or parsed.username
        or parsed.password
    ):
        return False
    hostname = parsed.hostname
    if hostname is None or hostname.lower() == "localhost":
        return False
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        return True
    return not (address.is_loopback or address.is_unspecified or address.is_private or address.is_link_local)


__all__ = [
    "get_launch_attachment_upload_public_base_url",
    "launch_attachment_upload_config",
    "launch_attachment_upload_runtime_holder",
]
