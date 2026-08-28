"""Unit coverage for exact curated test-result reads."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.client.exceptions import AllureAPIError, AllureValidationError
from src.services.test_result_service import TestResultService


def _client() -> MagicMock:
    client = MagicMock()
    client.get_base_url.return_value = "https://testops.example/"
    client.get_project.return_value = 9
    client.get_test_result = AsyncMock(
        return_value=SimpleNamespace(
            id=1498142,
            launch_id=89067,
            project_id=9,
            test_case_id=41,
            name="Result",
            full_name="Suite Result",
            status="failed",
            manual=False,
            external=False,
            hidden=False,
            flaky=False,
            muted=False,
            known=False,
            duration=0,
            description="",
            parameters=[],
            tags=[],
            links=[],
        )
    )
    client.get_test_result_execution_raw = AsyncMock(
        return_value={
            "steps": [
                {
                    "id": 3,
                    "name": "parent",
                    "status": "failed",
                    "steps": [
                        {
                            "type": "attachment",
                            "attachment": {"id": 55, "name": "step.log", "entity": "test_result"},
                        }
                    ],
                }
            ]
        }
    )
    client.get_test_result_fixtures = AsyncMock(return_value=[])
    client.list_test_result_attachments = AsyncMock(return_value=SimpleNamespace(content=[], last=True, number=0))
    client.get_test_result_fixture_attachments = AsyncMock(
        return_value=SimpleNamespace(content=[], last=True, number=0)
    )
    client.get_test_result_custom_fields = AsyncMock(return_value=[])
    client.get_test_result_environment = AsyncMock(return_value=[])
    client.get_test_result_members = AsyncMock(return_value=[])
    client.get_test_result_test_keys = AsyncMock(return_value=[])
    client.get_test_result_issues = AsyncMock(return_value=[])
    client.get_test_result_defects = AsyncMock(return_value=SimpleNamespace(content=[], last=True, number=0))
    client.get_test_result_history = AsyncMock(return_value=SimpleNamespace(content=[], last=True, number=0))
    client.get_test_result_retries = AsyncMock(return_value=SimpleNamespace(content=[], last=True, number=0))
    return client


@pytest.mark.asyncio
async def test_get_test_result_uses_exact_id_preserves_falsey_values_and_v2_execution() -> None:
    client = _client()

    detail = await TestResultService(client).get_test_result(1498142)

    client.get_test_result.assert_awaited_once_with(1498142)
    client.get_test_result_execution_raw.assert_awaited_once_with(1498142, v2=True)
    assert detail.actual_launch_id == 89067
    assert detail.result_url == "https://testops.example/launch/89067/tree/1498142"
    assert "treeId" not in detail.result_url
    assert detail.core["manual"] is False
    assert detail.core["duration"] == 0
    assert detail.core["description"] == ""
    assert detail.test_case == {
        "id": 41,
        "name": None,
        "url": "https://testops.example/project/9/test-cases/41",
    }
    attachment = detail.execution_steps[0].steps[0].attachments[0]
    assert attachment.attachment_id == 55
    assert attachment.attachment_kind == "test_result"
    assert attachment.test_result_id == 1498142
    assert attachment.test_case_id is None


@pytest.mark.asyncio
async def test_get_test_result_reports_optional_failure_and_never_substitutes_launch_context() -> None:
    client = _client()
    client.get_test_result.return_value.launch_id = None
    client.get_test_result_issues.side_effect = AllureAPIError("unavailable", status_code=503)

    detail = await TestResultService(client).get_test_result(1498142)

    assert detail.result_url is None
    assert detail.partial is True
    assert {item.section for item in detail.unavailable_sections} == {"issues", "result_url"}
    assert client.list_test_result_attachments.await_count == 1


@pytest.mark.asyncio
async def test_get_test_result_preserves_zero_project_id_and_rejects_unverified_launch_id() -> None:
    client = _client()
    client.get_test_result.return_value.project_id = 0
    client.get_test_result.return_value.launch_id = 0

    detail = await TestResultService(client).get_test_result(1498142)

    assert detail.project_id == 0
    assert detail.test_case is not None
    assert detail.test_case["url"] == "https://testops.example/project/0/test-cases/41"
    assert detail.result_url is None
    assert detail.launch_url is None
    assert any(item.section == "result_url" for item in detail.unavailable_sections)


@pytest.mark.asyncio
async def test_get_test_result_rejects_boolean_id() -> None:
    with pytest.raises(AllureValidationError, match="positive integer"):
        await TestResultService(_client()).get_test_result(True)


@pytest.mark.asyncio
async def test_get_test_result_omits_unusable_attachment_preparation_reference() -> None:
    client = _client()
    client.get_test_result.return_value.test_case_id = None
    client.list_test_result_attachments.return_value = SimpleNamespace(
        content=[SimpleNamespace(id=0, name="invalid-result.log", entity="test_result")], last=True, number=0
    )
    client.get_test_result_execution_raw.return_value = {
        "steps": [
            {
                "type": "attachment",
                "attachment": {"id": 55, "name": "case.log", "from_test_case": True},
            }
        ]
    }

    detail = await TestResultService(client).get_test_result(1498142)

    assert detail.result_attachments[0].attachment_id is None
    attachment = detail.execution_steps[0].attachments[0]
    assert attachment.attachment_id is None
    assert attachment.attachment_kind is None
    assert attachment.test_result_id is None
    assert attachment.test_case_id is None


@pytest.mark.asyncio
async def test_get_test_result_reports_unverified_fixture_attachment_ownership() -> None:
    client = _client()
    client.get_test_result_fixtures.return_value = [
        SimpleNamespace(id=1, name="setup", scenario=SimpleNamespace(steps=[]), type="before")
    ]
    client.get_test_result_fixture_attachments.return_value = SimpleNamespace(
        content=[SimpleNamespace(id=99, name="orphan.log", entity="test_fixture_result")], last=True, number=0
    )

    detail = await TestResultService(client).get_test_result(1498142)

    assert detail.fixtures[0].attachments == ()
    assert any(item.section == "fixture_attachments" for item in detail.unavailable_sections)


@pytest.mark.asyncio
async def test_get_test_result_preserves_collected_pages_when_a_later_page_fails() -> None:
    client = _client()
    first_page = SimpleNamespace(
        content=[SimpleNamespace(id=1, name="result.log", entity="test_result")], last=False, number=0
    )
    client.list_test_result_attachments.side_effect = [first_page, AllureAPIError("unavailable", status_code=503)]

    detail = await TestResultService(client).get_test_result(1498142)

    assert [attachment.attachment_id for attachment in detail.result_attachments] == [1]
    unavailable = next(item for item in detail.unavailable_sections if item.section == "result_attachments")
    assert unavailable.items_retrieved == 1
    assert unavailable.status_code == 503


@pytest.mark.asyncio
async def test_get_test_result_marks_contradictory_pagination_incomplete() -> None:
    client = _client()
    client.list_test_result_attachments.return_value = SimpleNamespace(
        content=[SimpleNamespace(id=1, name="result.log", entity="test_result")],
        last=True,
        number=0,
        total_pages=2,
    )

    detail = await TestResultService(client).get_test_result(1498142)

    assert [attachment.attachment_id for attachment in detail.result_attachments] == [1]
    assert any(item.section == "result_attachments" for item in detail.unavailable_sections)


@pytest.mark.asyncio
async def test_get_test_result_omits_unverified_related_result_url() -> None:
    client = _client()
    client.get_test_result_history.return_value = SimpleNamespace(
        content=[SimpleNamespace(id=52, name="Earlier", status="passed")], last=True, number=0
    )

    detail = await TestResultService(client).get_test_result(1498142)

    assert detail.related_results[0].launch_id is None
    assert detail.related_results[0].url is None


@pytest.mark.asyncio
async def test_get_test_result_reconciles_and_deduplicates_fixture_attachments() -> None:
    client = _client()
    client.get_test_result_fixtures.return_value = [
        SimpleNamespace(
            id=1,
            name="setup",
            scenario=SimpleNamespace(
                steps=[
                    SimpleNamespace(actual_instance=SimpleNamespace(type="attachment", attachment_id=99)),
                    SimpleNamespace(actual_instance=SimpleNamespace(type="attachment", attachment_id=99)),
                ]
            ),
            type="before",
        )
    ]
    client.get_test_result_fixture_attachments.return_value = SimpleNamespace(
        content=[
            SimpleNamespace(
                id=99,
                name="full.log",
                entity="test_fixture_result",
                content_type="text/plain",
                content_length=10,
            )
        ],
        last=True,
        number=0,
    )

    detail = await TestResultService(client).get_test_result(1498142)

    assert len(detail.fixtures[0].attachments) == 1
    attachment = detail.fixtures[0].attachments[0]
    assert attachment.name == "full.log"
    assert attachment.attachment_id == 99
    assert attachment.attachment_kind == "fixture_result"
    assert attachment.test_result_id == 1498142
