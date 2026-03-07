import json

import httpx
import pytest
import respx

from src.services.telemetry_service import TelemetryService
from src.utils.config import settings


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

    assert startup_event["name"] == f"startup.{startup_payload['deployment_method']}"
    assert tool_event["name"] == "tool_use.search_test_cases"
    assert startup_payload["server_version"]
    assert startup_payload["project_id_hash"] != "999"
    assert tool_payload["tool_name"] == "search_test_cases"
    assert tool_payload["outcome"] == "success"
    assert tool_payload["duration_bucket"] == "<100ms"
