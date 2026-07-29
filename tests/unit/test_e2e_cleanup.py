"""Unit tests for E2E cleanup helpers."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from tests.e2e.helpers.cleanup import CleanupTracker


@pytest.mark.asyncio
async def test_delete_test_case_strict_accepts_missing_case_as_cleaned() -> None:
    tracker = CleanupTracker(MagicMock())
    service = MagicMock()
    service.delete_test_case = AsyncMock(return_value=SimpleNamespace(status="not_found"))

    await tracker.delete_test_case_strict(service, test_case_id=42)

    service.delete_test_case.assert_awaited_once_with(42)
