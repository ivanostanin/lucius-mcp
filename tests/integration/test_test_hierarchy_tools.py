"""Integration tests for test hierarchy tools."""

from unittest.mock import AsyncMock, patch

import pytest

from src.client.generated.models.tree_dto_v2 import TreeDtoV2
from src.services.test_hierarchy_service import SuiteNode
from src.tools.assign_test_cases_to_suite import assign_test_cases_to_suite
from src.tools.create_test_suite import create_test_suite
from src.tools.list_test_suites import list_test_suites


@pytest.mark.asyncio
async def test_create_test_suite_output_format() -> None:
    """create_test_suite returns concise success output."""
    with patch("src.tools.create_test_suite.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.create_test_suite.TestHierarchyService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            created_suite = type("SuiteDto", (), {"id": 25, "name": "Payments"})
            mock_service.create_test_suite = AsyncMock(return_value=created_suite)

            output = await create_test_suite(name="Payments", project_id=1, tree_id=200, parent_suite_id=11)

            assert "✅ Test suite created successfully!" in output
            assert "ID: 25" in output
            assert "Name: Payments" in output
            mock_service.create_test_suite.assert_called_once_with(name="Payments", tree_id=200, parent_suite_id=11)


@pytest.mark.asyncio
async def test_list_test_suites_output_hierarchical() -> None:
    """list_test_suites prints hierarchical suite output."""
    with patch("src.tools.list_test_suites.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.list_test_suites.TestHierarchyService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            tree = TreeDtoV2(id=101, name="Main Tree", project_id=1, custom_fields_project=[])
            suites = [
                SuiteNode(
                    id=10,
                    name="Backend",
                    children=[SuiteNode(id=11, name="API", children=[])],
                )
            ]
            mock_service.list_test_suites = AsyncMock(return_value=(tree, suites))

            output = await list_test_suites(project_id=1, tree_id=101, include_empty=True)

            assert "Tree: Main Tree (ID: 101)" in output
            assert "Found 1 top-level suites:" in output
            assert "- ID: 10, Name: Backend" in output
            assert "  - ID: 11, Name: API" in output


@pytest.mark.asyncio
async def test_list_test_suites_empty_tree_message() -> None:
    """list_test_suites handles empty suite list."""
    with patch("src.tools.list_test_suites.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.list_test_suites.TestHierarchyService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            tree = TreeDtoV2(id=12, name="Core", project_id=1, custom_fields_project=[])
            mock_service.list_test_suites = AsyncMock(return_value=(tree, []))

            output = await list_test_suites(project_id=1)

            assert output == "Tree 'Core' (ID: 12) has no suites."


@pytest.mark.asyncio
async def test_assign_test_cases_to_suite_output() -> None:
    """assign_test_cases_to_suite reports assigned count."""
    with patch("src.tools.assign_test_cases_to_suite.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.assign_test_cases_to_suite.TestHierarchyService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_service.assign_test_cases_to_suite = AsyncMock(return_value=3)

            output = await assign_test_cases_to_suite(
                suite_id=44, test_case_ids=[100, 101, 102], project_id=1, tree_id=2
            )

            assert output == "✅ Assigned 3 test case(s) to suite 44."
            mock_service.assign_test_cases_to_suite.assert_called_once_with(
                suite_id=44,
                test_case_ids=[100, 101, 102],
                tree_id=2,
            )
