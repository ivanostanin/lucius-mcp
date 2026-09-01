"""Runtime-owned delivery accessors shared by MCP tools and server lifecycles."""

from __future__ import annotations

import ipaddress
from urllib.parse import urlsplit

from src.client.exceptions import AllureValidationError
from src.services.attachment_download_gateway import LoopbackAttachmentDownloadGateway
from src.services.attachment_download_service import AttachmentDownloadRuntimeHolder
from src.utils.config import settings
from src.utils.direct_cli_context import is_direct_cli_attachment_request

attachment_download_runtime_holder = AttachmentDownloadRuntimeHolder()
attachment_download_loopback_gateway = LoopbackAttachmentDownloadGateway(attachment_download_runtime_holder)


async def get_attachment_download_public_base_url() -> str:
    """Resolve a live delivery base only after an attachment is ownership-verified."""
    if is_direct_cli_attachment_request():
        raise AllureValidationError(
            "One-shot CLI commands cannot keep attachment capability URLs alive",
            suggestions=["Use a persistent MCP server session to prepare and HTTP GET the attachment"],
        )
    if settings.MCP_MODE == "http":
        if settings.ATTACHMENT_DOWNLOAD_PUBLIC_BASE_URL:
            public_base_url = settings.ATTACHMENT_DOWNLOAD_PUBLIC_BASE_URL
            if _is_loopback_url(public_base_url):
                raise AllureValidationError(
                    "HTTP attachment downloads require a non-loopback public base URL",
                    suggestions=["Set ATTACHMENT_DOWNLOAD_PUBLIC_BASE_URL to the externally reachable server URL"],
                )
            return public_base_url
        raise AllureValidationError(
            "Attachment downloads require ATTACHMENT_DOWNLOAD_PUBLIC_BASE_URL in HTTP mode",
            suggestions=["Set it to the externally reachable server URL"],
        )
    if settings.MCP_MODE == "stdio":
        return await attachment_download_loopback_gateway.start()
    raise AllureValidationError(
        "One-shot CLI commands cannot serve attachment capability URLs",
        suggestions=["Use the documented --output delivery mode when it is available"],
    )


def _is_loopback_url(value: str) -> bool:
    """Identify local-only URLs, which cannot be advertised by HTTP MCP mode."""
    hostname = urlsplit(value).hostname
    if hostname is None:
        return False
    if hostname.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(hostname).is_loopback
    except ValueError:
        return False
