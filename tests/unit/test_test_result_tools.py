"""Unit coverage for the exact test-result MCP tool."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

from src.services.test_result_service import AttachmentDetail, TestRunResultDetail
from src.tools.launches import get_test_result
from src.tools.output_schemas import TestResultDetailOutput
from src.utils.telemetry import _apply_mcp_output_contract


@pytest.mark.asyncio
async def test_get_test_result_forwards_exact_id_and_renders_partial_diagnostics(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ALLURE_API_TOKEN", raising=False)
    monkeypatch.delenv("ALLURE_ENDPOINT", raising=False)
    monkeypatch.delenv("ALLURE_PROJECT_ID", raising=False)

    with patch("src.tools.launches._launch_client_context") as mock_client_context:
        mock_client = MagicMock()
        mock_client_context.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_context.return_value.__aexit__ = AsyncMock(return_value=False)
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
                    result_attachments=(
                        AttachmentDetail(
                            attachment_id=22,
                            attachment_kind="test_result",
                            test_result_id=10,
                            test_case_id=None,
                            name="evidence.txt",
                            entity="test_result",
                            content_type="text/plain",
                            content_length=8,
                            missed=False,
                            from_test_case=False,
                            storage_key=None,
                        ),
                    ),
                    related_results=(),
                    partial=True,
                    unavailable_sections=(),
                )
            )

            output = await get_test_result(10)
            plain = await get_test_result(10, output_format="plain")

    assert mock_client_context.call_args_list == [call(project_id=None), call(project_id=None)]
    assert mock_service_cls.call_args_list == [call(mock_client), call(mock_client)]
    assert mock_service_cls.return_value.get_test_result.await_args_list == [call(10), call(10)]
    validated = _apply_mcp_output_contract(output, TestResultDetailOutput)
    assert validated.structured_content["test_result_id"] == 10
    assert validated.structured_content["custom_fields"] == []
    assert validated.structured_content["result_attachments"] == [
        {
            "attachment_id": 22,
            "attachment_kind": "test_result",
            "test_result_id": 10,
            "test_case_id": None,
            "name": "evidence.txt",
            "entity": "test_result",
            "content_type": "text/plain",
            "content_length": 8,
            "missed": False,
            "from_test_case": False,
            "storage_key": None,
        }
    ]

    assert '"execution_steps": []' in plain
    assert '"partial": true' in plain
