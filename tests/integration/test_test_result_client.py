"""Integration coverage for exact test-result facade reads."""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from pydantic import SecretStr

from src.client import AllureClient
from src.client.exceptions import AllureNotFoundError
from src.client.generated.exceptions import ApiException


def _client() -> AllureClient:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    return client


@pytest.mark.asyncio
async def test_client_exact_result_enrichment_wrappers_call_generated_controllers() -> None:
    client = _client()
    client._test_result_custom_field_api = MagicMock()
    client._test_result_defect_api = MagicMock()
    client._test_result_env_var_api = MagicMock()
    client._test_result_issue_api = MagicMock()
    client._test_result_members_api = MagicMock()
    client._test_result_test_key_api = MagicMock()
    client._test_fixture_result_attachment_api = MagicMock()
    client._test_result_api = MagicMock()
    custom_fields = object()
    defects = object()
    environment = object()
    issues = object()
    members = object()
    test_keys = object()
    history = object()
    retries = object()
    fixture_content = httpx.Response(200, content=b"fixture evidence")
    client._test_result_custom_field_api.get_custom_fields_with_values1 = AsyncMock(return_value=custom_fields)
    client._test_result_defect_api.get_defects = AsyncMock(return_value=defects)
    client._test_result_env_var_api.get_env_var_values = AsyncMock(return_value=environment)
    client._test_result_issue_api.get_issues = AsyncMock(return_value=issues)
    client._test_result_members_api.get_members = AsyncMock(return_value=members)
    client._test_result_test_key_api.get_keys = AsyncMock(return_value=test_keys)
    client._test_fixture_result_attachment_api.read_content1_without_preload_content = AsyncMock(
        return_value=fixture_content
    )
    client._test_result_api.find_history = AsyncMock(return_value=history)
    client._test_result_api.find_retries = AsyncMock(return_value=retries)

    assert await client.get_test_result_custom_fields(12) is custom_fields
    assert await client.get_test_result_defects(12, page=2, size=50, sort=["name,ASC"]) is defects
    assert await client.get_test_result_environment(12) is environment
    assert await client.get_test_result_issues(12) is issues
    assert await client.get_test_result_members(12) is members
    assert await client.get_test_result_test_keys(12) is test_keys
    assert await client.read_test_result_fixture_attachment_content(15) == b"fixture evidence"
    assert await client.get_test_result_history(12, page=0, size=100) is history
    assert await client.get_test_result_retries(12, page=0, size=100) is retries

    client._test_result_custom_field_api.get_custom_fields_with_values1.assert_awaited_once_with(
        test_result_id=12, _request_timeout=client._timeout
    )
    client._test_result_defect_api.get_defects.assert_awaited_once_with(
        test_result_id=12, page=2, size=50, sort=["name,ASC"], _request_timeout=client._timeout
    )
    client._test_result_env_var_api.get_env_var_values.assert_awaited_once_with(
        test_result_id=12, _request_timeout=client._timeout
    )
    client._test_result_issue_api.get_issues.assert_awaited_once_with(
        test_result_id=12, _request_timeout=client._timeout
    )
    client._test_result_members_api.get_members.assert_awaited_once_with(
        test_result_id=12, _request_timeout=client._timeout
    )
    client._test_result_test_key_api.get_keys.assert_awaited_once_with(
        test_result_id=12, _request_timeout=client._timeout
    )
    client._test_fixture_result_attachment_api.read_content1_without_preload_content.assert_awaited_once_with(
        id=15, inline=False, _request_timeout=client._timeout
    )
    client._test_result_api.find_history.assert_awaited_once_with(
        id=12, page=0, size=100, sort=None, _request_timeout=client._timeout
    )
    client._test_result_api.find_retries.assert_awaited_once_with(
        id=12, page=0, size=100, sort=None, _request_timeout=client._timeout
    )


@pytest.mark.asyncio
async def test_client_test_case_attachment_facade_uses_authenticated_generated_requests() -> None:
    client = _client()
    client._attachment_api = MagicMock()
    list_response = httpx.Response(
        200,
        json={"content": [{"id": 15, "name": "evidence.txt", "contentType": "text/plain"}], "last": True},
    )
    content_response = httpx.Response(
        200,
        content=b"case evidence",
        headers={"content-type": "text/plain", "content-disposition": 'attachment; filename="evidence.txt"'},
    )
    client._attachment_api.find_all13_without_preload_content = AsyncMock(return_value=list_response)
    client._attachment_api.read_content2_without_preload_content = AsyncMock(return_value=content_response)

    attachments = await client.list_test_case_attachments(12, page=0, size=100)
    content = await client.read_test_case_attachment(15)

    assert attachments.content is not None
    assert attachments.content[0].id == 15
    assert content.data == b"case evidence"
    assert content.content_type == "text/plain"
    assert content.filename == "evidence.txt"
    client._attachment_api.find_all13_without_preload_content.assert_awaited_once_with(
        test_case_id=12, page=0, size=100, sort=None, _request_timeout=client._timeout
    )
    client._attachment_api.read_content2_without_preload_content.assert_awaited_once_with(
        id=15, inline=False, _request_timeout=client._timeout
    )


@pytest.mark.asyncio
async def test_attachment_content_errors_are_translated_without_echoing_response_bodies() -> None:
    client = _client()
    client._test_result_attachment_api = MagicMock()
    client._test_result_attachment_api.read_content_without_preload_content = AsyncMock(
        return_value=httpx.Response(404, text="sensitive upstream attachment URL")
    )

    with pytest.raises(AllureNotFoundError) as error:
        await client.read_test_result_attachment(15)

    assert "sensitive upstream" not in str(error.value)


@pytest.mark.asyncio
async def test_client_exact_result_execution_sends_v2_and_translates_errors() -> None:
    client = _client()
    client._api_client = MagicMock()
    client._api_client.param_serialize.return_value = (
        "GET",
        "https://example.com/api/testresult/12/execution",
        {},
        None,
        [],
    )
    client._api_client.call_api = AsyncMock(return_value=httpx.Response(200, json={"steps": []}))

    assert await client.get_test_result_execution_raw(12, v2=True) == {"steps": []}
    client._api_client.param_serialize.assert_called_once_with(
        method="GET",
        resource_path="/api/testresult/{id}/execution",
        path_params={"id": 12},
        query_params=[("v2", True)],
        header_params={},
        auth_settings=[],
    )

    client._test_result_issue_api = MagicMock()
    client._test_result_issue_api.get_issues = AsyncMock(
        side_effect=ApiException(status=404, reason="Not Found", body="{}")
    )
    with pytest.raises(AllureNotFoundError, match="Resource not found"):
        await client.get_test_result_issues(12)
