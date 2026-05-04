"""Coverage-focused tests for AllureClient facade delegation and parsers."""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

import httpx
import pytest
from pydantic import SecretStr

from src.client import (
    AllureAPIError,
    AllureClient,
    AllureValidationError,
)
from src.client.client import AttachmentStepDtoWithName, SharedStepStepDtoWithId, StepWithExpected
from src.client.generated.api.shared_step_attachment_controller_api import SharedStepAttachmentControllerApi
from src.client.generated.api.test_case_attachment_controller_api import TestCaseAttachmentControllerApi
from src.client.generated.exceptions import ApiException
from src.client.generated.models.launch_existing_upload_dto import LaunchExistingUploadDto
from src.client.generated.models.scenario_step_create_dto import ScenarioStepCreateDto
from src.client.generated.models.scenario_step_patch_dto import ScenarioStepPatchDto
from src.client.generated.models.shared_step_patch_dto import SharedStepPatchDto
from src.client.generated.models.test_case_patch_v2_dto import TestCasePatchV2Dto
from src.client.generated.models.test_case_scenario_v2_dto import TestCaseScenarioV2Dto


class RecordingApi:
    def __init__(self, result: object = None) -> None:
        self.result = result if result is not None else SimpleNamespace()
        self.calls: list[tuple[str, tuple[object, ...], dict[str, object]]] = []

    def __getattr__(self, name: str) -> object:
        def call(*args: object, **kwargs: object) -> object:
            self.calls.append((name, args, kwargs))

            async def result() -> object:
                if isinstance(self.result, BaseException):
                    raise self.result
                return self.result

            return result()

        return call


class RawTreeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")


@pytest.fixture
def facade_client(monkeypatch: pytest.MonkeyPatch) -> AllureClient:
    client = AllureClient("https://allure.example.com", SecretStr("token"), project=7)
    client._is_entered = True

    async def no_token_refresh() -> None:
        return None

    monkeypatch.setattr(client, "_ensure_valid_token", no_token_refresh)
    return client


@pytest.mark.asyncio
async def test_basic_facade_accessors_and_api_guards(facade_client: AllureClient) -> None:
    facade_client.set_project(11)

    assert facade_client.get_project() == 11
    assert facade_client.get_base_url() == "https://allure.example.com"
    assert AllureClient._escape_rql_value(r'a\b"c') == r"a\\b\"c"
    assert AllureClient._build_rql_filters('smoke "case"', "Draft", ["p0", "ui"]) == (
        'name~="smoke \\"case\\"" and status="Draft" and tag="p0" and tag="ui"'
    )
    assert AllureClient._validate_positive_int_list([1, 2], "bad ids") == [1, 2]

    with pytest.raises(AllureValidationError, match="bad ids"):
        AllureClient._validate_positive_int_list([1, 0], "bad ids")
    with pytest.raises(RuntimeError, match="async context manager"):
        unentered_client = AllureClient("https://allure.example.com", SecretStr("token"), project=1)
        _ = unentered_client.api_client
    with pytest.raises(AllureAPIError, match="missing_api"):
        await facade_client._get_api("_shared_step_api", error_name="missing_api")


def test_static_response_and_attachment_helpers() -> None:
    assert AllureClient._extract_response_data(httpx.Response(200, json={"ok": True})) == {"ok": True}
    with pytest.raises(ApiException):
        AllureClient._extract_response_data(httpx.Response(204, json=[]))
    with pytest.raises(ApiException):
        AllureClient._extract_response_data(httpx.Response(404, text="missing"))

    assert AllureClient._patch_attachment_with_discriminator({"entity": "unknown"}) == {"entity": "unknown"}
    assert AllureClient._patch_attachment_with_discriminator({"entity": "TestCaseAttachmentRowDto"})["entity"] == (
        "test_case"
    )


def test_denormalizes_complex_scenario_tree() -> None:
    scenario = AllureClient._denormalize_to_v2_from_dict(
        {
            "root": {"children": [1, 2, 3, 999]},
            "scenarioSteps": {
                "1": {"body": "Open form", "children": [4], "expectedResultId": 5},
                "2": {"attachmentId": 22},
                "3": {"sharedStepId": 33},
                "4": {"body": "Nested body"},
                "5": {"body": "Expected Result", "children": [6, 7]},
                "6": {"body": "First expectation"},
                "7": {"body": "Second expectation"},
            },
            "attachments": {"22": {"name": "screen.png"}},
        }
    )

    assert isinstance(scenario, TestCaseScenarioV2Dto)
    assert len(scenario.steps or []) == 3
    body_step = scenario.steps[0].actual_instance
    attachment_step = scenario.steps[1].actual_instance
    shared_step = scenario.steps[2].actual_instance
    assert isinstance(body_step, StepWithExpected)
    assert body_step.body == "Open form"
    assert body_step.expected_result == "First expectation\nSecond expectation"
    assert isinstance(attachment_step, AttachmentStepDtoWithName)
    assert attachment_step.name == "screen.png"
    assert isinstance(shared_step, SharedStepStepDtoWithId)
    assert shared_step.shared_step_id == 33


def test_parse_tree_children_handles_groups_leaves_and_empty_pages(facade_client: AllureClient) -> None:
    assert facade_client._parse_tree_children(None) is None

    empty_page = facade_client._parse_tree_children({"content": "not-a-list", "totalElements": 0})
    assert empty_page is not None
    assert empty_page.content == []

    page = facade_client._parse_tree_children(
        {
            "content": [
                {"id": 10, "name": "Suite", "type": "GROUP", "count": 3},
                {"id": 20, "name": "Case", "type": "LEAF"},
                "ignored",
            ],
            "totalElements": 2,
        }
    )
    assert page is not None
    assert len(page.content or []) == 2


@pytest.mark.asyncio
async def test_search_launch_and_custom_field_delegation(facade_client: AllureClient) -> None:
    launch_api = RecordingApi(SimpleNamespace(status_code=204))
    launch_search_api = RecordingApi(SimpleNamespace(valid=True, count=4))
    search_api = RecordingApi(SimpleNamespace(valid=True, count=2))
    custom_field_values_api = RecordingApi("value-result")
    facade_client._launch_api = launch_api  # type: ignore[assignment]
    facade_client._launch_search_api = launch_search_api  # type: ignore[assignment]
    facade_client._search_api = search_api  # type: ignore[assignment]
    facade_client._custom_field_value_project_api = custom_field_values_api  # type: ignore[assignment]

    assert (await facade_client.get_launch(5)).status_code == 204
    assert await facade_client.close_launch(5) == 204
    await facade_client.reopen_launch(5)
    await facade_client.delete_launch(5)
    assert await facade_client.search_launches_aql(7, 'name = "Run"', sort=["createdDate,DESC"]) == SimpleNamespace(
        valid=True, count=4
    )
    assert await facade_client.validate_launch_query(7, 'name = "Run"') == SimpleNamespace(valid=True, count=4)
    assert await facade_client.search_test_cases_aql(7, 'tag = "smoke"', deleted=True) == SimpleNamespace(
        valid=True, count=2
    )
    assert await facade_client.validate_test_case_query(7, 'tag = "smoke"') == (True, 2)
    assert await facade_client.list_custom_field_values(7, -12, page=0, size=1000) == "value-result"
    await facade_client.update_custom_field_value(7, 22, SimpleNamespace(name="P0"))  # type: ignore[arg-type]
    await facade_client.delete_custom_field_value(7, 22)

    assert [call[0] for call in launch_api.calls] == ["find_one23", "close_with_http_info", "reopen", "delete27"]
    assert [call[0] for call in launch_search_api.calls] == ["search2", "validate_query2"]
    assert [call[0] for call in search_api.calls] == ["search1", "validate_query1"]
    assert [call[0] for call in custom_field_values_api.calls] == ["find_all22", "patch23", "delete47"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("operation", "message"),
    [
        (lambda c: c.get_launch(0), "Launch ID"),
        (lambda c: c.search_launches_aql(0, "x"), "Project ID"),
        (lambda c: c.search_launches_aql(1, " "), "AQL query"),
        (lambda c: c.search_launches_aql(1, "x", page=-1), "Page"),
        (lambda c: c.search_test_cases_aql(1, "x", size=101), "Size"),
        (lambda c: c.list_custom_field_values(1, 0), "Custom Field ID"),
        (lambda c: c.update_custom_field_value(1, 0, SimpleNamespace()), "Custom Field Value ID"),
        (lambda c: c.delete_custom_field_value(0, 1), "Project ID"),
    ],
)
async def test_common_facade_validation_errors(facade_client: AllureClient, operation: Any, message: str) -> None:
    facade_client._launch_api = RecordingApi()  # type: ignore[assignment]
    facade_client._launch_search_api = RecordingApi()  # type: ignore[assignment]
    facade_client._search_api = RecordingApi()  # type: ignore[assignment]
    facade_client._custom_field_value_project_api = RecordingApi()  # type: ignore[assignment]

    with pytest.raises(AllureValidationError, match=message):
        await operation(facade_client)


@pytest.mark.asyncio
async def test_tree_facade_delegation_and_validation(facade_client: AllureClient) -> None:
    tree_api = RecordingApi("tree-result")
    case_tree_api = RecordingApi("node-result")
    bulk_api = RecordingApi("bulk-result")
    facade_client._tree_api = tree_api  # type: ignore[assignment]
    facade_client._test_case_tree_api = case_tree_api  # type: ignore[assignment]
    facade_client._test_case_tree_bulk_api = bulk_api  # type: ignore[assignment]

    assert await facade_client.list_trees(7, with_archived=True, page=0, size=10) == "tree-result"
    assert await facade_client.get_tree(3, with_archived=False) == "tree-result"
    assert await facade_client.create_tree_group(7, 3, " Suite ", parent_node_id=2) == "node-result"
    assert await facade_client.upsert_tree_group(7, 3, "Suite") == "node-result"
    assert await facade_client.rename_tree_group(7, 2, "Renamed") == "node-result"
    await facade_client.delete_tree_group(7, 2)
    assert await facade_client.create_tree_leaf(7, 3, "Leaf", node_id=2) == "node-result"
    assert await facade_client.rename_tree_leaf(7, 2, "Leaf 2") == "node-result"
    await facade_client.assign_test_cases_to_tree_node(7, [1, 2], 4, 3)
    assert (
        await facade_client.suggest_tree_groups(
            7, query="suite", tree_id=3, path=[1], node_ids=[2], ignore_ids=[3], page=0, size=10
        )
        == "node-result"
    )

    assert [call[0] for call in tree_api.calls] == ["find_all48", "find_one38"]
    assert [call[0] for call in bulk_api.calls] == ["drag_and_drop"]
    assert case_tree_api.calls[-1][0] == "suggest1"

    with pytest.raises(AllureValidationError, match="At least one test case ID"):
        await facade_client.assign_test_cases_to_tree_node(7, [], 4, 3)
    with pytest.raises(AllureValidationError, match="All test case IDs"):
        await facade_client.assign_test_cases_to_tree_node(7, [1, -2], 4, 3)
    with pytest.raises(AllureValidationError, match="Suite name"):
        await facade_client.create_tree_group(7, 3, " ")
    with pytest.raises(AllureValidationError, match="Node IDs"):
        await facade_client.suggest_tree_groups(7, node_ids=[0])


@pytest.mark.asyncio
async def test_raw_tree_node_and_scenario_fetching(facade_client: AllureClient) -> None:
    tree_payload = {
        "id": 1,
        "name": "Root",
        "type": "GROUP",
        "children": {"content": [{"id": 2, "name": "Leaf", "type": "LEAF"}], "totalElements": 1},
    }

    async def get_tree_node_without_preload_content(**_kwargs: object) -> RawTreeResponse:
        return RawTreeResponse(tree_payload)

    tree_api = SimpleNamespace(get_tree_node_without_preload_content=get_tree_node_without_preload_content)
    scenario_payload = {
        "root": {"children": [1]},
        "scenarioSteps": {"1": {"body": "Only step"}},
        "attachments": {},
    }
    scenario_api = RecordingApi(httpx.Response(200, json=scenario_payload))
    facade_client._test_case_tree_api = tree_api  # type: ignore[assignment]
    facade_client._scenario_api = scenario_api  # type: ignore[assignment]

    node = await facade_client.get_tree_node(7, 3, parent_node_id=1, filter_id=2, page=0, size=10)
    assert node.name == "Root"
    assert node.children is not None

    scenario = await facade_client.get_test_case_scenario(99)
    assert len(scenario.steps or []) == 1
    assert scenario_api.calls[-1][0] == "get_normalized_scenario_without_preload_content"


@pytest.mark.asyncio
async def test_shared_step_attachment_and_custom_field_project_delegation(facade_client: AllureClient) -> None:
    shared_api = RecordingApi("shared-result")
    shared_scenario_api = RecordingApi(httpx.Response(200, json={"id": 1}))
    scenario_api = RecordingApi(httpx.Response(200, json={}))

    async def created_attachments() -> list[str]:
        return ["attachment"]

    async def created_shared_attachments() -> list[str]:
        return ["shared-attachment"]

    attachment_api = object.__new__(TestCaseAttachmentControllerApi)
    attachment_api.create16 = lambda **_kwargs: created_attachments()  # type: ignore[attr-defined]
    shared_attachment_api = object.__new__(SharedStepAttachmentControllerApi)
    shared_attachment_api.create21 = lambda **_kwargs: created_shared_attachments()  # type: ignore[attr-defined]
    custom_project_api = RecordingApi(SimpleNamespace(content=[]))
    project_api = RecordingApi(["count"])
    custom_field_api = RecordingApi(None)
    test_case_custom_field_api = RecordingApi(["case-fields"])
    test_case_api = RecordingApi("test-case")
    facade_client._shared_step_api = shared_api  # type: ignore[assignment]
    facade_client._shared_step_scenario_api = shared_scenario_api  # type: ignore[assignment]
    facade_client._scenario_api = scenario_api  # type: ignore[assignment]
    facade_client._attachment_api = attachment_api  # type: ignore[assignment]
    facade_client._shared_step_attachment_api = shared_attachment_api  # type: ignore[assignment]
    facade_client._custom_field_project_v2_api = custom_project_api  # type: ignore[assignment]
    facade_client._custom_field_project_api = custom_field_api  # type: ignore[assignment]
    facade_client._project_api = project_api  # type: ignore[assignment]
    facade_client._test_case_custom_field_api = test_case_custom_field_api  # type: ignore[assignment]
    facade_client._test_case_api = test_case_api  # type: ignore[assignment]

    assert await facade_client.create_shared_step(7, "Login") == "shared-result"
    assert await facade_client.list_shared_steps(7, search="log", archived=False) == "shared-result"
    await facade_client.patch_test_case_scenario_step(1, ScenarioStepPatchDto(body="Updated"))
    await facade_client.patch_shared_step_scenario_step(2, ScenarioStepPatchDto(body="Updated"))
    assert await facade_client.upload_attachment(10, [("a.txt", b"a")]) == ["attachment"]
    assert await facade_client.upload_shared_step_attachment(20, [("b.txt", b"b")]) == ["shared-attachment"]
    await facade_client.archive_shared_step(20)
    assert await facade_client.get_shared_step(20) == "shared-result"
    assert await facade_client.update_shared_step(20, SharedStepPatchDto(name="New")) == "shared-result"
    await facade_client.delete_shared_step(20)
    await facade_client.purge_shared_step(20)
    assert await facade_client.list_project_custom_fields(7, page=0, size=10) == []
    assert await facade_client.count_test_cases_in_projects([7], 3, deleted=False) == ["count"]
    await facade_client.remove_custom_field_from_project(3, 7)
    await facade_client.update_test_case_custom_fields(42, [])
    assert await facade_client.get_test_case_custom_fields(42, 7) == ["case-fields"]
    await facade_client.update_cfvs_of_test_case(42, [])
    await facade_client.delete_scenario_step(9)
    await facade_client.update_test_case(42, TestCasePatchV2Dto(name="Updated"))

    with pytest.raises(AllureValidationError, match="shared_step_id"):
        await facade_client.create_shared_step_scenario_step(ScenarioStepCreateDto(body="body"))
    with pytest.raises(AllureValidationError, match="test_case_id"):
        await facade_client._upload_attachment_via_api(attachment_api, file_data=[])
    with pytest.raises(AllureValidationError, match="shared_step_id"):
        await facade_client._upload_attachment_via_api(shared_attachment_api, file_data=[])
    with pytest.raises(AllureValidationError, match="At least one project ID"):
        await facade_client.count_test_cases_in_projects([], 3)
    with pytest.raises(AllureValidationError, match="Custom field ID"):
        await facade_client.remove_custom_field_from_project(0, 7)


@pytest.mark.asyncio
async def test_launch_upload_validation_paths(facade_client: AllureClient) -> None:
    with pytest.raises(AllureValidationError, match="Launch ID"):
        await facade_client.upload_results_to_launch(0, [b"data"])
    with pytest.raises(AllureValidationError, match="files"):
        await facade_client.upload_results_to_launch(1, [])

    facade_client._api_client = None
    with pytest.raises(AllureAPIError, match="Client not initialized"):
        await facade_client.upload_results_to_launch(1, [b"data"], LaunchExistingUploadDto())
