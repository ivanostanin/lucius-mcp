"""Additional focused coverage for thin validation and generated-wrapper edges."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Annotated

import httpx
import pytest
from pydantic import BaseModel, Field, SecretStr

from src.client import AllureClient, AllureValidationError, FindAll29200Response
from src.client.exceptions import AllureAPIError
from src.client.generated.models.custom_field_dto import CustomFieldDto
from src.client.generated.models.custom_field_project_dto import CustomFieldProjectDto
from src.client.models.plans import TestPlanCaseSelection, TestPlanValues
from src.client.overridden.test_case_custom_fields_v2 import TestCaseCustomFieldV2ControllerApi
from src.services.attachment_service import AttachmentService
from src.services.launch_service import LaunchService
from src.services.telemetry_service import TelemetryService
from src.utils.schema_hint import _format_dict_type, _format_union_type, _get_type_name, generate_schema_hint
from src.version import _version_from_pyproject


class FakeResponse:
    async def read(self) -> None:
        return None


class FakeApiClient:
    def __init__(self, data: object = None) -> None:
        self.data = data
        self.serialized: list[dict[str, object]] = []

    def select_header_accept(self, values: list[str]) -> str:
        return values[0]

    def select_header_content_type(self, values: list[str]) -> str:
        return values[0]

    def param_serialize(self, **kwargs: object) -> tuple[object, ...]:
        self.serialized.append(kwargs)
        return ("serialized",)

    async def call_api(self, *_args: object, **_kwargs: object) -> FakeResponse:
        return FakeResponse()

    def response_deserialize(self, **_kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(data=self.data)


class RecordingApi:
    def __init__(self, result: object = None) -> None:
        self.result = result if result is not None else SimpleNamespace()

    def __getattr__(self, _name: str) -> object:
        def call(*_args: object, **_kwargs: object) -> object:
            async def result() -> object:
                if isinstance(self.result, BaseException):
                    raise self.result
                return self.result

            return result()

        return call


@pytest.fixture
def entered_client(monkeypatch: pytest.MonkeyPatch) -> AllureClient:
    client = AllureClient("https://allure.example.com", SecretStr("token"), project=7)
    client._is_entered = True

    async def no_token_refresh() -> None:
        return None

    monkeypatch.setattr(client, "_ensure_valid_token", no_token_refresh)
    return client


def test_plan_helper_models_validate_selection() -> None:
    values = TestPlanValues(name="Regression", description="desc", product_area_id=1, tags=["smoke"])
    assert values.name == "Regression"

    TestPlanCaseSelection(test_case_ids=[1]).validate_selection()
    TestPlanCaseSelection(aql_filter='tag = "smoke"').validate_selection()
    with pytest.raises(ValueError, match="Either test_case_ids"):
        TestPlanCaseSelection().validate_selection()


@pytest.mark.asyncio
async def test_manual_custom_field_override_serializes_and_deserializes() -> None:
    api_client = FakeApiClient(data=["field"])
    api = TestCaseCustomFieldV2ControllerApi(api_client=api_client)  # type: ignore[arg-type]

    assert await api.get_custom_fields_with_values3(10, 7, _headers={"X-Test": "1"}) == ["field"]
    await api.update_cfvs_of_test_case(10, [], _content_type="application/json")

    get_call, update_call = api_client.serialized
    assert get_call["resource_path"] == "/api/testcase/{testCaseId}/cfv"
    assert ("v2", "True") in get_call["query_params"]
    assert ("projectId", 7) in get_call["query_params"]
    assert update_call["method"] == "POST"
    assert update_call["body"] == []


@pytest.mark.asyncio
async def test_attachment_service_validation_and_upload_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    uploaded = SimpleNamespace(id=1, name="a.txt")
    client = SimpleNamespace(upload_attachment=lambda _test_case_id, _files: None)

    async def upload_attachment(test_case_id: int, files: list[object]) -> list[object]:
        assert test_case_id == 10
        assert files == [("a.txt", b"A")]
        return [uploaded]

    client.upload_attachment = upload_attachment
    service = AttachmentService(client=client)  # type: ignore[arg-type]

    assert await service.upload_attachment(10, {"name": "a.txt", "content_type": "text/plain", "content": "QQ=="}) is (
        uploaded
    )

    with pytest.raises(AllureValidationError, match="missing required"):
        await service.upload_attachment(10, {"name": "a.txt"})
    with pytest.raises(AllureValidationError, match="not allowed"):
        await service.upload_attachment(
            10,
            {"name": "a.exe", "content_type": "application/x-msdownload", "content": "QQ=="},
        )
    with pytest.raises(AllureValidationError, match="both"):
        await service.upload_attachment(
            10,
            {"name": "a.txt", "content_type": "text/plain", "content": "QQ==", "url": "https://example.com/a.txt"},
        )
    with pytest.raises(AllureValidationError, match="Invalid base64"):
        await service.upload_attachment(10, {"name": "a.txt", "content_type": "text/plain", "content": "not-base64!"})
    with pytest.raises(AllureValidationError, match="either"):
        await service.upload_attachment(10, {"name": "a.txt", "content_type": "text/plain"})

    async def empty_upload(_test_case_id: int, _files: list[object]) -> list[object]:
        return []

    client.upload_attachment = empty_upload
    with pytest.raises(AllureValidationError, match="no results"):
        await service.upload_attachment(10, {"name": "a.txt", "content_type": "text/plain", "content": "QQ=="})

    class FakeHttpResponse:
        content = b"downloaded"

        def raise_for_status(self) -> None:
            return None

    class FakeHttpClient:
        async def __aenter__(self) -> object:
            return self

        async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
            return None

        async def get(self, *_args: object, **_kwargs: object) -> FakeHttpResponse:
            return FakeHttpResponse()

    monkeypatch.setattr("src.services.attachment_service.httpx.AsyncClient", FakeHttpClient)
    assert await service._retrieve_content({"url": "https://example.com/a.txt"}) == b"downloaded"

    class FailingHttpClient:
        async def __aenter__(self) -> object:
            return self

        async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
            return None

        async def get(self, *_args: object, **_kwargs: object) -> object:
            raise httpx.RequestError("network down")

    monkeypatch.setattr("src.services.attachment_service.httpx.AsyncClient", FailingHttpClient)
    with pytest.raises(AllureValidationError, match="Failed to download attachment"):
        await service._retrieve_content({"url": "https://example.com/a.txt"})

    monkeypatch.setattr("src.services.attachment_service.MAX_ATTACHMENT_SIZE", 1)
    with pytest.raises(AllureValidationError, match="exceeds limit"):
        await service.upload_attachment(10, {"name": "a.txt", "content_type": "text/plain", "content": "QUE="})


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("setup_attr", "operation", "message"),
    [
        ("_test_case_api", lambda c: c.list_deleted_test_cases(0), "Project ID"),
        ("_test_case_api", lambda c: c.list_deleted_test_cases(1, page=-1), "Page"),
        ("_test_case_api", lambda c: c.list_deleted_test_cases(1, size=101), "Size"),
        ("_tree_api", lambda c: c.list_trees(1, page=-1), "Page"),
        ("_tree_api", lambda c: c.list_trees(1, size=0), "Size"),
        ("_tree_api", lambda c: c.get_tree(0), "Tree ID"),
        ("_test_case_tree_api", lambda c: c.create_tree_group(0, 1, "Suite"), "Project ID"),
        ("_test_case_tree_api", lambda c: c.create_tree_group(1, 0, "Suite"), "Tree ID"),
        ("_test_case_tree_api", lambda c: c.create_tree_group(1, 1, "Suite", parent_node_id=0), "Parent node"),
        ("_test_case_tree_api", lambda c: c.rename_tree_group(1, 0, "Suite"), "Group ID"),
        ("_test_case_tree_api", lambda c: c.delete_tree_group(0, 1), "Project ID"),
        ("_test_case_tree_api", lambda c: c.create_tree_leaf(1, 1, "Leaf", node_id=0), "Node ID"),
        ("_test_case_tree_api", lambda c: c.rename_tree_leaf(1, 0, "Leaf"), "Leaf ID"),
        ("_test_case_tree_api", lambda c: c.get_tree_node(1, 1, filter_id=0), "Filter ID"),
        ("_test_case_tree_api", lambda c: c.get_tree_node(1, 1, page=-1), "Page"),
        ("_test_case_tree_api", lambda c: c.get_tree_node(1, 1, size=0), "Size"),
        ("_test_case_tree_api", lambda c: c.suggest_tree_groups(1, tree_id=0), "Tree ID"),
        ("_test_case_tree_api", lambda c: c.suggest_tree_groups(1, page=-1), "Page"),
        ("_test_case_tree_api", lambda c: c.suggest_tree_groups(1, size=0), "Size"),
        ("_test_case_tree_bulk_api", lambda c: c.assign_test_cases_to_tree_node(0, [1], 1, 1), "Project ID"),
        ("_test_case_tree_bulk_api", lambda c: c.assign_test_cases_to_tree_node(1, [1], 0, 1), "Target node"),
        ("_test_case_tree_bulk_api", lambda c: c.assign_test_cases_to_tree_node(1, [1], 1, 0), "Tree ID"),
        ("_custom_field_project_v2_api", lambda c: c.list_project_custom_fields(0), "Project ID"),
        ("_custom_field_project_v2_api", lambda c: c.list_project_custom_fields(1, page=-1), "Page"),
        ("_custom_field_project_v2_api", lambda c: c.list_project_custom_fields(1, size=101), "Size"),
        ("_project_api", lambda c: c.count_test_cases_in_projects([0], 1), "Project IDs"),
        ("_project_api", lambda c: c.count_test_cases_in_projects([1], 0), "Custom field ID"),
    ],
)
async def test_client_validation_branches(
    entered_client: AllureClient, setup_attr: str, operation: object, message: str
) -> None:
    setattr(entered_client, setup_attr, RecordingApi())
    with pytest.raises(AllureValidationError, match=message):
        await operation(entered_client)  # type: ignore[misc]


@pytest.mark.asyncio
async def test_client_custom_field_value_conflict_and_fetch_fallback(entered_client: AllureClient) -> None:
    entered_client._custom_field_value_project_api = RecordingApi(
        AllureAPIError("conflict", status_code=409, response_body="duplicate")
    )  # type: ignore[assignment]
    with pytest.raises(AllureValidationError, match="Duplicate custom field value"):
        await entered_client.create_custom_field_value(7, SimpleNamespace(name="P0"))  # type: ignore[arg-type]

    cf_project = CustomFieldProjectDto.model_construct(custom_field=CustomFieldDto.model_construct(id=1, name="Layer"))
    entered_client._custom_field_project_v2_api = RecordingApi(SimpleNamespace(content=[cf_project]))  # type: ignore[assignment]
    entered_client._custom_field_value_project_api = RecordingApi(AllureAPIError("temporary", status_code=500))  # type: ignore[assignment]

    fields = await entered_client.get_custom_fields_with_values(7)
    assert len(fields) == 1
    assert fields[0].values == []


@pytest.mark.asyncio
async def test_client_integration_listing_success_and_fallbacks(entered_client: AllureClient) -> None:
    entered_client._integration_api = RecordingApi(SimpleNamespace(content=["github"]))  # type: ignore[assignment]

    assert await entered_client.get_integrations() == ["github"]
    assert await entered_client.get_project_available_integrations(7) == ["github"]

    entered_client._integration_api = RecordingApi(RuntimeError("api unavailable"))  # type: ignore[assignment]
    assert await entered_client.get_integrations() == []
    assert await entered_client.get_project_available_integrations(7) == []

    entered_client._integration_api = None
    with pytest.raises(RuntimeError, match="async context manager"):
        await entered_client.get_integrations()


def test_schema_hint_handles_typing_shapes() -> None:
    class HintModel(BaseModel):
        required_name: str
        maybe_count: int | None = None
        names: list[str] = Field(default_factory=list, alias="displayNames")
        metadata: dict[str, int] = Field(default_factory=dict)
        annotated_value: Annotated[int, Field(gt=0)] = 1

    hint = generate_schema_hint(HintModel)

    assert "required_name: str (required)" in hint
    assert "maybe_count: int (optional)" in hint
    assert "displayNames: List[str] (optional)" in hint
    assert "metadata: Dict[str, int] (optional)" in hint
    assert "annotated_value: int (optional)" in hint
    assert generate_schema_hint(object) == ""  # type: ignore[arg-type]
    assert _get_type_name(None) == "Any"
    assert _get_type_name("typing.Annotated[StrictInt, Gt(gt=0)]") == "int"
    assert _get_type_name("typing.Annotated[StrictStr]") == "str"
    assert _get_type_name("StrictBool") == "bool"
    assert _get_type_name(dict) == "dict"
    assert _format_dict_type(dict) == "Dict[Any, Any]"
    assert _format_union_type(str | int) == "str | int"
    assert _format_union_type(type(None)) == "Any"


def test_version_fallback_reads_pyproject_version() -> None:
    assert _version_from_pyproject()


def test_launch_service_validation_helpers_cover_edge_cases() -> None:
    service = LaunchService(SimpleNamespace(get_project=lambda: 1))  # type: ignore[arg-type]

    service._validate_project_id(1)
    LaunchService._validate_pagination(0, 100)
    LaunchService._validate_launch_id(1)
    LaunchService._validate_name("Launch")
    LaunchService._validate_tags(["smoke"])
    LaunchService._validate_links([{"name": "Docs", "url": "https://example.com", "type": "issue"}])
    LaunchService._validate_issues([{"id": 1}])

    assert LaunchService._build_tag_dtos(["smoke"])[0].name == "smoke"
    assert LaunchService._build_link_dtos([{"name": "Docs", "url": "https://example.com"}])[0].name == "Docs"
    assert LaunchService._build_issue_dtos([{"name": "ISSUE-1"}])[0].name == "ISSUE-1"
    assert LaunchService._determine_close_report_status(SimpleNamespace(closed=True), SimpleNamespace()) == (
        "already-closed"
    )
    assert (
        LaunchService._determine_close_report_status(SimpleNamespace(closed=False), SimpleNamespace(status="done"))
        == "done"
    )
    with pytest.raises(AllureValidationError, match="Unexpected launch list"):
        LaunchService._extract_page(FindAll29200Response.model_construct(actual_instance=SimpleNamespace()))

    invalid_cases = [
        (service._validate_project_id, (None,), "Project ID"),
        (service._validate_project_id, (0,), "positive"),
        (LaunchService._validate_pagination, (-1, 20), "Page"),
        (LaunchService._validate_pagination, (0, 101), "Size"),
        (LaunchService._validate_launch_id, ("1",), "integer"),
        (LaunchService._validate_launch_id, (0,), "positive"),
        (LaunchService._validate_name, (123,), "string"),
        (LaunchService._validate_name, (" ",), "required"),
        (LaunchService._validate_name, ("x" * 256,), "255"),
        (LaunchService._validate_tags, ("smoke",), "list"),
        (LaunchService._validate_tags, ([1],), "index 0"),
        (LaunchService._validate_tags, ([" "],), "cannot be empty"),
        (LaunchService._validate_tags, (["x" * 256],), "255"),
        (LaunchService._validate_links, ("bad",), "list"),
        (LaunchService._validate_links, ([()],), "dictionary"),
        (LaunchService._validate_links, ([{}],), "cannot be empty"),
        (LaunchService._validate_links, ([{"url": 1}],), "url"),
        (LaunchService._validate_links, ([{"name": 1}],), "name"),
        (LaunchService._validate_links, ([{"type": 1}],), "type"),
        (LaunchService._validate_issues, ("bad",), "list"),
        (LaunchService._validate_issues, ([()],), "dictionary"),
        (LaunchService._validate_issues, ([{}],), "cannot be empty"),
    ]
    for func, args, message in invalid_cases:
        with pytest.raises(AllureValidationError, match=message):
            func(*args)


@pytest.mark.asyncio
async def test_telemetry_helpers_and_error_paths(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    service = TelemetryService(enabled=False, hash_salt="salt", umami_website_id=None)
    state_root = tmp_path / "state"

    assert TelemetryService._resolve_umami_base_url("https://u.example/api/send") == "https://u.example"
    assert (
        TelemetryService._telemetry_state_dir_for_platform(
            configured_state_dir=None,
            os_name="nt",
            sys_platform="win32",
            env={"LOCALAPPDATA": "C:/Users/me/AppData/Local"},
            home_dir=tmp_path,  # type: ignore[arg-type]
        )
        .as_posix()
        .endswith("lucius-mcp")
    )
    assert (
        TelemetryService._telemetry_state_dir_for_platform(
            configured_state_dir=None,
            os_name="posix",
            sys_platform="linux",
            env={"XDG_STATE_HOME": state_root.as_posix()},
            home_dir=tmp_path,
        )
        == state_root / "lucius-mcp"
    )
    assert service._hash_identifier("value") is not None
    assert service._duration_bucket(50) == "<100ms"
    assert service._duration_bucket(250) == "100-500ms"
    assert service._duration_bucket(1000) == "500ms-2s"
    assert service._duration_bucket(2500) == ">2s"
    assert service._classify_error(ValueError("bad")) == "validation"
    assert service._classify_error(PermissionError("denied")) == "auth"
    assert service._classify_error(httpx.TimeoutException("slow")) == "api"
    assert service._classify_error(RuntimeError("boom")) == "unexpected"

    service._umami_ready = False
    service._schedule_event("event", {})
    service._umami_ready = True
    service._website_id = None
    service._schedule_event("event", {})
    service._schedule_event("event", {})

    async def raises_status(**_kwargs: object) -> None:
        response = httpx.Response(500, request=httpx.Request("POST", "https://u.example"))
        raise httpx.HTTPStatusError("bad", request=response.request, response=response)

    monkeypatch.setattr("src.services.telemetry_service.umami.new_event_async", raises_status)
    service._website_id = "site"
    await service._send_event(event_name="event", payload={})
