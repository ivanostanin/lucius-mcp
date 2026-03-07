"""Integration tests for cleanup tools."""

from unittest.mock import AsyncMock, patch

import pytest

from src.tools.cleanup import (
    DESTRUCTIVE_CONFIRMATION_MESSAGE,
    delete_archived_shared_steps,
    delete_archived_test_cases,
    delete_unused_custom_fields,
)


@pytest.mark.asyncio
async def test_delete_archived_test_cases_requires_confirmation() -> None:
    with patch("src.tools.cleanup.TestCaseService") as mock_service_cls:
        output = await delete_archived_test_cases(confirm=False)
        assert output == DESTRUCTIVE_CONFIRMATION_MESSAGE
        mock_service_cls.assert_not_called()


@pytest.mark.asyncio
async def test_delete_archived_test_cases_output() -> None:
    with patch("src.tools.cleanup.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.cleanup.TestCaseService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_service.cleanup_archived = AsyncMock(return_value=4)

            output = await delete_archived_test_cases(confirm=True)

            assert output == "Deleted 4 archived test case(s)."
            mock_service.cleanup_archived.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_archived_shared_steps_requires_confirmation() -> None:
    with patch("src.tools.cleanup.SharedStepService") as mock_service_cls:
        output = await delete_archived_shared_steps(confirm=False)
        assert output == DESTRUCTIVE_CONFIRMATION_MESSAGE
        mock_service_cls.assert_not_called()


@pytest.mark.asyncio
async def test_delete_archived_shared_steps_output() -> None:
    with patch("src.tools.cleanup.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.cleanup.SharedStepService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_service.cleanup_archived = AsyncMock(return_value=2)

            output = await delete_archived_shared_steps(confirm=True)

            assert output == "Deleted 2 archived shared step(s)."
            mock_service.cleanup_archived.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_unused_custom_fields_requires_confirmation() -> None:
    with patch("src.tools.cleanup.CustomFieldService") as mock_service_cls:
        output = await delete_unused_custom_fields(confirm=False)
        assert output == DESTRUCTIVE_CONFIRMATION_MESSAGE
        mock_service_cls.assert_not_called()


@pytest.mark.asyncio
async def test_delete_unused_custom_fields_output() -> None:
    with patch("src.tools.cleanup.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.cleanup.CustomFieldService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_service.cleanup_unused = AsyncMock(return_value=3)

            output = await delete_unused_custom_fields(confirm=True)

            assert output == "Deleted 3 unused custom field(s)."
            mock_service.cleanup_unused.assert_awaited_once()
