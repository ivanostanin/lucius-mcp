from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.client import AllureClient
from src.services.attachment_service import AttachmentService


@pytest.fixture
def mock_client() -> AsyncMock:
    return AsyncMock(spec=AllureClient)


@pytest.fixture
def service(mock_client: AsyncMock) -> AttachmentService:
    return AttachmentService(mock_client)


@pytest.mark.asyncio
async def test_upload_base64_attachment(service: AttachmentService, mock_client: AsyncMock) -> None:
    """Test uploading a base64 encoded attachment."""
    project_id = 1
    attachment_data = {
        "name": "image.png",
        "content": "SGVsbG8=",  # "Hello" in base64
        "content_type": "image/png",
    }
    result_mock = Mock()
    result_mock.id = 500
    mock_client.upload_attachment.return_value = [result_mock]

    result = await service.upload_attachment(project_id, attachment_data)

    assert result == result_mock
    mock_client.upload_attachment.assert_called_once()
    # verify decoding happening if service handles decoding, OR client handles it?
    # Usually service prepares file/content.
    # checking call args
    call_args = mock_client.upload_attachment.call_args
    assert call_args[0][0] == project_id
    # arg 1 should be file content or tuple.
    # Let's assume client takes list of files or single file tuple.
    # We'll refine client signature expectation in service implementation.


@pytest.mark.asyncio
async def test_upload_url_attachment(service: AttachmentService, mock_client: AsyncMock) -> None:
    """Test uploading an attachment from a URL."""
    project_id = 1
    url = "http://example.com/logo.png"
    attachment_data = {
        "name": "logo.png",
        "url": url,
        "content_type": "image/png",
    }

    # Mock Allure upload result
    result_mock = Mock()
    result_mock.id = 501
    mock_client.upload_attachment.return_value = [result_mock]

    # Mock httpx response
    mock_response = Mock()
    mock_response.content = b"downloaded-content"
    mock_response.raise_for_status = Mock()

    # Patch httpx.AsyncClient
    with patch("src.services.attachment_service.httpx.AsyncClient") as mock_httpx_cls:
        mock_client_instance = AsyncMock()
        mock_httpx_cls.return_value.__aenter__.return_value = mock_client_instance
        mock_client_instance.get.return_value = mock_response

        result = await service.upload_attachment(project_id, attachment_data)

        assert result == result_mock

        # Verify download triggered
        mock_client_instance.get.assert_called_with(url, follow_redirects=True, timeout=10.0)

        # Verify upload triggered with downloaded content
        mock_client.upload_attachment.assert_called_once()
        files = mock_client.upload_attachment.call_args[0][1]
        assert files["file"] == ("logo.png", b"downloaded-content", "image/png")
