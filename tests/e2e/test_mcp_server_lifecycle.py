import asyncio
import os
import signal
import socket
import subprocess
import sys
import time
from contextlib import asynccontextmanager

import httpx
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client

# Define the server script path
SERVER_SCRIPT = "src.main"


@pytest.fixture
def unused_port():
    """Find a free port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@asynccontextmanager
async def run_server_stdio():
    """Run the MCP server in stdio mode as a subprocess."""
    env = os.environ.copy()
    env["MCP_MODE"] = "stdio"
    env["LOG_LEVEL"] = "ERROR"  # Reduce noise

    # Use sys.executable to run with the current python interpreter
    process = subprocess.Popen(  # noqa: S603
        [sys.executable, "-m", SERVER_SCRIPT],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr,
        env=env,
        text=True,
        bufsize=0,  # Unbuffered
    )

    try:
        yield process
    finally:
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()


@asynccontextmanager
async def run_server_http(port: int):
    """Run the MCP server in http mode as a subprocess."""
    env = os.environ.copy()
    env["MCP_MODE"] = "http"
    env["PORT"] = str(port)
    env["HOST"] = "127.0.0.1"
    env["LOG_LEVEL"] = "INFO"

    process = subprocess.Popen(  # noqa: S603
        [sys.executable, "-m", SERVER_SCRIPT],
        env=env,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )

    # Wait for server to start
    # Route is /mcp for Streamable HTTP
    url = f"http://127.0.0.1:{port}/mcp"

    print(f"Waiting for HTTP server at {url}...")
    start_time = time.time()
    while time.time() - start_time < 15:
        try:
            async with httpx.AsyncClient() as client:
                # Streamable HTTP endpoint handles POST mostly
                # We check with GET to see if port is open and server responds (even with 405)
                try:
                    resp = await client.get(url, timeout=1.0)
                    status = resp.status_code
                except httpx.HTTPStatusError as e:
                    status = e.response.status_code

                print(f"Health check {url}: {status}")
                if status in [200, 404, 405, 406]:
                    break
        except Exception as e:
            # Connection refused etc - expected during startup
            print(f"Health check exception (expected during startup): {e}")

        await asyncio.sleep(0.5)
    else:
        process.terminate()
        raise RuntimeError(f"Server failed to start in HTTP mode at {url}")

    try:
        yield url
    finally:
        # Send SIGINT (CTRL+C) to allow graceful shutdown
        process.send_signal(signal.SIGINT)
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()


async def test_stdio_lifecycle():
    """
    Test MCP server lifecycle in STDIO mode.
    Client -> Server: initialize
    Server -> Client: result (capabilities)
    Client -> Server: notifications/initialized
    Client -> Server: tools/list
    Server -> Client: result (tools)
    """
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", SERVER_SCRIPT],
        env={**os.environ, "MCP_MODE": "stdio", "LOG_LEVEL": "ERROR"},
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()

            # List tools
            tools_result = await session.list_tools()

            # Verify tools are present
            tool_names = [tool.name for tool in tools_result.tools]
            print(f"Discovered tools (stdio): {tool_names}")

            assert "create_test_case" in tool_names
            assert "list_test_cases" in tool_names


async def test_http_lifecycle(unused_port):
    """
    Test MCP server lifecycle in HTTP (Streamable) mode.
    Connect -> Handshake -> List Tools -> Disconnect
    """
    port = unused_port
    async with run_server_http(port) as http_url:
        print(f"Connecting to Streamable HTTP URL: {http_url}")

        async with streamable_http_client(http_url) as (read, write, _get_session_id):
            async with ClientSession(read, write) as session:
                # Initialize
                await session.initialize()

                # List tools
                tools_result = await session.list_tools()

                # Verify tools
                tool_names = [tool.name for tool in tools_result.tools]
                print(f"Discovered tools (http): {tool_names}")

                assert "create_test_case" in tool_names
                assert "search_test_cases" in tool_names
