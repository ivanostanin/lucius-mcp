"""Integration tests for plan tools."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.client.generated.models import TestPlanDto
from src.tools.plans import (
    create_test_plan,
    delete_test_plan,
    list_test_plans,
    manage_test_plan_content,
    update_test_plan,
)


def _mock_url_context(project_id: int = 1) -> MagicMock:
    mock_client = MagicMock()
    mock_client.get_base_url.return_value = "https://example.com"
    mock_client.get_project.return_value = project_id
    return mock_client


@pytest.mark.asyncio
async def test_create_test_plan_tool() -> None:
    with patch("src.tools.plans.AllureClient.from_env") as mock_client_ctx:
        mock_client = _mock_url_context()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.plans.PlanService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_plan = TestPlanDto(id=100, name="Plan 100")
            mock_service.create_plan = AsyncMock(return_value=mock_plan)

            output = await create_test_plan(name="Plan 100", test_case_ids=[1, 2], output_format="plain")

            assert "Created Test Plan 100: 'Plan 100'" in output
            assert "Test Plan URL: https://example.com/testplan/100" in output
            mock_service.create_plan.assert_called_once_with(
                name="Plan 100",
                test_case_ids=[1, 2],
                aql_filter=None,
            )


@pytest.mark.asyncio
async def test_create_test_plan_json_includes_url() -> None:
    with patch("src.tools.plans.AllureClient.from_env") as mock_client_ctx:
        mock_client = _mock_url_context(project_id=2)
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.plans.PlanService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_plan = TestPlanDto(id=100, name="Plan 100")
            mock_service.create_plan = AsyncMock(return_value=mock_plan)

            output = await create_test_plan(name="Plan 100", test_case_ids=[1, 2], output_format="json")

            assert output.structured_content["url"] == "https://example.com/testplan/100"


@pytest.mark.asyncio
async def test_update_test_plan_tool() -> None:
    with patch("src.tools.plans.AllureClient.from_env") as mock_client_ctx:
        mock_client = _mock_url_context()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.plans.PlanService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_plan = TestPlanDto(id=100, name="Updated Plan")
            mock_service.update_plan = AsyncMock(return_value=mock_plan)

            output = await update_test_plan(plan_id=100, name="Updated Plan", output_format="plain")

            assert "Updated Test Plan 100: 'Updated Plan'" in output
            assert "Test Plan URL: https://example.com/testplan/100" in output
            mock_service.update_plan.assert_called_once_with(plan_id=100, name="Updated Plan")


@pytest.mark.asyncio
async def test_manage_test_plan_content_tool() -> None:
    with patch("src.tools.plans.AllureClient.from_env") as mock_client_ctx:
        mock_client = _mock_url_context()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.plans.PlanService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            # manage content returns a plan but tool returns string
            mock_service.update_plan_content = AsyncMock()

            output = await manage_test_plan_content(plan_id=100, add_test_case_ids=[10], output_format="plain")

            assert "Updated content for Test Plan 100" in output
            assert "Test Plan URL: https://example.com/testplan/100" in output
            mock_service.update_plan_content.assert_called_once_with(
                plan_id=100, test_case_ids_add=[10], test_case_ids_remove=None, aql_filter=None
            )


@pytest.mark.asyncio
async def test_list_test_plans_tool() -> None:
    with patch("src.tools.plans.AllureClient.from_env") as mock_client_ctx:
        mock_client = _mock_url_context()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.plans.PlanService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_plans = [
                TestPlanDto(id=1, name="P1", test_cases_count=5),
                TestPlanDto(id=2, name="P2", test_cases_count=0),
            ]
            mock_service.list_plans = AsyncMock(return_value=mock_plans)

            output = await list_test_plans(page=0, size=10, output_format="plain")

            assert "[1] P1 (5 cases)" in output
            assert "[2] P2 (0 cases)" in output
            assert "Test Plan URL: https://example.com/testplan/1" in output
            assert "Test Plan URL: https://example.com/testplan/2" in output
            mock_service.list_plans.assert_called_once_with(page=0, size=10)


@pytest.mark.asyncio
async def test_delete_test_plan_tool() -> None:
    with patch("src.tools.plans.AllureClient.from_env") as mock_client_ctx:
        mock_client = _mock_url_context()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.plans.PlanService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_service.delete_plan = AsyncMock()

            # Test with confirm=True
            output = await delete_test_plan(plan_id=100, confirm=True, output_format="plain")

            assert "Successfully deleted Test Plan 100" in output
            assert "Test Plan URL: https://example.com/testplan/100" in output
            mock_service.delete_plan.assert_called_once_with(plan_id=100)


@pytest.mark.asyncio
async def test_delete_test_plan_no_confirm() -> None:
    # Test without confirmation (should not call service)
    output = await delete_test_plan(plan_id=100, confirm=False, output_format="plain")

    assert "⚠️ Deletion requires confirmation" in output
    assert "confirm=True" in output
