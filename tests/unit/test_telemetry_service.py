import asyncio
import hashlib
import hmac
import json
from pathlib import Path

import httpx
import pytest
import respx

from src.services.telemetry_service import TelemetryService
from src.utils.config import settings


@pytest.mark.asyncio
@respx.mock
async def test_startup_event_payload_and_user_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "ALLURE_ENDPOINT", "https://example.testops.cloud")
    monkeypatch.setattr(settings, "ALLURE_PROJECT_ID", 123)

    service = TelemetryService(
        enabled=True,
        umami_base_url="https://cloud.umami.is/api/send",
        umami_website_id="website-1",
        umami_hostname="lucius.test",
        hash_salt="telemetry-salt",
        mcp_mode="http",
        server_version="1.2.3",
    )
    route = respx.post("https://cloud.umami.is/api/send").mock(return_value=httpx.Response(204))

    service.emit_startup_event()
    await service.drain()

    assert route.called
    request = route.calls.last.request
    body = json.loads(request.content.decode("utf-8"))
    event_payload = body["payload"]
    payload = event_payload["data"]

    assert request.headers["User-Agent"]
    assert body["type"] == "event"
    assert event_payload["name"] == f"startup.{payload['deployment_method']}"
    assert payload["server_version"] == "1.2.3"
    assert payload["mcp_mode"] == "http"
    assert payload["deployment_method"] in {"docker", "mcpb", "uvx+pypi", "cli", "plain-code-checkout"}
    assert payload["project_id_hash"] != "123"
    assert payload["endpoint_host_hash"] != "example.testops.cloud"


@pytest.mark.asyncio
@respx.mock
async def test_tool_event_error_contains_classification(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "ALLURE_ENDPOINT", "https://example.testops.cloud")
    monkeypatch.setattr(settings, "ALLURE_PROJECT_ID", 321)

    service = TelemetryService(
        enabled=True,
        umami_base_url="https://cloud.umami.is",
        umami_website_id="website-1",
        umami_hostname="lucius.test",
        hash_salt="telemetry-salt",
        mcp_mode="stdio",
    )
    route = respx.post("https://cloud.umami.is/api/send").mock(return_value=httpx.Response(204))

    service.emit_tool_usage_event(
        tool_name="create_test_case",
        outcome="error",
        duration_ms=750.0,
        error=ValueError("invalid"),
    )
    await service.drain()

    assert route.called
    body = json.loads(route.calls.last.request.content.decode("utf-8"))
    event_payload = body["payload"]
    payload = event_payload["data"]
    assert event_payload["name"] == "tool_error.validation.create_test_case"
    assert payload["tool_name"] == "create_test_case"
    assert payload["outcome"] == "error"
    assert payload["duration_bucket"] == "500ms-2s"
    assert payload["error_category"] == "validation"


@pytest.mark.asyncio
@respx.mock
async def test_tool_event_non_validation_error_uses_other_error_event() -> None:
    service = TelemetryService(
        enabled=True,
        umami_base_url="https://cloud.umami.is",
        umami_website_id="website-1",
        umami_hostname="lucius.test",
    )
    route = respx.post("https://cloud.umami.is/api/send").mock(return_value=httpx.Response(204))

    service.emit_tool_usage_event(
        tool_name="search_test_cases",
        outcome="error",
        duration_ms=80.0,
        error=RuntimeError("boom"),
    )
    await service.drain()

    assert route.called
    body = json.loads(route.calls.last.request.content.decode("utf-8"))
    event_payload = body["payload"]
    payload = event_payload["data"]
    assert event_payload["name"] == "tool_error.other.search_test_cases"
    assert payload["error_category"] == "unexpected"


@pytest.mark.asyncio
@respx.mock
async def test_opt_out_disables_http_requests() -> None:
    service = TelemetryService(
        enabled=False,
        umami_base_url="https://cloud.umami.is",
        umami_website_id="website-1",
        umami_hostname="lucius.test",
    )
    route = respx.post("https://cloud.umami.is/api/send").mock(return_value=httpx.Response(204))

    service.emit_startup_event()
    service.emit_tool_usage_event(tool_name="list_test_cases", outcome="success", duration_ms=20.0)
    await service.drain()

    assert not route.called


def test_opt_out_does_not_persist_telemetry_state(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    state_dir = tmp_path / "telemetry-state"
    state_dir.mkdir()
    monkeypatch.setattr(TelemetryService, "_telemetry_state_dir", staticmethod(lambda: state_dir))

    TelemetryService(enabled=False)

    assert list(state_dir.iterdir()) == []


def test_telemetry_state_dir_windows_uses_localappdata(monkeypatch: pytest.MonkeyPatch) -> None:
    state_dir = TelemetryService._telemetry_state_dir_for_platform(
        configured_state_dir=None,
        os_name="nt",
        sys_platform="win32",
        env={"LOCALAPPDATA": r"C:\Users\tester\AppData\Local"},
        home_dir=Path("/home/ignored"),
    )

    assert state_dir == Path(r"C:\Users\tester\AppData\Local") / "lucius-mcp"


def test_telemetry_state_dir_windows_falls_back_to_home() -> None:
    state_dir = TelemetryService._telemetry_state_dir_for_platform(
        configured_state_dir=None,
        os_name="nt",
        sys_platform="win32",
        env={"XDG_STATE_HOME": "/var/lib/ignored"},
        home_dir=Path("C:/Users/tester"),
    )

    assert state_dir == Path("C:/Users/tester") / "AppData" / "Local" / "lucius-mcp"


def test_telemetry_state_dir_uses_xdg_on_posix() -> None:
    state_dir = TelemetryService._telemetry_state_dir_for_platform(
        configured_state_dir=None,
        os_name="posix",
        sys_platform="linux",
        env={"XDG_STATE_HOME": "/var/lib/xdg-state"},
        home_dir=Path("/home/ignored"),
    )

    assert state_dir == Path("/var/lib/xdg-state") / "lucius-mcp"


def test_telemetry_state_dir_macos_default() -> None:
    state_dir = TelemetryService._telemetry_state_dir_for_platform(
        configured_state_dir=None,
        os_name="posix",
        sys_platform="darwin",
        env={},
        home_dir=Path("/Users/tester"),
    )

    assert state_dir == Path("/Users/tester") / "Library" / "Application Support" / "lucius-mcp"


def test_telemetry_state_dir_linux_default() -> None:
    state_dir = TelemetryService._telemetry_state_dir_for_platform(
        configured_state_dir=None,
        os_name="posix",
        sys_platform="linux",
        env={},
        home_dir=Path("/home/tester"),
    )

    assert state_dir == Path("/home/tester") / ".local" / "state" / "lucius-mcp"


def test_telemetry_state_dir_explicit_override() -> None:
    state_dir = TelemetryService._telemetry_state_dir_for_platform(
        configured_state_dir="~/custom-state",
        os_name="posix",
        sys_platform="linux",
        env={},
        home_dir=Path("/home/tester"),
    )

    assert state_dir == Path("~/custom-state").expanduser()


def test_state_creation_tolerates_chmod_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    state_dir = tmp_path / "telemetry-state"
    monkeypatch.setattr(TelemetryService, "_telemetry_state_dir", staticmethod(lambda: state_dir))

    def fail_chmod(_path: Path, _mode: int) -> None:
        raise OSError("unsupported chmod")

    monkeypatch.setattr(Path, "chmod", fail_chmod)

    service = TelemetryService(enabled=False, hash_salt="explicit-secret")
    value = service._read_or_create_telemetry_state_value(filename="hash-secret", generator=lambda: "generated-value")

    assert value == "generated-value"
    assert (state_dir / "hash-secret").read_text(encoding="utf-8") == "generated-value"


@pytest.mark.asyncio
@respx.mock
async def test_env_opt_out_disables_http_requests(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "TELEMETRY_ENABLED", False)
    service = TelemetryService(
        umami_base_url="https://cloud.umami.is",
        umami_website_id="website-1",
        umami_hostname="lucius.test",
    )
    route = respx.post("https://cloud.umami.is/api/send").mock(return_value=httpx.Response(204))

    service.emit_startup_event()
    service.emit_tool_usage_event(tool_name="list_test_cases", outcome="success", duration_ms=20.0)
    await service.drain()

    assert service.is_enabled is False
    assert not route.called


def test_env_overrides_umami_website_id_and_hostname(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "TELEMETRY_WEBSITE_ID", "env-website")
    monkeypatch.setattr(settings, "TELEMETRY_HOSTNAME", "env-hostname.test")

    service = TelemetryService(enabled=False)

    assert service._website_id == "env-website"
    assert service._hostname == "env-hostname.test"


def test_explicit_umami_values_override_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "TELEMETRY_WEBSITE_ID", "env-website")
    monkeypatch.setattr(settings, "TELEMETRY_HOSTNAME", "env-hostname.test")

    service = TelemetryService(
        enabled=False,
        umami_website_id="explicit-website",
        umami_hostname="explicit-hostname.test",
    )

    assert service._website_id == "explicit-website"
    assert service._hostname == "explicit-hostname.test"


@pytest.mark.asyncio
@respx.mock
async def test_send_failures_are_swallowed(caplog: pytest.LogCaptureFixture) -> None:
    service = TelemetryService(
        enabled=True,
        umami_base_url="https://cloud.umami.is",
        umami_website_id="website-1",
        umami_hostname="lucius.test",
    )
    respx.post("https://cloud.umami.is/api/send").mock(side_effect=httpx.ConnectError("down"))

    service.emit_tool_usage_event(tool_name="list_test_cases", outcome="success", duration_ms=10.0)
    await service.drain()

    assert "Telemetry emission failed" in caplog.text


def test_hash_identifier_is_deterministic() -> None:
    service = TelemetryService(enabled=False, hash_salt="salt")

    hash_a = service._hash_identifier("abc")
    hash_b = service._hash_identifier("abc")
    hash_c = service._hash_identifier("abcd")

    assert hash_a == hash_b
    assert hash_a != hash_c


def test_sensitive_fields_use_hmac_hashes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "ALLURE_ENDPOINT", "https://sensitive.testops.cloud")
    monkeypatch.setattr(settings, "ALLURE_PROJECT_ID", 456)

    service = TelemetryService(enabled=False, hash_salt="telemetry-salt")
    payload = service._runtime_context()

    expected_project_hash = hmac.new(b"telemetry-salt", b"456", hashlib.sha256).hexdigest()
    expected_host_hash = hmac.new(b"telemetry-salt", b"sensitive.testops.cloud", hashlib.sha256).hexdigest()

    assert payload["project_id_hash"] == expected_project_hash
    assert payload["endpoint_host_hash"] == expected_host_hash
    assert payload["project_id_hash"] != "456"
    assert payload["endpoint_host_hash"] != "sensitive.testops.cloud"


def test_sensitive_fields_are_unknown_without_hash_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(TelemetryService, "_resolve_hash_secret", lambda self, _: None)
    monkeypatch.setattr(TelemetryService, "_resolve_installation_id", lambda self: None)
    monkeypatch.setattr(settings, "ALLURE_ENDPOINT", "https://sensitive.testops.cloud")
    monkeypatch.setattr(settings, "ALLURE_PROJECT_ID", 456)

    service = TelemetryService(enabled=False)
    payload = service._runtime_context()

    assert payload["project_id_hash"] == "unknown"
    assert payload["endpoint_host_hash"] == "unknown"
    assert service._installation_id_hash() == "unknown"


@pytest.mark.asyncio
async def test_tool_event_is_scheduled_async_non_blocking() -> None:
    service = TelemetryService(
        enabled=True,
        umami_base_url="https://cloud.umami.is",
        umami_website_id="website-1",
        umami_hostname="lucius.test",
    )
    entered_send = asyncio.Event()
    release_send = asyncio.Event()

    async def fake_send_event(*, event_name: str, payload: dict[str, str]) -> None:
        assert event_name == "tool_use.list_test_cases"
        assert payload["tool_name"] == "list_test_cases"
        entered_send.set()
        await release_send.wait()

    service._send_event = fake_send_event  # type: ignore[method-assign]

    service.emit_tool_usage_event(tool_name="list_test_cases", outcome="success", duration_ms=5.0)
    assert len(service._pending_tasks) == 1
    task = next(iter(service._pending_tasks))
    assert not task.done()

    await asyncio.wait_for(entered_send.wait(), timeout=1.0)
    release_send.set()
    await service.drain()
    assert not service._pending_tasks
