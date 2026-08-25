"""Integration coverage for exact test-result facade reads."""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import SecretStr

from src.client import AllureClient
from src.client.generated.models.custom_field_with_values_dto import CustomFieldWithValuesDto
from src.client.generated.models.page_test_result_history_dto import PageTestResultHistoryDto


def _client() -> AllureClient:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    return client


@pytest.mark.asyncio
async def test_client_exact_result_enrichment_wrappers_call_generated_controllers() -> None:
    client = _client()
    client._test_result_custom_field_api = MagicMock()
    client._test_result_api = MagicMock()
    custom_fields = [CustomFieldWithValuesDto(values=[])]
    history = PageTestResultHistoryDto(content=[], last=True, number=0)
    client._test_result_custom_field_api.get_custom_fields_with_values1 = AsyncMock(return_value=custom_fields)
    client._test_result_api.find_history = AsyncMock(return_value=history)
    client._test_result_api.find_retries = AsyncMock(return_value=history)

    assert await client.get_test_result_custom_fields(12) == custom_fields
    assert await client.get_test_result_history(12, page=0, size=100) == history
    assert await client.get_test_result_retries(12, page=0, size=100) == history

    client._test_result_custom_field_api.get_custom_fields_with_values1.assert_awaited_once()
    client._test_result_api.find_history.assert_awaited_once()
    client._test_result_api.find_retries.assert_awaited_once()
