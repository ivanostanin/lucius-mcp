"""Helper utilities for E2E test isolation and cleanup."""

from src.client import AllureClient


class CleanupTracker:
    """Tracks created entities for cleanup after tests.

    This helper ensures test isolation by tracking all entities created during
    a test run and automatically cleaning them up afterwards.

    Usage:
        ```python
        @pytest.fixture
        async def cleanup_tracker(allure_client):
            tracker = CleanupTracker(allure_client)
            yield tracker
            await tracker.cleanup_all()

        async def test_something(cleanup_tracker):
            test_case_id = ...  # Create test case
            cleanup_tracker.track_test_case(test_case_id)
            # Test will auto-cleanup after execution
        ```
    """

    def __init__(self, client: AllureClient) -> None:
        """Initialize cleanup tracker with AllureClient.

        Args:
            client: Authenticated AllureClient instance for API calls
        """
        self._client = client
        self._test_cases: list[int] = []
        self._shared_steps: list[int] = []

    def track_test_case(self, test_case_id: int) -> None:
        """Track a test case for cleanup.

        Args:
            test_case_id: ID of the test case to track
        """
        self._test_cases.append(test_case_id)

    def track_shared_step(self, step_id: int) -> None:
        """Track a shared step for cleanup.

        Args:
            step_id: ID of the shared step to track
        """
        self._shared_steps.append(step_id)

    async def cleanup_all(self) -> None:
        """Delete all tracked entities.

        Performs best-effort cleanup - silently ignores errors if entities
        are already deleted or inaccessible.
        """
        import logging

        logger = logging.getLogger(__name__)

        # Clean up test cases
        for tc_id in self._test_cases:
            try:
                await self._client.delete_test_case(tc_id)
            except Exception as e:
                logger.warning(f"Failed to cleanup test case {tc_id}: {e}")

        # Clean up shared steps
        for step_id in self._shared_steps:
            try:
                await self._client.delete_shared_step(step_id)
            except Exception as e:
                logger.warning(f"Failed to cleanup shared step {step_id}: {e}")
