"""Service for handling attachments."""

import base64
import binascii

import httpx

from src.client import AllureClient
from src.client.exceptions import AllureValidationError
from src.client.generated.models import TestCaseAttachmentRowDto

# Default limits
MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "image/gif",
    "text/plain",
    "text/csv",
    "application/json",
    "application/pdf",
    "application/zip",
    "video/mp4",
}


class AttachmentService:
    """Service for processing and uploading attachments."""

    def __init__(self, client: AllureClient) -> None:
        self._client = client

    async def upload_attachment(self, test_case_id: int, data: dict[str, str]) -> TestCaseAttachmentRowDto:
        """Upload an attachment from base64 content or URL.

        Args:
            test_case_id: Test case ID to attach the file to.
            data: Dictionary with:
                  - 'name': Filename (required)
                  - 'content_type': MIME type (required)
                  - 'content': Base64 encoded content (optional, exclusive with url)
                  - 'url': URL to download content from (optional, exclusive with content)

        Returns:
            The uploaded attachment info.

        Raises:
            AllureValidationError: If data is invalid, download fails, or upload fails.
        """
        name = data.get("name")
        content_type = data.get("content_type")

        if not name or not content_type:
            raise AllureValidationError("Attachment data missing required fields (name, content_type)")

        if content_type not in ALLOWED_MIME_TYPES:
            # Basic check, though usually we'd want to inspect bytes.
            # For a thin tool/service layer, trusting the declared type with a whitelist is a good start.
            raise AllureValidationError(f"Content-Type '{content_type}' is not allowed or supported.")

        content = await self._retrieve_content(data)

        if len(content) > MAX_ATTACHMENT_SIZE:
            raise AllureValidationError(
                f"Attachment size {len(content)} bytes exceeds limit of {MAX_ATTACHMENT_SIZE} bytes"
            )

        # Prepare file data for the generated API: list of file entries
        file_data: list[bytes | str | tuple[str, bytes]] = [(name, content)]

        results = await self._client.upload_attachment(test_case_id, file_data)

        if not results:
            raise AllureValidationError("Upload returned no results")

        # Return the first (and only) attachment
        return results[0]

    async def _retrieve_content(self, data: dict[str, str]) -> bytes:
        """Retrieve content from base64 string or URL."""
        content_b64 = data.get("content")
        url = data.get("url")

        if content_b64:
            if url:
                raise AllureValidationError("Cannot specify both 'content' and 'url' for attachment")
            try:
                return base64.b64decode(content_b64)
            except binascii.Error as e:
                raise AllureValidationError("Invalid base64 content") from e
        elif url:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, follow_redirects=True, timeout=10.0)
                    response.raise_for_status()
                    return response.content
            except httpx.RequestError as e:
                raise AllureValidationError(f"Failed to download attachment from {url}: {e!s}") from e
            except httpx.HTTPStatusError as e:
                raise AllureValidationError(
                    f"Failed to download attachment from {url}: HTTP {e.response.status_code}"
                ) from e

        raise AllureValidationError("Attachment must have either 'content' or 'url'")
