import os

import pytest

from src.client import AllureClient
from src.services.test_case_service import TestCaseService


@pytest.mark.asyncio
async def test_delete_test_case_e2e() -> None:
    """End-to-end test for deleting a test case."""
    if not os.getenv("ALLURE_ENDPOINT") or not os.getenv("ALLURE_API_TOKEN"):
        pytest.skip("E2E environment variables not set")

    project_id = int(os.getenv("ALLURE_PROJECT_ID", "1"))

    async with AllureClient.from_env() as client:
        service = TestCaseService(client)

        # 1. Create a test case to delete
        created = await service.create_test_case(
            project_id=project_id, name="E2E Delete Test", description="Temporary test case for delete verification"
        )
        assert created.id is not None
        test_case_id = created.id

        try:
            # 2. Delete the test case
            result = await service.delete_test_case(test_case_id)

            # Verify deletion result
            assert result.status == "archived"
            assert result.test_case_id == test_case_id
            assert result.name == "E2E Delete Test"

            # 3. Verify Idempotency (delete again)
            result_again = await service.delete_test_case(test_case_id)
            assert result_again.status == "archived"

        finally:
            # Cleanup not needed as we deleted it, but if delete failed, we might want to try again?
            # In soft-delete systems, 'cleanup' is the test itself.
            pass
