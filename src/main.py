import asyncio
import contextlib
import os
import typing

from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.routing import Mount

from src.client.exceptions import AllureValidationError
from src.services.attachment_download_gateway import LoopbackAttachmentDownloadGateway, attachment_download_route
from src.services.attachment_download_service import AttachmentDownloadRuntimeHolder
from src.services.telemetry_service import TelemetryService
from src.tools import all_tools
from src.tools.annotations import get_tool_annotations, get_tool_tags, validate_tool_annotation_coverage
from src.tools.output_schemas import output_model_for, output_schema_for, validate_registry_coverage
from src.utils.config import settings
from src.utils.error import agent_hint_handler
from src.utils.logger import configure_logging, get_logger
from src.utils.telemetry import set_telemetry_service, wrap_tool_with_telemetry
from src.version import __version__

# Configure logging early
configure_logging(
    log_level=settings.LOG_LEVEL, log_format=settings.LOG_FORMAT, force_stderr=(settings.MCP_MODE == "stdio")
)
logger = get_logger("lucius-mcp")
telemetry_service = TelemetryService()
set_telemetry_service(telemetry_service)


# Initialize FastMCP server
mcp = FastMCP(
    name="lucius-mcp",
    version=__version__,
)

# Register tools
validate_tool_annotation_coverage({tool.__name__ for tool in all_tools})
validate_registry_coverage()
for tool in all_tools:
    mcp.tool(
        tags=get_tool_tags(tool.__name__),
        annotations=get_tool_annotations(tool.__name__),
        output_schema=output_schema_for(tool.__name__),
    )(wrap_tool_with_telemetry(tool, output_model=output_model_for(tool.__name__)))

# The ASGI app and main app are created lazily or only when needed for HTTP mode
_mcp_asgi = None
attachment_download_runtime_holder = AttachmentDownloadRuntimeHolder()
attachment_download_loopback_gateway = LoopbackAttachmentDownloadGateway(attachment_download_runtime_holder)


async def get_attachment_download_public_base_url() -> str:
    """Resolve delivery only in a runtime that can keep a capability URL alive."""
    if settings.MCP_MODE == "http":
        if settings.ATTACHMENT_DOWNLOAD_PUBLIC_BASE_URL:
            return settings.ATTACHMENT_DOWNLOAD_PUBLIC_BASE_URL
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


def get_mcp_asgi() -> Starlette:
    global _mcp_asgi
    if _mcp_asgi is None:
        _mcp_asgi = mcp.http_app()
    return _mcp_asgi


@contextlib.asynccontextmanager
async def lifespan(app: Starlette) -> typing.AsyncGenerator[None, None]:
    """
    Lifespan context manager for Starlette application.
    Handles startup and shutdown events.
    """
    telemetry_service.log_status()
    telemetry_service.emit_startup_event()
    logger.info(f"Starting Lucius MCP Server in {settings.MCP_MODE} mode")
    mcp_asgi = get_mcp_asgi()
    # Ensure MCP task group is initialized by entering its lifespan
    try:
        if hasattr(mcp_asgi, "lifespan"):
            async with mcp_asgi.lifespan(app):
                yield
        else:
            yield
    finally:
        await attachment_download_runtime_holder.close()
        logger.info("Shutting down Lucius MCP Server")


# Create main Starlette application lazily
def get_app() -> Starlette | None:
    if settings.MCP_MODE == "http":
        return Starlette(
            debug=False,
            lifespan=lifespan,
            exception_handlers={Exception: agent_hint_handler},
            routes=[
                # Explicit capability route must precede FastMCP's root mount.
                attachment_download_route(attachment_download_runtime_holder),
                # Mount the FastMCP ASGI app under /
                Mount("/", app=get_mcp_asgi()),
            ],
        )
    else:
        return None


# For uvicorn.run("src.main:app", ...)
app = get_app()


async def _run_stdio() -> None:
    telemetry_service.log_status()
    telemetry_service.emit_startup_event()
    try:
        await mcp.run_stdio_async(show_banner=False, log_level=settings.LOG_LEVEL)
    finally:
        await attachment_download_loopback_gateway.close()
        await attachment_download_runtime_holder.close()


def start() -> None:
    """Entry point for running the application directly."""
    if settings.MCP_MODE == "stdio":
        try:
            asyncio.run(_run_stdio())
        except KeyboardInterrupt:
            os._exit(0)
    elif settings.MCP_MODE == "http":
        import uvicorn

        uvicorn.run("src.main:app", host=settings.HOST, port=settings.PORT, reload=True, ws="wsproto")
    else:
        raise ValueError(f"Invalid MCP mode: {settings.MCP_MODE}")


if __name__ == "__main__":
    start()
