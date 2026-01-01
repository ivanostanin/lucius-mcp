"""Service for handling attachments."""

import base64
import binascii

from src.client import AllureClient
from src.client.exceptions import AllureValidationError
from src.client.models.attachments import AttachmentRow


class AttachmentService:
    """Service for processing and uploading attachments."""

    def __init__(self, client: AllureClient) -> None:
        self._client = client

    async def upload_attachment(self, project_id: int, data: dict[str, str]) -> AttachmentRow:
        """Upload an attachment from base64 content.

        Args:
            project_id: Project ID.
            data: Dictionary with 'name', 'content' (base64), 'content_type'.

        Returns:
            The uploaded attachment info.

        Raises:
            AllureValidationError: If base64 content is invalid or upload fails.
        """
        name = data.get("name")
        content_b64 = data.get("content")
        content_type = data.get("content_type")

        if not name or not content_b64 or not content_type:
            raise AllureValidationError("Attachment data missing required fields")

        try:
            content = base64.b64decode(content_b64)
        except binascii.Error as e:
            raise AllureValidationError("Invalid base64 content") from e

        # Prepare file tuple for httpx: (filename, content, content_type)
        # key 'file' is expected by Allure
        files = {"file": (name, content, content_type)}

        results = await self._client.upload_attachment(project_id, files)

        if not results:
            raise AllureValidationError("Upload returned no results")

        # Return the first (and only) attachment
        return results[0]
