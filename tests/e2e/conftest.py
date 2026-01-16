"""Shared fixtures for E2E tests."""

import os
from collections.abc import AsyncGenerator

import pytest

from src.client import AllureClient


@pytest.fixture
def project_id() -> int:
    """Get project ID from environment."""
    return int(os.getenv("ALLURE_PROJECT_ID", "1"))


@pytest.fixture
async def allure_client() -> AsyncGenerator[AllureClient]:
    """Provide an authenticated AllureClient for E2E tests."""
    async with AllureClient.from_env() as client:
        yield client


@pytest.fixture
def test_case_cleanup() -> list[int]:
    """Track test case IDs for cleanup.

    Usage in tests:
        test_case_cleanup.append(test_case_id)

    The fixture automatically handles cleanup, but tests should also
    clean up in their finally blocks for immediate cleanup.
    """
    return []
