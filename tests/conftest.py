import importlib
import sys

import pytest
import umami
from starlette.applications import Starlette
from starlette.routing import Mount

from src.utils.config import settings

settings.MCP_MODE = "http"

# Fixtures are imported via pytest_plugins to avoid re-import warnings
pytest_plugins = [
    "tests.support.fixtures.base",
    "tests.support.fixtures.logger_fixture",
    "tests.support.fixtures.client_fixture",
    "tests.support.fixtures.allure_client_fixture",
]


@pytest.fixture(autouse=True)
def _resolve_tool_patch_targets_on_python_310(monkeypatch: pytest.MonkeyPatch) -> None:
    """Expose tool modules for Python 3.10's stricter ``unittest.mock.patch`` lookup."""
    if sys.version_info >= (3, 11):
        return

    import src.tools as tools

    module_by_export = {
        "assign_test_cases_to_suite": "src.tools.assign_test_cases_to_suite",
        "create_custom_field_value": "src.tools.create_custom_field_value",
        "create_test_case": "src.tools.create_test_case",
        "create_test_layer": "src.tools.create_test_layer",
        "create_test_layer_schema": "src.tools.create_test_layer_schema",
        "create_test_suite": "src.tools.create_test_suite",
        "delete_custom_field_value": "src.tools.delete_custom_field_value",
        "delete_test_case": "src.tools.delete_test_case",
        "delete_test_layer": "src.tools.delete_test_layer",
        "delete_test_layer_schema": "src.tools.delete_test_layer_schema",
        "delete_test_suite": "src.tools.delete_test_suite",
        "get_custom_fields": "src.tools.get_custom_fields",
        "get_test_case_custom_fields": "src.tools.get_test_case_custom_fields",
        "link_shared_step": "src.tools.link_shared_step",
        "list_custom_field_values": "src.tools.list_custom_field_values",
        "list_test_layer_schemas": "src.tools.list_test_layer_schemas",
        "list_test_layers": "src.tools.list_test_layers",
        "list_test_suites": "src.tools.list_test_suites",
        "unlink_shared_step": "src.tools.unlink_shared_step",
        "update_custom_field_value": "src.tools.update_custom_field_value",
        "update_test_case": "src.tools.update_test_case",
        "update_test_layer": "src.tools.update_test_layer",
        "update_test_layer_schema": "src.tools.update_test_layer_schema",
    }
    for export_name, module_name in module_by_export.items():
        monkeypatch.setattr(tools, export_name, importlib.import_module(module_name))


@pytest.fixture
def app() -> Starlette:
    """
    Fixture that returns the Starlette application with a FRESH FastMCP session manager.
    FastMCP's StreamableHTTPSessionManager is single-use, so we must recreate
    the mcp_asgi app and update the global app references for each test.
    """
    import src.main

    # 1. Generate a new ASGI app from the global mcp instance
    # This creates a new StreamableHTTPSessionManager
    new_asgi = src.main.mcp.http_app()

    # 2. Update the internal variable so get_mcp_asgi() and subsequent calls use the new one
    src.main._mcp_asgi = new_asgi

    # 3. Update the Starlette app's routes to point to the new ASGI app
    # We find the Mount for "/" and replace it
    # Note: Accessing/modifying routes list directly.
    # The routes list contains Route or Mount objects.
    for i, route in enumerate(src.main.app.routes):
        if isinstance(route, Mount) and route.path == "/":
            src.main.app.routes[i] = Mount("/", app=new_asgi)
            break

    return src.main.app


@pytest.fixture
def umami_async_post_recorder(monkeypatch: pytest.MonkeyPatch):
    def factory(
        *,
        status_code: int = 200,
        response_json: dict[str, object] | None = None,
        side_effect: Exception | None = None,
    ) -> list[dict[str, object]]:
        calls: list[dict[str, object]] = []

        class FakeAsyncClient:
            async def __aenter__(self) -> "FakeAsyncClient":
                return self

            async def __aexit__(self, exc_type: object, exc: object, tb: object) -> bool:
                return False

            async def post(
                self,
                url: str,
                *,
                json: dict[str, object] | None = None,
                headers: dict[str, str] | None = None,
                follow_redirects: bool = False,
                **kwargs: object,
            ):
                calls.append(
                    {
                        "url": url,
                        "json": json,
                        "headers": headers or {},
                        "follow_redirects": follow_redirects,
                        "kwargs": kwargs,
                    }
                )
                if side_effect is not None:
                    raise side_effect

                request = umami.impl.httpx.Request("POST", url, headers=headers)
                return umami.impl.httpx.Response(status_code, json=response_json or {"ok": True}, request=request)

        monkeypatch.setattr(umami.impl.httpx, "AsyncClient", FakeAsyncClient)
        return calls

    return factory
