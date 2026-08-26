from unittest.mock import AsyncMock

import pytest
from pytest_mock import MockerFixture
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.testclient import TestClient

from src.main import app as global_app
from src.main import telemetry_service
from src.utils.telemetry import set_telemetry_service, wrap_tool_with_telemetry


def test_app_initialization(client: TestClient) -> None:
    """
    Verify app initializes correctly using the client fixture which handles refresh.
    """
    # Simply using the client proves the app logic works
    response = client.get("/")
    assert response.status_code in [200, 404, 405]

    # Check global app reference just for sanity
    assert global_app is not None


def test_attachment_download_route_precedes_the_fastmcp_mount() -> None:
    """The capability endpoint must not be shadowed by FastMCP's root mount."""
    assert global_app is not None
    assert isinstance(global_app.routes[0], Route)
    assert global_app.routes[0].path == "/downloads/{handle}"
    assert isinstance(global_app.routes[1], Mount)
    assert global_app.routes[1].path in {"", "/"}


def test_http_startup_emits_telemetry_status_and_event(app: Starlette, mocker: MockerFixture) -> None:
    log_status = mocker.patch.object(telemetry_service, "log_status")
    emit_startup_event = mocker.patch.object(telemetry_service, "emit_startup_event")

    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code in [200, 404, 405]

    log_status.assert_called_once()
    emit_startup_event.assert_called_once()


def test_http_startup_logs_telemetry_enabled_status(
    app: Starlette,
    mocker: MockerFixture,
    caplog: pytest.LogCaptureFixture,
) -> None:
    original_enabled = telemetry_service._enabled
    telemetry_service._enabled = True
    mocker.patch.object(telemetry_service, "emit_startup_event")

    try:
        with caplog.at_level("INFO"):
            with TestClient(app) as client:
                response = client.get("/")
                assert response.status_code in [200, 404, 405]
    finally:
        telemetry_service._enabled = original_enabled

    assert "Telemetry status: enabled" in caplog.text


def test_http_startup_logs_telemetry_disabled_status(
    app: Starlette,
    mocker: MockerFixture,
    caplog: pytest.LogCaptureFixture,
) -> None:
    original_enabled = telemetry_service._enabled
    telemetry_service._enabled = False
    mocker.patch.object(telemetry_service, "emit_startup_event")

    try:
        with caplog.at_level("INFO"):
            with TestClient(app) as client:
                response = client.get("/")
                assert response.status_code in [200, 404, 405]
    finally:
        telemetry_service._enabled = original_enabled

    assert "Telemetry status: disabled" in caplog.text


def test_start_stdio_mode(mocker: MockerFixture) -> None:
    """
    Verify that start() invokes run_stdio_async when MCP_MODE is 'stdio'.
    """
    from src.main import mcp, start
    from src.utils.config import settings

    # Mock settings.MCP_MODE
    mocker.patch.object(settings, "MCP_MODE", "stdio")
    mocker.patch.object(telemetry_service, "log_status")
    mocker.patch.object(telemetry_service, "emit_startup_event")

    # Mock mcp.run_stdio_async and execute the stdio startup path.
    run_stdio_async = mocker.patch.object(mcp, "run_stdio_async", new_callable=AsyncMock)

    start()

    run_stdio_async.assert_awaited_once_with(show_banner=False, log_level=settings.LOG_LEVEL)


@pytest.mark.asyncio
async def test_stdio_delivery_base_url_starts_loopback_gateway_and_shutdown_closes_it(mocker: MockerFixture) -> None:
    from src.main import (
        _run_stdio,
        attachment_download_loopback_gateway,
        attachment_download_runtime_holder,
        get_attachment_download_public_base_url,
        mcp,
    )
    from src.utils.config import settings

    mocker.patch.object(settings, "MCP_MODE", "stdio")
    base_url = await get_attachment_download_public_base_url()
    assert base_url.startswith("http://127.0.0.1:")

    run_stdio_async = mocker.patch.object(mcp, "run_stdio_async", new_callable=AsyncMock)
    close_gateway = mocker.spy(attachment_download_loopback_gateway, "close")
    close_holder = mocker.spy(attachment_download_runtime_holder, "close")

    await _run_stdio()

    run_stdio_async.assert_awaited_once_with(show_banner=False, log_level=settings.LOG_LEVEL)
    close_gateway.assert_awaited_once()
    close_holder.assert_awaited_once()


@pytest.mark.asyncio
async def test_wrap_tool_with_telemetry_emits_success(mocker: MockerFixture) -> None:
    async def dummy_tool(value: int) -> str:
        return str(value)

    set_telemetry_service(telemetry_service)
    emit_tool_usage_event = mocker.patch.object(telemetry_service, "emit_tool_usage_event")
    wrapped_tool = wrap_tool_with_telemetry(dummy_tool)

    result = await wrapped_tool(7)

    assert result == "7"
    emit_tool_usage_event.assert_called_once()
    assert emit_tool_usage_event.call_args.kwargs["tool_name"] == "dummy_tool"
    assert emit_tool_usage_event.call_args.kwargs["outcome"] == "success"


@pytest.mark.asyncio
async def test_wrap_tool_with_telemetry_emits_error_and_reraises(mocker: MockerFixture) -> None:
    async def failing_tool() -> str:
        raise ValueError("boom")

    set_telemetry_service(telemetry_service)
    emit_tool_usage_event = mocker.patch.object(telemetry_service, "emit_tool_usage_event")
    wrapped_tool = wrap_tool_with_telemetry(failing_tool)

    with pytest.raises(ValueError, match="boom"):
        await wrapped_tool()

    emit_tool_usage_event.assert_called_once()
    assert emit_tool_usage_event.call_args.kwargs["tool_name"] == "failing_tool"
    assert emit_tool_usage_event.call_args.kwargs["outcome"] == "error"
    assert isinstance(emit_tool_usage_event.call_args.kwargs["error"], ValueError)
