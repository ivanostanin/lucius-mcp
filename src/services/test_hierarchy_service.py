"""Service for managing test hierarchy suites in Allure TestOps."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

import httpx

from src.client import AllureClient
from src.client.exceptions import AllureAPIError, AllureNotFoundError, AllureValidationError
from src.client.generated.models.id_and_name_only_dto import IdAndNameOnlyDto
from src.client.generated.models.page_tree_dto_v2 import PageTreeDtoV2
from src.client.generated.models.test_case_full_tree_node_dto import TestCaseFullTreeNodeDto
from src.client.generated.models.test_case_light_tree_node_dto import TestCaseLightTreeNodeDto
from src.client.generated.models.test_case_tree_leaf_dto_v2 import TestCaseTreeLeafDtoV2
from src.client.generated.models.tree_dto_v2 import TreeDtoV2

MAX_NAME_LENGTH = 255
MAX_CONCURRENT_TREE_NODE_REQUESTS = 8
TREE_SNAPSHOT_ATTEMPTS = 3
logger = logging.getLogger(__name__)


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
        for attempt in range(TREE_SNAPSHOT_ATTEMPTS):
            try:
                # Resolve the tree as part of each attempt: a transient failure
                # here invalidates the whole snapshot just as much as a node read.
                target_tree = await self._resolve_tree(tree_id)
                target_tree_id = self._require_positive_id(target_tree.id, "Tree ID")
                fetch_limiter = asyncio.Semaphore(MAX_CONCURRENT_TREE_NODE_REQUESTS)
                root = await self._fetch_tree_node(
                    tree_id=target_tree_id,
                    parent_suite_id=None,
                    fetch_limiter=fetch_limiter,
                )
                root_id = self._require_positive_id(root.id, "Root suite ID")
                suites = await self._extract_suite_nodes(
                    tree_id=target_tree_id,
                    root=root,
                    include_empty=include_empty,
                    visited_nodes=set(),
                    parent_suite_id=root_id,
                    fetch_limiter=fetch_limiter,
                )
                return target_tree, suites
            except (httpx.TransportError, AllureAPIError) as exc:
                if attempt + 1 == TREE_SNAPSHOT_ATTEMPTS or not self._is_retryable_tree_read_error(exc):
                    raise
                logger.warning("Retrying hierarchy snapshot after transient read failure: %s", exc)
                await asyncio.sleep(0.5 * (attempt + 1))

        raise AssertionError("Hierarchy snapshot retry loop exited unexpectedly")

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

    async def delete_suite(self, suite_id: int, tree_id: int | None = None) -> bool:
        """Delete a suite node by ID with idempotent behavior."""
        target_suite_id = self._require_positive_id(suite_id, "Suite ID")

        try:
            await self._client.delete_tree_group(
                project_id=self._project_id,
                group_id=target_suite_id,
            )
        except AllureNotFoundError:
            logger.info("Test suite %s already deleted or not found", target_suite_id)
            return False
        except AllureAPIError as exc:
            fallback_deleted = await self._delete_suite_via_custom_field_value(target_suite_id, tree_id=tree_id)
            if fallback_deleted is True:
                logger.info("Deleted test suite %s via custom-field fallback", target_suite_id)
                return True
            if fallback_deleted is False:
                logger.info("Test suite %s is absent from every project hierarchy tree", target_suite_id)
                return False
            raise exc

        logger.info("Deleted test suite %s", target_suite_id)
        return True

    async def delete_test_suite(self, suite_id: int, tree_id: int | None = None) -> bool:
        """Backward-compatible alias for deleting suite nodes."""
        return await self.delete_suite(suite_id=suite_id, tree_id=tree_id)

    async def resolve_suite_id_by_name(
        self,
        name: str,
        tree_id: int | None = None,
    ) -> IdAndNameOnlyDto | None:
        """Resolve suite ID by exact name using suggest endpoint."""
        if not isinstance(name, str) or not name.strip():
            raise AllureValidationError("Suite name is required")

        normalized_name = name.strip()
        for attempt in range(TREE_SNAPSHOT_ATTEMPTS):
            try:
                target_tree = await self._resolve_tree(tree_id)
                target_tree_id = self._require_positive_id(target_tree.id, "Tree ID")
                page = 0
                while True:
                    suggestions = await self._client.suggest_tree_groups(
                        project_id=self._project_id,
                        tree_id=target_tree_id,
                        query=normalized_name,
                        page=page,
                        size=100,
                    )
                    content = suggestions.content if isinstance(suggestions.content, list) else []
                    for item in content:
                        if isinstance(item, IdAndNameOnlyDto) and item.name == normalized_name:
                            return item

                    total_pages = suggestions.total_pages
                    if not isinstance(total_pages, int) or page + 1 >= total_pages:
                        return None
                    page += 1
            except (httpx.TransportError, AllureAPIError) as exc:
                if attempt + 1 == TREE_SNAPSHOT_ATTEMPTS or not self._is_retryable_tree_read_error(exc):
                    raise
                logger.warning("Retrying suite name resolution after transient read failure: %s", exc)
                await asyncio.sleep(0.5 * (attempt + 1))

        raise AssertionError("Suite resolution retry loop exited unexpectedly")

    async def get_test_case_ids_in_suite(
        self,
        suite_id: int,
        tree_id: int | None = None,
    ) -> list[int]:
        """Return test-case IDs directly assigned to a suite.

        This performs a targeted suite-node read, rather than traversing the
        project hierarchy, so callers can verify an assignment safely in a
        shared project.
        """
        target_suite_id = self._require_positive_id(suite_id, "Suite ID")
        target_tree = await self._resolve_tree(tree_id)
        target_tree_id = self._require_positive_id(target_tree.id, "Tree ID")
        node = await self._fetch_tree_node(tree_id=target_tree_id, parent_suite_id=target_suite_id)
        if node.id != target_suite_id:
            raise AllureNotFoundError(message=f"Suite ID {target_suite_id} was not found in tree {target_tree_id}")

        children = node.children.content if node.children and node.children.content else []
        return [
            actual.test_case_id
            for item in children
            if isinstance((actual := item.actual_instance), TestCaseTreeLeafDtoV2)
            and isinstance(actual.test_case_id, int)
        ]

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

    async def _fetch_tree_node(
        self,
        tree_id: int,
        parent_suite_id: int | None,
        fetch_limiter: asyncio.Semaphore | None = None,
    ) -> TestCaseFullTreeNodeDto:
        """Fetch tree node from API and validate payload type."""

        async def fetch_page(page: int) -> TestCaseFullTreeNodeDto:
            if fetch_limiter is None:
                return await self._get_tree_node(tree_id=tree_id, parent_suite_id=parent_suite_id, page=page)
            async with fetch_limiter:
                return await self._get_tree_node(tree_id=tree_id, parent_suite_id=parent_suite_id, page=page)

        node = await fetch_page(0)
        if not isinstance(node, TestCaseFullTreeNodeDto):
            raise AllureValidationError("Unable to read hierarchy tree nodes from API response")

        children = node.children
        if children is None:
            return node
        total_pages = children.total_pages
        if not isinstance(total_pages, int) or total_pages <= 1:
            return node

        content = list(children.content or [])
        for page in range(1, total_pages):
            next_page = await fetch_page(page)
            if not isinstance(next_page, TestCaseFullTreeNodeDto) or next_page.id != node.id:
                raise AllureValidationError("Unable to read a consistent hierarchy tree page from API response")
            if next_page.children and next_page.children.content:
                content.extend(next_page.children.content)
        node.children = children.model_copy(update={"content": content})
        return node

    async def _get_tree_node(
        self,
        tree_id: int,
        parent_suite_id: int | None,
        page: int,
    ) -> TestCaseFullTreeNodeDto:
        """Read one page of a hierarchy node's children."""
        return await self._client.get_tree_node(
            project_id=self._project_id,
            tree_id=tree_id,
            parent_node_id=parent_suite_id,
            page=page,
            size=500,
        )

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

    async def _delete_suite_via_custom_field_value(self, suite_id: int, tree_id: int | None) -> bool | None:
        """Targeted fallback for an API-erroring suite deletion.

        Returns True when the backing custom-field value was deleted, False when
        no hierarchy tree remains for the project, and None when the requested
        suite cannot be proven absent or has no removable backing value.
        """
        if tree_id is not None:
            candidate_trees = [await self._resolve_tree(tree_id)]
        else:
            trees_page = await self._client.list_trees(project_id=self._project_id, page=0, size=100)
            candidate_trees = trees_page.content or []
            if not candidate_trees:
                return False

        for candidate_tree in candidate_trees:
            candidate_tree_id = self._require_positive_id(candidate_tree.id, "Tree ID")
            try:
                node = await self._fetch_tree_node(tree_id=candidate_tree_id, parent_suite_id=suite_id)
            except AllureNotFoundError:
                continue

            if node.id != suite_id:
                continue

            custom_field_value_id = node.custom_field_value_id
            if not isinstance(custom_field_value_id, int) or custom_field_value_id <= 0:
                return None

            try:
                await self._client.delete_custom_field_value(
                    project_id=self._project_id,
                    cfv_id=custom_field_value_id,
                )
                logger.info(
                    "Deleted suite %s via custom field value %s",
                    suite_id,
                    custom_field_value_id,
                )
                return True
            except AllureNotFoundError:
                logger.info(
                    "Suite %s custom field value %s already removed",
                    suite_id,
                    custom_field_value_id,
                )
                return False

        # A targeted miss does not prove a globally-addressed group was deleted.
        # Propagate the original delete error instead of reporting false success.
        return None

    async def _extract_suite_nodes(
        self,
        tree_id: int,
        root: TestCaseFullTreeNodeDto,
        include_empty: bool,
        visited_nodes: set[int],
        parent_suite_id: int,
        fetch_limiter: asyncio.Semaphore,
    ) -> list[SuiteNode]:
        """Build normalized suite hierarchy with a bounded breadth-first walk."""
        if not root.children or not root.children.content:
            return []

        seen_ids = set(visited_nodes)
        roots: list[SuiteNode] = []
        frontier: list[tuple[TestCaseLightTreeNodeDto, SuiteNode | None, int]] = [
            (actual, None, parent_suite_id)
            for item in root.children.content
            if isinstance((actual := item.actual_instance), TestCaseLightTreeNodeDto)
        ]

        while frontier:
            next_frontier: list[tuple[TestCaseLightTreeNodeDto, SuiteNode | None, int]] = []
            current_level: list[tuple[TestCaseLightTreeNodeDto, SuiteNode]] = []
            for actual, parent, expected_parent_id in frontier:
                suite_id = self._require_positive_id(actual.id, "Suite ID")
                if suite_id in seen_ids or (
                    actual.parent_node_id is not None and actual.parent_node_id != expected_parent_id
                ):
                    continue
                seen_ids.add(suite_id)
                suite = SuiteNode(id=suite_id, name=actual.name or "Unnamed suite", children=[])
                if parent is None:
                    roots.append(suite)
                else:
                    parent.children.append(suite)
                current_level.append((actual, suite))

            for start in range(0, len(current_level), MAX_CONCURRENT_TREE_NODE_REQUESTS):
                batch = current_level[start : start + MAX_CONCURRENT_TREE_NODE_REQUESTS]
                child_roots = await asyncio.gather(
                    *(
                        self._fetch_tree_node(
                            tree_id=tree_id,
                            parent_suite_id=self._require_positive_id(actual.id, "Suite ID"),
                            fetch_limiter=fetch_limiter,
                        )
                        for actual, _suite in batch
                    )
                )
                for (_actual, suite), child_root in zip(batch, child_roots, strict=True):
                    child_items = (
                        child_root.children.content if child_root.children and child_root.children.content else []
                    )
                    next_frontier.extend(
                        (child_actual, suite, suite.id)
                        for child_item in child_items
                        if isinstance((child_actual := child_item.actual_instance), TestCaseLightTreeNodeDto)
                    )
            frontier = next_frontier

        if include_empty:
            return roots

        def exclude_empty(suite: SuiteNode) -> SuiteNode | None:
            suite.children = [
                child for child in (exclude_empty(child) for child in suite.children) if child is not None
            ]
            return suite if suite.children else None

        return [suite for suite in (exclude_empty(root_suite) for root_suite in roots) if suite is not None]

    @staticmethod
    def _is_retryable_tree_read_error(exc: httpx.TransportError | AllureAPIError) -> bool:
        """Identify transient failures that can invalidate a tree snapshot."""
        return isinstance(exc, httpx.TransportError) or (exc.status_code is not None and exc.status_code >= 500)

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
