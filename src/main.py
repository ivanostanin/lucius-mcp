import asyncio
import contextlib
import os
import typing

import uvicorn
from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.middleware.cors import CORSMiddleware

from src.tools.create_test_case import create_test_case
from src.utils.config import settings
from src.utils.error import agent_hint_handler
from src.utils.logger import configure_logging, get_logger

# Configure logging early
configure_logging(
    log_level=settings.LOG_LEVEL, 
    log_format=settings.LOG_FORMAT,
    force_stderr=(settings.MCP_MODE == "stdio")
)
logger = get_logger("lucius-mcp")

# Initialize FastMCP server
mcp = FastMCP(name="lucius-mcp",
              # stateless_http=True
              )

# Register tools
mcp.tool()(create_test_case)


@mcp.tool()
def no_op_tool() -> str:
    """
    A placeholder tool to verify the MCP server is reachable.
    Returns a simple 'Ready' string.
    """
    logger.info("no_op_tool invoked")
    return "Ready"


# The ASGI app and main app are created lazily or only when needed for HTTP mode
_mcp_asgi = None

def get_mcp_asgi():
    global _mcp_asgi
    if _mcp_asgi is None:
        _mcp_asgi = mcp.http_app()
    return _mcp_asgi

@contextlib.asynccontextmanager
async def lifespan(app: Starlette) -> typing.AsyncGenerator[None]:
    """
    Lifespan context manager for Starlette application.
    Handles startup and shutdown events.
    """
    logger.info(f"Starting Lucius MCP Server in {settings.MCP_MODE} mode")
    mcp_asgi = get_mcp_asgi()
    # Ensure MCP task group is initialized by entering its lifespan
    if hasattr(mcp_asgi, "lifespan"):
        async with mcp_asgi.lifespan(app):
            yield
    else:
        yield
    logger.info("Shutting down Lucius MCP Server")


# Create main Starlette application lazily
def get_app():
    return Starlette(
        debug=False,
        lifespan=lifespan,
        exception_handlers={Exception: agent_hint_handler},
        routes=[
            # Mount the FastMCP ASGI app under /
            Mount("/", app=get_mcp_asgi())
        ],
    )

# For uvicorn.run("src.main:app", ...)
app = get_app()


def start() -> None:
    """Entry point for running the application directly."""
    if settings.MCP_MODE == "stdio":
        try:
            asyncio.run(mcp.run_stdio_async(show_banner=False))
        except KeyboardInterrupt:
            os._exit(0)
    else:
        uvicorn.run("src.main:app", host=settings.HOST, port=settings.PORT, reload=True, ws="wsproto")


if __name__ == "__main__":
    start()
