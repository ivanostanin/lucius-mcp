import asyncio
import contextlib
import os
import typing

import uvicorn
from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.routing import Mount

from src.utils.config import settings
from src.utils.error import agent_hint_handler
from src.utils.logger import configure_logging, get_logger

# Configure logging early
configure_logging(log_level=settings.LOG_LEVEL)
logger = get_logger("lucius-mcp")

# Initialize FastMCP server
# We define dependencies that the client needs to know about (if any),
# though FastMCP usually infers them from tool signatures.
mcp = FastMCP("lucius-mcp")


@mcp.tool()
def no_op_tool() -> str:
    """
    A placeholder tool to verify the MCP server is reachable.
    Returns a simple 'Ready' string.
    """
    logger.info("no_op_tool invoked")
    return "Ready"


# Get the ASGI app instance once
mcp_asgi = mcp.http_app()


@contextlib.asynccontextmanager
async def lifespan(app: Starlette) -> typing.AsyncGenerator[None]:
    """
    Lifespan context manager for Starlette application.
    Handles startup and shutdown events.
    """
    logger.info(f"Starting Lucius MCP Server in {settings.MCP_MODE} mode")
    # Ensure MCP task group is initialized by entering its lifespan
    if hasattr(mcp_asgi, "lifespan"):
        async with mcp_asgi.lifespan(app):
            yield
    else:
        yield
    logger.info("Shutting down Lucius MCP Server")


# Create main Starlette application
app = Starlette(
    debug=False,
    lifespan=lifespan,
    exception_handlers={Exception: agent_hint_handler},
    routes=[
        # Mount the FastMCP ASGI app under /
        Mount("/", app=mcp_asgi)
    ],
)


def start() -> None:
    """Entry point for running the application directly."""
    if settings.MCP_MODE == "stdio":
        try:
            asyncio.run(mcp.run_stdio_async())
        except KeyboardInterrupt:
            # We use os._exit(0) to avoid the 'Fatal Python error' related to
            # daemon threads and stdin locks during interpreter finalization
            # which often occurs when multiple Ctrl+C signals are received.
            os._exit(0)
    else:
        uvicorn.run("src.main:app", host=settings.HOST, port=settings.PORT, reload=True, ws="wsproto")


if __name__ == "__main__":
    start()
