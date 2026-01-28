"""Shared fixtures for E2E tests."""

import os
import uuid
from collections.abc import AsyncGenerator

import pytest

from src.client import AllureClient
from src.utils.auth import get_auth_context
from tests.e2e.helpers.cleanup import CleanupTracker


@pytest.fixture
def project_id() -> int:
    """Get project ID from environment."""
    project_id = os.getenv("ALLURE_PROJECT_ID", "0")
    project_id = int(project_id) if project_id else 0
    if project_id <= 0:
        pytest.skip("ALLURE_PROJECT_ID must be a positive integer")
    return project_id


@pytest.fixture
async def allure_client(project_id: int) -> AsyncGenerator[AllureClient]:
    """Provide an authenticated AllureClient for E2E tests."""
    # Prioritize sandbox credentials if available
    base_url = os.getenv("ALLURE_ENDPOINT")
    token = os.getenv("ALLURE_API_TOKEN")

    if not base_url or not token:
        pytest.skip("Sandbox credentials not configured (ALLURE_ENDPOINT/ALLURE_API_TOKEN)")

    auth_context = get_auth_context(api_token=token)

    # We can't use AllureClient.from_env() because we might be using sandbox vars
    # preventing internal env var conflict if standard vars are also set.
    async with AllureClient(
        base_url=base_url,
        token=auth_context.api_token,
        project=project_id,
    ) as client:
        yield client


@pytest.fixture
def api_token() -> str:
    token = os.getenv("ALLURE_API_TOKEN")
    if not token:
        pytest.skip("Sandbox credentials not configured (ALLURE_API_TOKEN)")
    return token


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
def pixel_b64() -> str:
    """Base64 encoded 1x1 pixel image."""
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAAAAAA6fptVAAAACklEQVR4nGNiAAAABgANjd8qAAAAAElFTkSuQmCC"
