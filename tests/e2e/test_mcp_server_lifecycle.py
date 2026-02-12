import asyncio
import json
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import time
import zipfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import cast

import httpx
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client

# Define the server script path
SERVER_SCRIPT = "src.main"


@pytest.fixture
def unused_port() -> int:
    """Find a free port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return cast(int, s.getsockname()[1])


def _read_project_version(repo_root: Path) -> str:
    pyproject = (repo_root / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version = "([^"]+)"', pyproject, re.MULTILINE)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    return match.group(1)


@pytest.fixture(scope="module")
def mcpb_python_bundle_path() -> Path:
    """Build mcpb bundles and return path to python bundle artifact."""
    if shutil.which("mcpb") is None:
        pytest.skip("mcpb CLI not found")

    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "deployment/scripts/build-mcpb.sh"

    bash_path = shutil.which("bash") or "/bin/bash"
    result = subprocess.run(  # noqa: S603
        [bash_path, str(script_path)],
        capture_output=True,
        text=True,
        cwd=str(repo_root),
        check=False,
    )
    assert result.returncode == 0, f"build-mcpb.sh failed: {result.stdout}\n{result.stderr}"

    version = _read_project_version(repo_root)
    bundle_path = repo_root / "dist" / f"lucius-mcp-{version}-python.mcpb"
    assert bundle_path.exists(), f"Python bundle not found: {bundle_path}"
    return bundle_path


def _extract_bundle(bundle_path: Path, destination: Path) -> Path:
    with zipfile.ZipFile(bundle_path) as zf:
        zf.extractall(destination)

    manifest_path = destination / "manifest.json"
    assert manifest_path.exists(), f"manifest.json missing in extracted bundle: {destination}"
    return manifest_path


def _resolved_env_from_manifest(manifest: dict[str, object], bundle_root: Path) -> dict[str, str]:
    server = manifest.get("server")
    if not isinstance(server, dict):
        raise ValueError("manifest.server must be an object")

    mcp_config = server.get("mcp_config")
    if not isinstance(mcp_config, dict):
        raise ValueError("manifest.server.mcp_config must be an object")

    env = mcp_config.get("env")
    if not isinstance(env, dict):
        return {}

    resolved: dict[str, str] = {}
    for key, raw_value in env.items():
        if not isinstance(raw_value, str):
            continue

        if raw_value.startswith("${user_config."):
            if key == "ALLURE_ENDPOINT":
                resolved[key] = os.getenv("ALLURE_ENDPOINT", "https://example.invalid")
            elif key == "ALLURE_PROJECT_ID":
                resolved[key] = os.getenv("ALLURE_PROJECT_ID", "1")
            elif key == "ALLURE_API_TOKEN":
                resolved[key] = os.getenv("ALLURE_API_TOKEN", "token")
            continue

        resolved[key] = raw_value.replace("${__dirname}", str(bundle_root))

    return resolved


def _command_from_manifest(manifest: dict[str, object]) -> tuple[str, list[str]]:
    server = manifest.get("server")
    if not isinstance(server, dict):
        raise ValueError("manifest.server must be an object")

    mcp_config = server.get("mcp_config")
    if not isinstance(mcp_config, dict):
        raise ValueError("manifest.server.mcp_config must be an object")

    command = mcp_config.get("command")
    if not isinstance(command, str):
        raise ValueError("manifest.server.mcp_config.command must be a string")

    args_raw = mcp_config.get("args")
    if not isinstance(args_raw, list) or not all(isinstance(arg, str) for arg in args_raw):
        raise ValueError("manifest.server.mcp_config.args must be a list of strings")

    executable = sys.executable if command == "python" else command
    return executable, cast(list[str], list(args_raw))


async def _wait_for_http_server(url: str) -> None:
    start_time = time.time()
    while time.time() - start_time < 20:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=1.0)
                if response.status_code in [200, 404, 405, 406]:
                    return
        except Exception as e:
            print(f"httpx exception: {e}")

        await asyncio.sleep(0.5)

    raise RuntimeError(f"Server failed to start in HTTP mode at {url}")


@asynccontextmanager
async def run_server_stdio():
    """Run the MCP server in stdio mode as a subprocess."""
    env = os.environ.copy()
    env["MCP_MODE"] = "stdio"
    env["LOG_LEVEL"] = "ERROR"  # Reduce noise

    process = subprocess.Popen(  # noqa: S603
        [sys.executable, "-m", SERVER_SCRIPT],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr,
        env=env,
        text=True,
        bufsize=0,
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

    url = f"http://127.0.0.1:{port}/mcp"

    try:
        await _wait_for_http_server(url)
        yield url
    finally:
        process.send_signal(signal.SIGINT)
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()


@asynccontextmanager
async def run_server_from_bundle_http(bundle_root: Path, port: int):
    """Run server from unpacked bundle content using manifest command/args."""
    manifest_obj = json.loads((bundle_root / "manifest.json").read_text(encoding="utf-8"))
    if not isinstance(manifest_obj, dict):
        raise ValueError("manifest.json must be an object")

    manifest = cast(dict[str, object], manifest_obj)
    command, args = _command_from_manifest(manifest)

    env = os.environ.copy()
    env.update(_resolved_env_from_manifest(manifest, bundle_root))
    env["MCP_MODE"] = "http"
    env["PORT"] = str(port)
    env["HOST"] = "127.0.0.1"
    env["LOG_LEVEL"] = "INFO"

    process = subprocess.Popen(  # noqa: S603
        [command, *args],
        cwd=str(bundle_root),
        env=env,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )

    url = f"http://127.0.0.1:{port}/mcp"

    try:
        await _wait_for_http_server(url)
        yield url
    finally:
        process.send_signal(signal.SIGINT)
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()


@pytest.mark.e2e
async def test_stdio_lifecycle() -> None:
    """Test MCP server lifecycle in STDIO mode."""
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", SERVER_SCRIPT],
        env={**os.environ, "MCP_MODE": "stdio", "LOG_LEVEL": "ERROR"},
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            tool_names = [tool.name for tool in tools_result.tools]

            assert "create_test_case" in tool_names
            assert "list_test_cases" in tool_names


@pytest.mark.e2e
async def test_http_lifecycle(unused_port: int) -> None:
    """Test MCP server lifecycle in HTTP (Streamable) mode."""
    async with run_server_http(unused_port) as http_url:
        async with streamable_http_client(http_url) as (read, write, _get_session_id):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools_result = await session.list_tools()
                tool_names = [tool.name for tool in tools_result.tools]

                assert "create_test_case" in tool_names
                assert "search_test_cases" in tool_names


@pytest.mark.e2e
async def test_http_lifecycle_from_unpacked_python_bundle(
    tmp_path: Path,
    unused_port: int,
    mcpb_python_bundle_path: Path,
) -> None:
    """Verify bundle can be unpacked and server starts from unpacked content."""
    bundle_root = tmp_path / "python-bundle"
    bundle_root.mkdir(parents=True, exist_ok=True)
    _extract_bundle(mcpb_python_bundle_path, bundle_root)

    async with run_server_from_bundle_http(bundle_root, unused_port) as http_url:
        async with streamable_http_client(http_url) as (read, write, _get_session_id):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools_result = await session.list_tools()
                tool_names = [tool.name for tool in tools_result.tools]

                assert "create_test_case" in tool_names
                assert "list_test_cases" in tool_names
