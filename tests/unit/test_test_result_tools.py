"""Unit coverage for the exact test-result MCP tool."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.test_result_service import TestRunResultDetail
from src.tools.launches import get_test_result
from src.tools.output_schemas import TestResultDetailOutput
from src.utils.telemetry import _apply_mcp_output_contract


@pytest.mark.asyncio
async def test_get_test_result_forwards_exact_id_and_renders_partial_diagnostics() -> None:
    with patch("src.tools.launches.AllureClient.from_env") as mock_client_ctx:
        mock_client = MagicMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client
        with patch("src.tools.launches.TestResultService") as mock_service_cls:
            mock_service_cls.return_value.get_test_result = AsyncMock(
                return_value=TestRunResultDetail(
                    actual_launch_id=9,
                    test_result_id=10,
                    project_id=1,
                    result_url="https://example.com/launch/9/tree/10",
                    launch_url="https://example.com/launch/9",
                    test_case=None,
                    core={"name": "Result", "status": "failed"},
                    custom_fields=(),
                    environment=(),
                    members=(),
                    test_keys=(),
                    issues=(),
                    defects=(),
                    execution_steps=(),
                    fixtures=(),
                    result_attachments=(),
                    related_results=(),
                    partial=True,
                    unavailable_sections=(),
                )
            )

            plain = await get_test_result(10)
            output = await get_test_result(10, output_format="json")

    assert mock_service_cls.return_value.get_test_result.await_count == 2
    validated = _apply_mcp_output_contract(output, TestResultDetailOutput)
    assert validated.structured_content["test_result_id"] == 10
    assert validated.structured_content["custom_fields"] == []

    assert '"execution_steps": []' in plain
    assert '"partial": true' in plain
