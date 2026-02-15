"""Unit tests for TestHierarchyService."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.client import AllureClient
from src.client.exceptions import AllureNotFoundError, AllureValidationError
from src.client.generated.models.id_and_name_only_dto import IdAndNameOnlyDto
from src.client.generated.models.node_type import NodeType
from src.client.generated.models.page_id_and_name_only_dto import PageIdAndNameOnlyDto
from src.client.generated.models.page_test_case_tree_node_dto import PageTestCaseTreeNodeDto
from src.client.generated.models.page_test_case_tree_node_dto_content_inner import PageTestCaseTreeNodeDtoContentInner
from src.client.generated.models.page_tree_dto_v2 import PageTreeDtoV2
from src.client.generated.models.test_case_full_tree_node_dto import TestCaseFullTreeNodeDto
from src.client.generated.models.test_case_light_tree_node_dto import TestCaseLightTreeNodeDto
from src.client.generated.models.test_case_tree_leaf_dto_v2 import TestCaseTreeLeafDtoV2
from src.client.generated.models.tree_dto_v2 import TreeDtoV2
from src.services.test_hierarchy_service import SuiteNode, TestHierarchyService


@pytest.fixture
def mock_client() -> MagicMock:
    """Create a mock AllureClient with hierarchy methods."""
    client = MagicMock(spec=AllureClient)
    client.get_project.return_value = 1

    client.list_trees = AsyncMock()
    client.get_tree = AsyncMock()
    client.get_tree_node = AsyncMock()
    client.upsert_tree_group = AsyncMock()
    client.assign_test_cases_to_tree_node = AsyncMock()
    client.suggest_tree_groups = AsyncMock()

    return client


@pytest.fixture
def service(mock_client: MagicMock) -> TestHierarchyService:
    """Create TestHierarchyService with mocked client."""
    return TestHierarchyService(client=mock_client)


def _root_with_suites() -> TestCaseFullTreeNodeDto:
    child_suite = TestCaseLightTreeNodeDto(id=12, name="Auth", type=NodeType.GROUP)
    parent_suite = TestCaseLightTreeNodeDto(
        id=11,
        name="UI",
        type=NodeType.GROUP,
        children=PageTestCaseTreeNodeDto(content=[PageTestCaseTreeNodeDtoContentInner(actual_instance=child_suite)]),
    )
    return TestCaseFullTreeNodeDto(
        id=10,
        name="Root",
        children=PageTestCaseTreeNodeDto(content=[PageTestCaseTreeNodeDtoContentInner(actual_instance=parent_suite)]),
    )


@pytest.mark.asyncio
async def test_create_test_suite_uses_default_tree(service: TestHierarchyService, mock_client: MagicMock) -> None:
    """Create suite without tree_id resolves project tree and upserts group."""
    mock_client.list_trees.return_value = PageTreeDtoV2(
        content=[TreeDtoV2(id=101, name="Main", project_id=1, custom_fields_project=[])]
    )
    mock_client.upsert_tree_group.return_value = TestCaseLightTreeNodeDto(id=501, name="Payments", type=NodeType.GROUP)

    created = await service.create_test_suite(name="Payments")

    assert created.id == 501
    mock_client.list_trees.assert_called_once_with(project_id=1, page=0, size=100)
    mock_client.upsert_tree_group.assert_called_once_with(
        project_id=1,
        tree_id=101,
        name="Payments",
        parent_node_id=None,
    )


@pytest.mark.asyncio
async def test_create_test_suite_nested_validates_parent(service: TestHierarchyService, mock_client: MagicMock) -> None:
    """Nested suite creation validates parent existence before upsert."""
    mock_client.get_tree.return_value = TreeDtoV2(id=200, name="Main", project_id=1, custom_fields_project=[])
    mock_client.get_tree_node.return_value = TestCaseFullTreeNodeDto(
        id=11,
        name="UI",
        children=PageTestCaseTreeNodeDto(content=[]),
    )
    mock_client.upsert_tree_group.return_value = TestCaseLightTreeNodeDto(id=502, name="Login", type=NodeType.GROUP)

    created = await service.create_test_suite(name="Login", tree_id=200, parent_suite_id=11)

    assert created.id == 502
    mock_client.get_tree.assert_called_once_with(200)
    mock_client.get_tree_node.assert_called_once_with(project_id=1, tree_id=200, parent_node_id=11, page=0, size=1)


@pytest.mark.asyncio
async def test_create_test_suite_invalid_name(service: TestHierarchyService) -> None:
    """Empty suite name fails validation."""
    with pytest.raises(AllureValidationError, match="Suite name is required"):
        await service.create_test_suite(name="")


@pytest.mark.asyncio
async def test_create_test_suite_missing_tree_raises_not_found(
    service: TestHierarchyService, mock_client: MagicMock
) -> None:
    """Missing trees in project raises typed not-found error."""
    mock_client.list_trees.return_value = PageTreeDtoV2(content=[])

    with pytest.raises(AllureNotFoundError, match="No hierarchy trees found"):
        await service.create_test_suite(name="Smoke")


@pytest.mark.asyncio
async def test_list_test_suites_returns_hierarchy(service: TestHierarchyService, mock_client: MagicMock) -> None:
    """List suites returns normalized nested hierarchy."""
    mock_client.get_tree.return_value = TreeDtoV2(id=333, name="Tree A", project_id=1, custom_fields_project=[])
    mock_client.get_tree_node.side_effect = [
        _root_with_suites(),
        TestCaseFullTreeNodeDto(
            id=11,
            name="UI",
            children=PageTestCaseTreeNodeDto(
                content=[
                    PageTestCaseTreeNodeDtoContentInner(
                        actual_instance=TestCaseLightTreeNodeDto(
                            id=12,
                            name="Auth",
                            type=NodeType.GROUP,
                            parent_node_id=11,
                        )
                    )
                ]
            ),
        ),
        TestCaseFullTreeNodeDto(id=12, name="Auth", children=PageTestCaseTreeNodeDto(content=[])),
    ]

    tree, suites = await service.list_test_suites(tree_id=333)

    assert tree.id == 333
    assert len(suites) == 1
    top = suites[0]
    assert isinstance(top, SuiteNode)
    assert top.id == 11
    assert top.name == "UI"
    assert len(top.children) == 1
    assert top.children[0].id == 12


@pytest.mark.asyncio
async def test_list_test_suites_invalid_tree_id(service: TestHierarchyService) -> None:
    """Invalid tree_id fails validation."""
    with pytest.raises(AllureValidationError, match="Tree ID must be a positive integer"):
        await service.list_test_suites(tree_id=0)


@pytest.mark.asyncio
async def test_assign_test_cases_to_suite_success(service: TestHierarchyService, mock_client: MagicMock) -> None:
    """Assign test cases deduplicates IDs and calls bulk assignment."""
    mock_client.get_tree.return_value = TreeDtoV2(id=200, name="Main", project_id=1, custom_fields_project=[])

    suite_node = TestCaseFullTreeNodeDto(
        id=11,
        name="UI",
        children=PageTestCaseTreeNodeDto(content=[]),
    )
    root_node = TestCaseFullTreeNodeDto(
        id=10,
        name="Root",
        children=PageTestCaseTreeNodeDto(
            content=[
                PageTestCaseTreeNodeDtoContentInner(
                    actual_instance=TestCaseTreeLeafDtoV2(
                        id=9001,
                        name="Case 1001",
                        test_case_id=1001,
                        type=NodeType.LEAF,
                    )
                ),
                PageTestCaseTreeNodeDtoContentInner(
                    actual_instance=TestCaseTreeLeafDtoV2(
                        id=9002,
                        name="Case 1002",
                        test_case_id=1002,
                        type=NodeType.LEAF,
                    )
                ),
            ]
        ),
    )

    mock_client.get_tree_node.side_effect = [suite_node, root_node]

    assigned = await service.assign_test_cases_to_suite(suite_id=11, test_case_ids=[1001, 1001, 1002], tree_id=200)

    assert assigned == 2
    mock_client.assign_test_cases_to_tree_node.assert_called_once_with(
        project_id=1,
        test_case_ids=[9001, 9002],
        target_node_id=11,
        tree_id=200,
    )


@pytest.mark.asyncio
async def test_assign_test_cases_to_suite_invalid_ids(service: TestHierarchyService) -> None:
    """Invalid test case ID list fails validation."""
    with pytest.raises(AllureValidationError, match="At least one test case ID is required"):
        await service.assign_test_cases_to_suite(suite_id=11, test_case_ids=[])

    with pytest.raises(AllureValidationError, match="Test case ID must be a positive integer"):
        await service.assign_test_cases_to_suite(suite_id=11, test_case_ids=[1, -2])


@pytest.mark.asyncio
async def test_assign_test_cases_to_suite_missing_suite_raises(
    service: TestHierarchyService, mock_client: MagicMock
) -> None:
    """Assign fails with typed not-found when suite node is absent."""
    mock_client.get_tree.return_value = TreeDtoV2(id=200, name="Main", project_id=1, custom_fields_project=[])
    root_node = TestCaseFullTreeNodeDto(
        id=10,
        name="Root",
        children=PageTestCaseTreeNodeDto(content=[]),
    )
    mock_client.get_tree_node.return_value = root_node

    with pytest.raises(AllureNotFoundError, match="Suite ID 999 was not found"):
        await service.assign_test_cases_to_suite(suite_id=999, test_case_ids=[123], tree_id=200)


@pytest.mark.asyncio
async def test_assign_test_cases_to_suite_missing_leaf_raises(
    service: TestHierarchyService, mock_client: MagicMock
) -> None:
    """Assign fails when selected test case does not exist in tree leaves."""
    mock_client.get_tree.return_value = TreeDtoV2(id=200, name="Main", project_id=1, custom_fields_project=[])
    suite_node = TestCaseFullTreeNodeDto(
        id=11,
        name="UI",
        children=PageTestCaseTreeNodeDto(content=[]),
    )
    root_node = TestCaseFullTreeNodeDto(
        id=10,
        name="Root",
        children=PageTestCaseTreeNodeDto(
            content=[
                PageTestCaseTreeNodeDtoContentInner(
                    actual_instance=TestCaseTreeLeafDtoV2(
                        id=9000,
                        name="Case 1000",
                        test_case_id=1000,
                        type=NodeType.LEAF,
                    )
                )
            ]
        ),
    )
    mock_client.get_tree_node.side_effect = [suite_node, root_node]

    with pytest.raises(AllureNotFoundError, match="Test case ID 9999 was not found"):
        await service.assign_test_cases_to_suite(suite_id=11, test_case_ids=[9999], tree_id=200)


@pytest.mark.asyncio
async def test_resolve_suite_id_by_name_match(service: TestHierarchyService, mock_client: MagicMock) -> None:
    """Resolve suite by exact name from suggest endpoint."""
    mock_client.get_tree.return_value = TreeDtoV2(id=300, name="Main", project_id=1, custom_fields_project=[])
    mock_client.suggest_tree_groups.return_value = PageIdAndNameOnlyDto(
        content=[IdAndNameOnlyDto(id=10, name="Backend"), IdAndNameOnlyDto(id=11, name="Frontend")],
    )

    result = await service.resolve_suite_id_by_name(name="Frontend", tree_id=300)

    assert result is not None
    assert result.id == 11


@pytest.mark.asyncio
async def test_resolve_suite_id_by_name_no_match(service: TestHierarchyService, mock_client: MagicMock) -> None:
    """Resolve suite returns None when no exact name match exists."""
    mock_client.get_tree.return_value = TreeDtoV2(id=300, name="Main", project_id=1, custom_fields_project=[])
    mock_client.suggest_tree_groups.return_value = PageIdAndNameOnlyDto(
        content=[IdAndNameOnlyDto(id=10, name="Backend")]
    )

    result = await service.resolve_suite_id_by_name(name="Frontend", tree_id=300)

    assert result is None
