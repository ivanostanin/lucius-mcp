"""Sandbox proof for native launch attachments using API-token authentication."""

from __future__ import annotations

import uuid

import pytest

from src.client import AllureClient
from src.services.launch_service import LaunchService

pytestmark = pytest.mark.asyncio(loop_scope="module")


@pytest.mark.e2e
async def test_native_launch_attachment_accepts_api_token_without_browser_state(api_token: str) -> None:
    """Prove native GET and POST work after removing all browser-auth state."""
    client = AllureClient.from_env()
    async with client:
        client._csrf_token = None
        client.api_client.cookie = None
        client.api_client.default_headers.pop("X-XSRF-TOKEN", None)

        launch = await LaunchService(client).create_launch(name=f"[e2e-{uuid.uuid4().hex[:8]}] native attachment")
        assert launch.id is not None
        try:
            before = await client.list_launch_attachments(launch.id, page=0, size=10)
            created = await client.create_launch_attachment(
                launch.id,
                ("api-token-proof.json", b"{}"),
            )
            after = await client.list_launch_attachments(launch.id, page=0, size=10)
        finally:
            await client.delete_launch(launch.id)

    assert before.content == []
    assert len(created) == 1
    assert created[0].entity == "launch"
    assert created[0].name == "api-token-proof.json"
    assert after.content is not None
    assert any(row.id == created[0].id for row in after.content)
