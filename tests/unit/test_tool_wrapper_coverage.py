"""Focused coverage for tool wrapper formatting and confirmation branches."""

from __future__ import annotations

import importlib
from types import SimpleNamespace

import pytest

from src.client.generated.models.shared_step_step_dto import SharedStepStepDto
from src.services.search_service import TestCaseDetails, TestCaseListResult

link_tool = importlib.import_module("src.tools.link_shared_step")
unlink_tool = importlib.import_module("src.tools.unlink_shared_step")
search_tool = importlib.import_module("src.tools.search")
update_tool = importlib.import_module("src.tools.update_test_case")

BASE_URL = "https://allure.example"
PROJECT_ID = 7


class AsyncClientContext:
    def __init__(self, client: object) -> None:
        self.client = client

    async def __aenter__(self) -> object:
        return self.client

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None


def _scenario() -> SimpleNamespace:
    return SimpleNamespace(
        steps=[
            SimpleNamespace(
                actual_instance=SharedStepStepDto.model_construct(type="SharedStepStepDto", shared_step_id=55)
            ),
            SimpleNamespace(actual_instance=SimpleNamespace(body="Inline action")),
            SimpleNamespace(actual_instance=SimpleNamespace(body=None)),
        ],
        attachments=[SimpleNamespace(id=9, name="evidence.png"), {"attachmentId": "10", "file_name": "log.txt"}],
    )


def test_shared_step_formatters_cover_shared_inline_and_empty_steps() -> None:
    scenario = _scenario()

    assert "1. [Shared Step] ID: 55" in link_tool._format_steps(scenario, base_url=BASE_URL, project_id=PROJECT_ID)
    assert "2. Inline action" in unlink_tool._format_steps(scenario, base_url=BASE_URL, project_id=PROJECT_ID)
    assert link_tool._format_steps(SimpleNamespace(steps=[]), base_url=BASE_URL, project_id=PROJECT_ID) == "No steps."
    assert (
        unlink_tool._format_steps(SimpleNamespace(steps=None), base_url=BASE_URL, project_id=PROJECT_ID) == "No steps."
    )
    assert link_tool._serialize_steps(scenario, base_url=BASE_URL, project_id=PROJECT_ID) == [
        {
            "index": 1,
            "type": "shared_step",
            "shared_step_id": 55,
            "shared_step_url": f"{BASE_URL}/project/{PROJECT_ID}/shared-steps/55",
        },
        {"index": 2, "type": "inline", "action": "Inline action"},
        {"index": 3, "type": "inline", "action": "Step"},
    ]
    assert unlink_tool._serialize_steps(SimpleNamespace(steps="bad"), base_url=BASE_URL, project_id=PROJECT_ID) == []


@pytest.mark.asyncio
async def test_link_and_unlink_success_and_error_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    client = SimpleNamespace(
        get_base_url=lambda: BASE_URL,
        get_project=lambda: PROJECT_ID,
        get_test_case_scenario=lambda _test_case_id: _scenario(),
    )

    async def get_test_case_scenario(test_case_id: int) -> SimpleNamespace:
        return _scenario()

    client.get_test_case_scenario = get_test_case_scenario

    class SuccessfulService:
        def __init__(self, client: object) -> None:
            self.client = client

        async def add_shared_step_to_case(self, **_kwargs: object) -> None:
            return None

        async def remove_shared_step_from_case(self, **_kwargs: object) -> None:
            return None

    monkeypatch.setattr(link_tool.AllureClient, "from_env", lambda project=None: AsyncClientContext(client))
    monkeypatch.setattr(unlink_tool.AllureClient, "from_env", lambda project=None: AsyncClientContext(client))
    monkeypatch.setattr(link_tool, "TestCaseService", SuccessfulService)
    monkeypatch.setattr(unlink_tool, "TestCaseService", SuccessfulService)

    linked = await link_tool.link_shared_step(10, 55, position=0, confirm=True)
    unlinked = await unlink_tool.unlink_shared_step(10, 55, confirm=True)
    assert linked.structured_content["steps"][0]["type"] == "shared_step"
    assert unlinked.structured_content["steps"][1]["action"] == "Inline action"

    class FailingService(SuccessfulService):
        async def add_shared_step_to_case(self, **_kwargs: object) -> None:
            raise RuntimeError("link failed")

        async def remove_shared_step_from_case(self, **_kwargs: object) -> None:
            raise RuntimeError("unlink failed")

    monkeypatch.setattr(link_tool, "TestCaseService", FailingService)
    monkeypatch.setattr(unlink_tool, "TestCaseService", FailingService)

    link_error = await link_tool.link_shared_step(10, 55, confirm=True)
    unlink_error = await unlink_tool.unlink_shared_step(10, 55, confirm=True)
    assert link_error.structured_content["status"] == "error"
    assert unlink_error.structured_content["error"] == "unlink failed"


def test_search_formatters_serialize_details_and_pagination() -> None:
    tag = SimpleNamespace(name="smoke")
    status = SimpleNamespace(id=1, name="Draft")
    test_case = SimpleNamespace(
        id=123,
        name="Login",
        status=status,
        tags=[tag],
        description="desc",
        precondition="pre",
        custom_fields=[
            SimpleNamespace(custom_field=SimpleNamespace(name="Layer"), value="API"),
            {"field_name": "Priority", "valueName": "P0"},
        ],
        automation_status="manual",
    )
    child = SimpleNamespace(actual_instance=SimpleNamespace(body="Nested", expected_result="Done"))
    step = SimpleNamespace(actual_instance=SimpleNamespace(body="Open", expected="Visible", steps=[child]))
    details = TestCaseDetails(
        test_case=test_case,
        scenario=SimpleNamespace(steps=[step], attachments=_scenario().attachments),
    )
    result = TestCaseListResult(items=[test_case], total=2, page=0, size=1, total_pages=2)

    list_text = search_tool._format_test_case_list(result)
    details_text = search_tool._format_test_case_details(details)
    serialized = search_tool._serialize_test_case_details(details, base_url=BASE_URL, project_id=PROJECT_ID)

    assert "Use page=1" in list_text
    assert "Open" in details_text
    assert "Nested" in details_text
    assert serialized["custom_fields"] == [
        {"name": "Layer", "value": "API"},
        {"name": "Priority", "value": "P0"},
    ]
    assert serialized["attachments"] == [
        {"name": "evidence.png", "id": "9"},
        {"name": "log.txt", "id": "10"},
    ]
    assert search_tool._format_search_results(TestCaseListResult([], 0, 0, 20, 0), "none") == (
        "No test cases found matching 'none'."
    )


@pytest.mark.asyncio
async def test_update_test_case_reports_all_change_categories(monkeypatch: pytest.MonkeyPatch) -> None:
    current_case = SimpleNamespace(
        id=10,
        name="Old",
        description="old desc",
        tags=[SimpleNamespace(name="old")],
        automated=False,
        expected_result="old expected",
        status=SimpleNamespace(id=1),
        test_layer=SimpleNamespace(id=1),
        workflow=SimpleNamespace(id=1),
        links=[{"name": "old", "url": "https://old.example"}],
    )
    updated_case = SimpleNamespace(
        id=10,
        name="New",
        automated=True,
        test_layer=SimpleNamespace(id=2),
    )

    class UpdateService:
        def __init__(self, client: object) -> None:
            self.client = client

        async def get_test_case(self, test_case_id: int) -> object:
            assert test_case_id == 10
            return current_case

        async def update_test_case(self, test_case_id: int, update_data: object) -> object:
            assert test_case_id == 10
            assert update_data.name == "New"
            return updated_case

    client = SimpleNamespace(get_base_url=lambda: BASE_URL, get_project=lambda: PROJECT_ID)
    monkeypatch.setattr(update_tool.AllureClient, "from_env", lambda project=None: AsyncClientContext(client))
    monkeypatch.setattr(update_tool, "TestCaseService", UpdateService)

    result = await update_tool.update_test_case(
        10,
        confirm=True,
        name="New",
        description="new desc",
        steps=[{"action": "Open", "expected": "Visible"}],
        tags=["new"],
        attachments=[{"name": "a.txt", "content": "QQ=="}],
        custom_fields={"Layer": "API"},
        automated=True,
        expected_result="new expected",
        status_id=2,
        test_layer_id=2,
        workflow_id=2,
        links=[{"name": "new", "url": "https://new.example"}],
        issues=["ABC-1"],
        remove_issues=["ABC-2"],
        clear_issues=True,
    )

    changes = result.structured_content["changes"]
    assert "name='New'" in changes
    assert "steps updated" in changes
    assert "cleared all issues" in changes
