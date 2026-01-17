"""Shared fixtures for E2E tests."""

import os
import uuid
from collections.abc import AsyncGenerator

import pytest

from src.client import AllureClient
from tests.e2e.helpers.cleanup import CleanupTracker


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
async def cleanup_tracker(allure_client: AllureClient) -> AsyncGenerator[CleanupTracker]:
    """Track created entities for cleanup.

    This fixture automatically cleans up all tracked test cases after each test.

    Usage in tests:
        async def test_something(cleanup_tracker):
            # Create test case
            test_case_id = ...
            cleanup_tracker.track_test_case(test_case_id)
            # Automatic cleanup happens after test completes
    """
    tracker = CleanupTracker(allure_client)
    yield tracker
    await tracker.cleanup_all()


@pytest.fixture
def test_run_id() -> str:
    """Unique ID for test isolation.

    Returns a unique 8-character prefix to namespace test entities.
    This prevents test collisions when running E2E tests concurrently.

    Usage:
        name = f"[{test_run_id}] Login Test"
    """
    return f"e2e-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def test_case_cleanup() -> list[int]:
    """Track test case IDs for cleanup.

    Usage in tests:
        test_case_cleanup.append(test_case_id)

    The fixture automatically handles cleanup, but tests should also
    clean up in their finally blocks for immediate cleanup.

    NOTE: This fixture is deprecated in favor of cleanup_tracker.
    """
    return []


@pytest.fixture
def pixel_b64() -> str:
    """Base64 encoded 1x1 pixel image."""
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAAAAAA6fptVAAAACklEQVR4nGNiAAAABgANjd8qAAAAAElFTkSuQmCC"
