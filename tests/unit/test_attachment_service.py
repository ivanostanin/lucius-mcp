from types import SimpleNamespace

import pytest

from src.client.exceptions import AllureValidationError
from src.services import attachment_service
from src.services.attachment_service import AttachmentService


@pytest.mark.asyncio
async def test_attachment_upload_uses_configured_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(attachment_service, "MAX_ATTACHMENT_SIZE", 1)
    client = SimpleNamespace(upload_attachment=None)
    service = AttachmentService(client=client)  # type: ignore[arg-type]

    with pytest.raises(AllureValidationError, match="exceeds limit of 1 bytes"):
        await service.upload_attachment(
            10,
            {"name": "evidence.txt", "content_type": "text/plain", "content": "QUI="},
        )


@pytest.mark.asyncio
async def test_attachment_upload_accepts_content_at_configured_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(attachment_service, "MAX_ATTACHMENT_SIZE", 2)

    async def upload_attachment(_test_case_id: int, _files: list[object]) -> list[object]:
        return [SimpleNamespace(id=1, name="evidence.txt")]

    service = AttachmentService(client=SimpleNamespace(upload_attachment=upload_attachment))  # type: ignore[arg-type]

    result = await service.upload_attachment(
        10,
        {"name": "evidence.txt", "content_type": "text/plain", "content": "QUI="},
    )

    assert result.name == "evidence.txt"
