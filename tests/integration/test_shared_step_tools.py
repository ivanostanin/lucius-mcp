"""Integration tests for shared-step tool wrappers."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.tools.shared_steps import create_shared_step, list_shared_steps


@pytest.mark.asyncio
async def test_create_shared_step_uses_resolved_project_context_in_url() -> None:
    with patch("src.tools.shared_steps.AllureClient.from_env") as mock_client_ctx:
        mock_client = MagicMock()
        mock_client.get_project.return_value = 456
        mock_client.get_base_url.return_value = "https://example.com"
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.shared_steps.SharedStepService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_shared_step = type("SharedStepDto", (), {"id": 11, "name": "Login as Admin", "project_id": 456})
            mock_service.create_shared_step = AsyncMock(return_value=mock_shared_step)

            output = await create_shared_step(name="Login as Admin", output_format="json")

            payload = json.loads(output)
            assert payload["project_id"] == 456
            assert payload["url"] == "https://example.com/project/456/settings/shared-steps/11"


@pytest.mark.asyncio
async def test_list_shared_steps_uses_resolved_project_context_in_plain_output() -> None:
    with patch("src.tools.shared_steps.AllureClient.from_env") as mock_client_ctx:
        mock_client = MagicMock()
        mock_client.get_project.return_value = 456
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.shared_steps.SharedStepService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_step = type("SharedStepDto", (), {"id": 12, "name": "Login as Admin", "steps_count": 2})
            mock_service.list_shared_steps = AsyncMock(return_value=[mock_step])

            output = await list_shared_steps(search="Login", output_format="plain")

            assert "project 456" in output
            assert "project None" not in output
            assert "[ID: 12] Login as Admin (2 steps)" in output
