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
