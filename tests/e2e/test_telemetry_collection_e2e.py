"""End-to-end telemetry validation for Story 8.5."""

from __future__ import annotations

import json
import os
import sys
import time
from collections.abc import AsyncIterator, Generator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock, Thread
from typing import Any

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from src.utils.config import telemetry_config

pytestmark = pytest.mark.e2e


@dataclass
class TelemetryCapture:
    path: str
    headers: dict[str, str]
    body: dict[str, Any]


@pytest.fixture
def telemetry_prerequisites() -> str:
    """Ensure required runtime prerequisites exist before telemetry E2E tests run."""
    allure_token = os.getenv("ALLURE_API_TOKEN")
    if not allure_token:
        pytest.skip("Telemetry E2E requires ALLURE_API_TOKEN to be set.")
    if not telemetry_config.umami_website_id:
        pytest.skip("Telemetry E2E requires telemetry_config.umami_website_id in src/utils/config.py.")
    return allure_token


@pytest.fixture
def telemetry_collector() -> Generator[tuple[str, list[TelemetryCapture]]]:
    captures: list[TelemetryCapture] = []
    lock = Lock()

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            length = int(self.headers.get("Content-Length", "0"))
            body_raw = self.rfile.read(length).decode("utf-8")
            body = json.loads(body_raw) if body_raw else {}
            headers = {key: value for key, value in self.headers.items()}
            with lock:
                captures.append(TelemetryCapture(path=self.path, headers=headers, body=body))
            self.send_response(204)
            self.end_headers()

        def log_message(self, format: str, *args: object) -> None:
            return

    try:
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    except OSError as exc:
        pytest.skip(f"Local telemetry collector cannot start in this environment: {exc}")
    host, port = server.server_address
    base_url = f"http://{host}:{port}"
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        yield base_url, captures
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()


def _wait_for_count(captures: list[TelemetryCapture], expected: int, timeout: float = 5.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if len(captures) >= expected:
            return True
        time.sleep(0.05)
    return False


@asynccontextmanager
async def _stdio_session(env: dict[str, str]) -> AsyncIterator[ClientSession]:
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "tests.e2e.telemetry_server_entrypoint"],
        env=env,
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


def _build_server_env(
    *,
    allure_token: str,
    enabled: bool,
    collector_base_url: str,
) -> dict[str, str]:
    env = dict(os.environ)
    env["MCP_MODE"] = "stdio"
    env["LOG_LEVEL"] = "ERROR"
    env["ALLURE_API_TOKEN"] = allure_token
    env["TELEMETRY_ENABLED"] = "true" if enabled else "false"
    env["LUCIUS_E2E_UMAMI_BASE_URL"] = collector_base_url
    return env


def _assert_payload_has_runtime_fields(payload: dict[str, Any]) -> None:
    assert payload["server_version"]
    assert payload["python_version"]
    assert payload["platform"]
    assert payload["mcp_mode"] == "stdio"
    assert payload["deployment_method"] in {"docker", "mcpb", "uvx+pypi", "cli", "plain-code-checkout"}


@pytest.mark.asyncio
async def test_telemetry_startup_event_emitted(
    telemetry_prerequisites: str,
    telemetry_collector: tuple[str, list[TelemetryCapture]],
) -> None:
    allure_token = telemetry_prerequisites
    collector_base_url, captures = telemetry_collector
    env = _build_server_env(allure_token=allure_token, enabled=True, collector_base_url=collector_base_url)

    async with _stdio_session(env):
        assert _wait_for_count(captures, expected=1)

    startup = next(
        (
            item
            for item in captures
            if isinstance(item.body.get("payload"), dict)
            and str(item.body["payload"].get("name", "")).startswith("startup.")
        ),
        None,
    )
    assert startup is not None
    assert startup.path == "/api/send"
    assert startup.headers.get("User-Agent")
    payload = startup.body["payload"].get("data", {})
    assert isinstance(payload, dict)
    _assert_payload_has_runtime_fields(payload)
    assert payload.get("session_id_hash")
    assert payload.get("installation_id_hash")
    assert payload.get("project_id_hash")
    assert payload.get("endpoint_host_hash")


@pytest.mark.asyncio
async def test_telemetry_tool_success_and_error_events_emitted(
    telemetry_prerequisites: str,
    telemetry_collector: tuple[str, list[TelemetryCapture]],
) -> None:
    allure_token = telemetry_prerequisites
    collector_base_url, captures = telemetry_collector
    env = _build_server_env(allure_token=allure_token, enabled=True, collector_base_url=collector_base_url)

    async with _stdio_session(env) as session:
        success = await session.call_tool("update_test_case", {"test_case_id": 1, "confirm": False})
        assert success.isError is False

        validation_error = await session.call_tool("search_test_cases", {"query": ""})
        assert validation_error.isError is True

        assert _wait_for_count(captures, expected=3)

    tool_events = [
        item
        for item in captures
        if isinstance(item.body.get("payload"), dict)
        and (
            str(item.body["payload"].get("name", "")).startswith("tool_use.")
            or str(item.body["payload"].get("name", "")).startswith("tool_error.")
        )
    ]
    assert len(tool_events) >= 2

    update_event = next(item for item in tool_events if item.body["payload"].get("name") == "tool_use.update_test_case")
    update_payload = update_event.body["payload"]["data"]
    assert update_payload["outcome"] == "success"
    assert update_payload["duration_bucket"]
    _assert_payload_has_runtime_fields(update_payload)

    search_event = next(
        item
        for item in tool_events
        if item.body["payload"].get("name") == "tool_error.validation.search_test_cases"
        if isinstance(item.body["payload"].get("data"), dict)
    )
    search_payload = search_event.body["payload"]["data"]
    assert search_payload["outcome"] == "error"
    assert search_payload["error_category"] == "validation"
    _assert_payload_has_runtime_fields(search_payload)


@pytest.mark.asyncio
async def test_telemetry_opt_out_disables_emission(
    telemetry_prerequisites: str,
    telemetry_collector: tuple[str, list[TelemetryCapture]],
) -> None:
    allure_token = telemetry_prerequisites
    collector_base_url, captures = telemetry_collector
    env = _build_server_env(allure_token=allure_token, enabled=False, collector_base_url=collector_base_url)

    async with _stdio_session(env) as session:
        result = await session.call_tool("update_test_case", {"test_case_id": 1, "confirm": False})
        assert result.isError is False
        time.sleep(0.5)

    assert captures == []
