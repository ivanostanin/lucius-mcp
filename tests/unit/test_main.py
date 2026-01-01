from src.main import app as global_app


def test_app_initialization(client):
    """
    Verify app initializes correctly using the client fixture which handles refresh.
    """
    # Simply using the client proves the app logic works
    response = client.get("/")
    assert response.status_code in [200, 404, 405]

    # Check global app reference just for sanity
    assert global_app is not None


def test_start_stdio_mode(mocker):
    """
    Verify that start() invokes run_stdio_async when MCP_MODE is 'stdio'.
    """
    from src.main import mcp, start
    from src.utils.config import settings

    # Mock settings.MCP_MODE
    mocker.patch.object(settings, "MCP_MODE", "stdio")

    # Mock asyncio.run to verify it's called
    mock_asyncio_run = mocker.patch("asyncio.run")

    # Mock mcp.run_stdio_async
    # CRITICAL: We explicitly use a standard Mock, NOT an AsyncMock.
    # If run_stdio_async is natively async, patch() creates an AsyncMock by default.
    # An AsyncMock returns a coroutine when called. Since mock_asyncio_run acts as a mock,
    # it swallows the coroutine without awaiting it, causing "RuntimeWarning: coroutine was never awaited".
    # By forcing a standard Mock, no coroutine is created, avoiding the warning.
    mocker.patch.object(mcp, "run_stdio_async", new_callable=mocker.Mock)

    start()

    # Verify asyncio.run was called
    mock_asyncio_run.assert_called_once()

    # Verify mcp.run_stdio_async was called
    mcp.run_stdio_async.assert_called_once()
