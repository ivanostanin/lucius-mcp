import json

import httpx
import pytest
import respx

from src.services.telemetry_service import TelemetryService
from src.utils.config import settings
from src.utils.error import AuthenticationError


@pytest.mark.asyncio
@respx.mock
async def test_startup_and_tool_events_sent_to_umami(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "ALLURE_ENDPOINT", "https://example.testops.cloud")
    monkeypatch.setattr(settings, "ALLURE_PROJECT_ID", 999)

    service = TelemetryService(
        enabled=True,
        umami_base_url="https://cloud.umami.is",
        umami_website_id="website-1",
        umami_hostname="lucius.test",
        hash_salt="integration-salt",
    )
    route = respx.post("https://cloud.umami.is/api/send").mock(return_value=httpx.Response(204))

    service.emit_startup_event()
    service.emit_tool_usage_event(tool_name="search_test_cases", outcome="success", duration_ms=55.0)
    await service.drain()

    assert route.call_count == 2

    startup_event = json.loads(route.calls[0].request.content.decode("utf-8"))["payload"]
    tool_event = json.loads(route.calls[1].request.content.decode("utf-8"))["payload"]
    startup_payload = startup_event["data"]
    tool_payload = tool_event["data"]

    assert startup_event["name"] == "startup"
    assert tool_event["name"] == "tool_use"
    assert startup_payload["server_version"]
    assert startup_payload["project_id_hash"] != "999"
    assert tool_payload["tool_name"] == "search_test_cases"
    assert tool_payload["outcome"] == "success"
    assert tool_payload["duration_bucket"] == "<100ms"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("error", "expected_category"),
    [
        (AuthenticationError("bad token"), "auth"),
        (httpx.TimeoutException("request timed out"), "api"),
    ],
)
@respx.mock
async def test_tool_error_events_sent_to_umami_transport_boundary(
    monkeypatch: pytest.MonkeyPatch,
    error: Exception,
    expected_category: str,
) -> None:
    monkeypatch.setattr(settings, "ALLURE_ENDPOINT", "https://example.testops.cloud")
    monkeypatch.setattr(settings, "ALLURE_PROJECT_ID", 999)

    service = TelemetryService(
        enabled=True,
        umami_base_url="https://cloud.umami.is",
        umami_website_id="website-1",
        umami_hostname="lucius.test",
        hash_salt="integration-salt",
    )
    route = respx.post("https://cloud.umami.is/api/send").mock(return_value=httpx.Response(204))

    service.emit_tool_usage_event(tool_name="search_test_cases", outcome="error", duration_ms=550.0, error=error)
    await service.drain()

    assert route.call_count == 1

    tool_event = json.loads(route.calls[0].request.content.decode("utf-8"))["payload"]
    tool_payload = tool_event["data"]

    assert tool_event["name"] == "tool_error"
    assert tool_payload["tool_name"] == "search_test_cases"
    assert tool_payload["outcome"] == "error"
    assert tool_payload["error_category"] == expected_category
    assert tool_payload["duration_bucket"] == "500ms-2s"
    assert tool_payload["project_id_hash"] != "999"
