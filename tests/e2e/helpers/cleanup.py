"""Helper utilities for E2E test isolation and cleanup."""

from src.client import AllureClient
from src.services import CustomFieldValueService, DefectService, PlanService, TestHierarchyService, TestLayerService


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
        self._test_layers: list[int] = []
        self._test_suites: list[int] = []
        self._test_plans: list[int] = []
        self._defects: list[int] = []
        self._custom_field_value_names: list[str] = []

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

    def track_test_layer(self, layer_id: int) -> None:
        """Track a test layer for cleanup.

        Args:
            layer_id: ID of the shared step to track
        """
        self._test_layers.append(layer_id)

    def track_test_suite(self, suite_id: int) -> None:
        """Track a test suite for cleanup.

        Args:
            suite_id: ID of the test suite to track
        """
        self._test_suites.append(suite_id)

    def track_test_plan(self, plan_id: int) -> None:
        """Track a test plan for cleanup.

        Args:
            plan_id: ID of the test plan to track
        """
        self._test_plans.append(plan_id)

    def track_defect(self, defect_id: int) -> None:
        """Track a defect for cleanup.

        Args:
            defect_id: ID of the defect to track
        """
        self._defects.append(defect_id)

    def track_custom_field_value_name(self, value_name: str) -> None:
        """Track a custom field value name for cleanup across project fields.

        This is useful when tests create values implicitly via hierarchy mappings
        and don't receive a direct value ID.

        Args:
            value_name: Value name to remove from any project custom field.
        """
        normalized = value_name.strip()
        if normalized:
            self._custom_field_value_names.append(normalized)

    async def cleanup_all(self) -> None:
        """Delete all tracked entities.

        Performs best-effort cleanup - silently ignores errors if entities
        are already deleted or inaccessible.
        """
        await self._cleanup_test_cases()
        await self._cleanup_shared_steps()
        await self._cleanup_test_layers()
        await self._cleanup_test_suites()
        await self._cleanup_test_plans()
        await self._cleanup_defects()
        await self._cleanup_custom_field_values()

    async def _cleanup_test_cases(self) -> None:
        import logging

        logger = logging.getLogger(__name__)
        for tc_id in self._test_cases:
            try:
                await self._client.delete_test_case(tc_id)
            except Exception as e:
                logger.warning(f"Failed to cleanup test case {tc_id}: {e}")

    async def _cleanup_shared_steps(self) -> None:
        import logging

        logger = logging.getLogger(__name__)
        for step_id in self._shared_steps:
            try:
                await self._client.delete_shared_step(step_id)
            except Exception as e:
                logger.warning(f"Failed to cleanup shared step {step_id}: {e}")

    async def _cleanup_test_layers(self) -> None:
        import logging

        logger = logging.getLogger(__name__)
        layers_service = TestLayerService(self._client)
        for layer_id in self._test_layers:
            try:
                await layers_service.delete_test_layer(layer_id=layer_id)
            except Exception as e:
                logger.warning(f"Failed to cleanup test layer {layer_id}: {e}")

    async def _cleanup_test_suites(self) -> None:
        import logging

        logger = logging.getLogger(__name__)
        hierarchy_service = TestHierarchyService(self._client)
        for suite_id in reversed(self._test_suites):
            try:
                await hierarchy_service.delete_test_suite(suite_id=suite_id)
            except Exception as e:
                logger.warning(f"Failed to cleanup test suite {suite_id}: {e}")

    async def _cleanup_test_plans(self) -> None:
        import logging

        logger = logging.getLogger(__name__)
        plan_service = PlanService(self._client)
        for plan_id in self._test_plans:
            try:
                await plan_service.delete_plan(plan_id)
            except Exception as e:
                logger.warning(f"Failed to cleanup test plan {plan_id}: {e}")

    async def _cleanup_defects(self) -> None:
        import logging

        logger = logging.getLogger(__name__)
        defect_service = DefectService(self._client)
        for defect_id in self._defects:
            try:
                await defect_service.delete_defect(defect_id)
            except Exception as e:
                logger.warning(f"Failed to cleanup defect {defect_id}: {e}")

    async def _cleanup_custom_field_values(self) -> None:
        import logging

        logger = logging.getLogger(__name__)
        if not self._custom_field_value_names:
            return

        tracked_names = set(self._custom_field_value_names)

        try:
            project_id = self._client.get_project()
            project_fields = await self._client.get_custom_fields_with_values(project_id)
        except Exception as e:
            logger.warning(f"Failed to enumerate project custom fields for cleanup: {e}")
            return

        cf_value_service = CustomFieldValueService(self._client)
        for field in project_fields:
            custom_field = getattr(field, "custom_field", None)
            custom_field_name = getattr(custom_field, "name", None)
            if not isinstance(custom_field_name, str) or not custom_field_name.strip():
                continue

            values = getattr(field, "values", None) or []
            present_names: set[str] = set()
            for value in values:
                if isinstance(value, str):
                    present_names.add(value)
                    continue
                value_name = getattr(value, "name", None)
                if isinstance(value_name, str):
                    present_names.add(value_name)

            for matched_name in sorted(tracked_names.intersection(present_names)):
                try:
                    await cf_value_service.delete_custom_field_value(
                        custom_field_name=custom_field_name,
                        cfv_name=matched_name,
                        force=True,
                    )
                except Exception as e:
                    logger.warning(
                        "Failed to cleanup custom field value '%s' from field '%s': %s",
                        matched_name,
                        custom_field_name,
                        e,
                    )
