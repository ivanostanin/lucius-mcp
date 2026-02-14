"""Service for managing test hierarchy suites in Allure TestOps."""

from dataclasses import dataclass

from src.client import AllureClient
from src.client.exceptions import AllureNotFoundError, AllureValidationError
from src.client.generated.models.id_and_name_only_dto import IdAndNameOnlyDto
from src.client.generated.models.page_tree_dto_v2 import PageTreeDtoV2
from src.client.generated.models.test_case_full_tree_node_dto import TestCaseFullTreeNodeDto
from src.client.generated.models.test_case_light_tree_node_dto import TestCaseLightTreeNodeDto
from src.client.generated.models.test_case_tree_leaf_dto_v2 import TestCaseTreeLeafDtoV2
from src.client.generated.models.tree_dto_v2 import TreeDtoV2

MAX_NAME_LENGTH = 255


@dataclass
class SuiteNode:
    """Normalized suite node for hierarchy output."""

    id: int
    name: str
    children: list[SuiteNode]


class TestHierarchyService:
    """Service for suite hierarchy orchestration."""

    def __init__(self, client: AllureClient) -> None:
        """Initialize hierarchy service."""
        self._client = client
        self._project_id = client.get_project()

    async def create_test_suite(
        self,
        name: str,
        tree_id: int | None = None,
        parent_suite_id: int | None = None,
    ) -> TestCaseLightTreeNodeDto:
        """Create a new suite node (group) in hierarchy.

        If parent_suite_id is provided, new suite is nested under it.
        """
        self._validate_suite_name(name)

        target_tree = await self._resolve_tree(tree_id)
        target_tree_id = self._require_positive_id(target_tree.id, "Tree ID")

        parent_id: int | None = None
        if parent_suite_id is not None:
            parent_id = self._require_positive_id(parent_suite_id, "Parent suite ID")
            await self._ensure_suite_exists(target_tree_id, parent_id)

        return await self._client.upsert_tree_group(
            project_id=self._project_id,
            tree_id=target_tree_id,
            name=name.strip(),
            parent_node_id=parent_id,
        )

    async def list_test_suites(
        self,
        tree_id: int | None = None,
        include_empty: bool = True,
    ) -> tuple[TreeDtoV2, list[SuiteNode]]:
        """List suite hierarchy for a tree."""
        target_tree = await self._resolve_tree(tree_id)
        target_tree_id = self._require_positive_id(target_tree.id, "Tree ID")

        root = await self._fetch_tree_node(tree_id=target_tree_id, parent_suite_id=None)
        root_id = self._require_positive_id(root.id, "Root suite ID")

        suites = await self._extract_suite_nodes(
            tree_id=target_tree_id,
            root=root,
            include_empty=include_empty,
            visited_nodes=set(),
            parent_suite_id=root_id,
        )
        return target_tree, suites

    async def assign_test_cases_to_suite(
        self,
        suite_id: int,
        test_case_ids: list[int],
        tree_id: int | None = None,
    ) -> int:
        """Assign test cases to a suite via bulk drag-and-drop.

        Returns number of unique assigned test cases.
        """
        target_suite_id = self._require_positive_id(suite_id, "Suite ID")
        normalized_ids = self._normalize_test_case_ids(test_case_ids)

        target_tree = await self._resolve_tree(tree_id)
        target_tree_id = self._require_positive_id(target_tree.id, "Tree ID")

        await self._ensure_suite_exists(target_tree_id, target_suite_id)

        leaf_node_ids = await self._resolve_leaf_node_ids(
            tree_id=target_tree_id,
            test_case_ids=normalized_ids,
        )

        await self._client.assign_test_cases_to_tree_node(
            project_id=self._project_id,
            test_case_ids=leaf_node_ids,
            target_node_id=target_suite_id,
            tree_id=target_tree_id,
        )
        return len(normalized_ids)

    async def resolve_suite_id_by_name(
        self,
        name: str,
        tree_id: int | None = None,
    ) -> IdAndNameOnlyDto | None:
        """Resolve suite ID by exact name using suggest endpoint."""
        if not isinstance(name, str) or not name.strip():
            raise AllureValidationError("Suite name is required")

        target_tree = await self._resolve_tree(tree_id)
        target_tree_id = self._require_positive_id(target_tree.id, "Tree ID")

        suggestions = await self._client.suggest_tree_groups(
            project_id=self._project_id,
            tree_id=target_tree_id,
            query=name.strip(),
            page=0,
            size=100,
        )

        content = suggestions.content if isinstance(suggestions.content, list) else []
        for item in content:
            if isinstance(item, IdAndNameOnlyDto) and item.name == name.strip():
                return item
        return None

    async def _resolve_tree(self, tree_id: int | None) -> TreeDtoV2:
        """Resolve tree by explicit ID or choose default project tree."""
        if tree_id is not None:
            target_tree_id = self._require_positive_id(tree_id, "Tree ID")
            return await self._client.get_tree(target_tree_id)

        trees_page: PageTreeDtoV2 = await self._client.list_trees(project_id=self._project_id, page=0, size=100)
        trees = trees_page.content or []
        if not trees:
            raise AllureNotFoundError(
                message=(
                    f"No hierarchy trees found for project {self._project_id}. "
                    "Create a tree in Allure TestOps before managing suites."
                )
            )

        for tree in trees:
            if tree.project_id == self._project_id:
                return tree

        return trees[0]

    async def _ensure_suite_exists(self, tree_id: int, suite_id: int) -> None:
        """Ensure suite node exists in the target tree."""
        node = await self._client.get_tree_node(
            project_id=self._project_id,
            tree_id=tree_id,
            parent_node_id=suite_id,
            page=0,
            size=1,
        )
        if node.id != suite_id:
            raise AllureNotFoundError(
                message=f"Suite ID {suite_id} was not found in tree {tree_id}",
            )

    async def _fetch_tree_node(self, tree_id: int, parent_suite_id: int | None) -> TestCaseFullTreeNodeDto:
        """Fetch tree node from API and validate payload type."""
        node = await self._client.get_tree_node(
            project_id=self._project_id,
            tree_id=tree_id,
            parent_node_id=parent_suite_id,
            page=0,
            size=500,
        )
        if not isinstance(node, TestCaseFullTreeNodeDto):
            raise AllureValidationError("Unable to read hierarchy tree nodes from API response")
        return node

    async def _resolve_leaf_node_ids(self, tree_id: int, test_case_ids: list[int]) -> list[int]:
        """Resolve test case IDs to current tree leaf node IDs."""
        root = await self._fetch_tree_node(tree_id=tree_id, parent_suite_id=None)
        if not root.children or not root.children.content:
            raise AllureNotFoundError("Unable to locate any test case leaf nodes in hierarchy tree")

        leaf_ids_by_test_case: dict[int, int] = {}
        for item in root.children.content:
            actual = item.actual_instance
            if isinstance(actual, TestCaseTreeLeafDtoV2) and actual.test_case_id is not None and actual.id is not None:
                leaf_ids_by_test_case[actual.test_case_id] = actual.id

        leaf_node_ids: list[int] = []
        for test_case_id in test_case_ids:
            leaf_id = leaf_ids_by_test_case.get(test_case_id)
            if leaf_id is None:
                raise AllureNotFoundError(
                    message=f"Test case ID {test_case_id} was not found in tree {tree_id}",
                )
            leaf_node_ids.append(leaf_id)

        return leaf_node_ids

    async def _extract_suite_nodes(
        self,
        tree_id: int,
        root: TestCaseFullTreeNodeDto,
        include_empty: bool,
        visited_nodes: set[int],
        parent_suite_id: int,
    ) -> list[SuiteNode]:
        """Build normalized suite hierarchy from tree-node response."""
        if not root.children or not root.children.content:
            return []

        suites: list[SuiteNode] = []
        for item in root.children.content:
            actual = item.actual_instance
            if not isinstance(actual, TestCaseLightTreeNodeDto):
                continue

            suite_id = self._require_positive_id(actual.id, "Suite ID")
            if suite_id in visited_nodes:
                continue
            if actual.parent_node_id is not None and actual.parent_node_id != parent_suite_id:
                continue

            next_visited = set(visited_nodes)
            next_visited.add(suite_id)

            child_root = await self._fetch_tree_node(tree_id=tree_id, parent_suite_id=suite_id)
            nested = await self._extract_suite_nodes(
                tree_id=tree_id,
                root=child_root,
                include_empty=include_empty,
                visited_nodes=next_visited,
                parent_suite_id=suite_id,
            )

            if include_empty or nested:
                suites.append(
                    SuiteNode(
                        id=suite_id,
                        name=actual.name or "Unnamed suite",
                        children=nested,
                    )
                )

        return suites

    def _normalize_test_case_ids(self, test_case_ids: list[int]) -> list[int]:
        """Validate and deduplicate test case IDs preserving order."""
        if not isinstance(test_case_ids, list) or not test_case_ids:
            raise AllureValidationError("At least one test case ID is required")

        seen: set[int] = set()
        normalized: list[int] = []
        for test_case_id in test_case_ids:
            valid_id = self._require_positive_id(test_case_id, "Test case ID")
            if valid_id not in seen:
                seen.add(valid_id)
                normalized.append(valid_id)

        return normalized

    def _validate_suite_name(self, name: str) -> None:
        """Validate suite name value."""
        if not isinstance(name, str) or not name.strip():
            raise AllureValidationError("Suite name is required")
        if len(name.strip()) > MAX_NAME_LENGTH:
            raise AllureValidationError(f"Suite name too long (max {MAX_NAME_LENGTH})")

    def _require_positive_id(self, value: int | None, label: str) -> int:
        """Ensure ID-like value is a positive integer."""
        if not isinstance(value, int) or value <= 0:
            raise AllureValidationError(f"{label} must be a positive integer")
        return value
