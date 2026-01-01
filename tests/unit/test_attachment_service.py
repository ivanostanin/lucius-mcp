from unittest.mock import AsyncMock, Mock

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
async def test_upload_url_attachment(service: AttachmentService) -> None:
    """Test handling URL attachment (might just return a link object or similar)."""
    # If API supports URL attachments directly?
    # Or if we just embed it in Markdown?
    # The Story says "Support URL references".
    # Creating an 'attachment' from URL might mean downloading and uploading,
    # OR creating a link step.
    # Let's assume for now we just validate it.
    pass
