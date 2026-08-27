"""Sandbox coverage for the exact TestOps test-result read."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence

import httpx
import pytest

from src.client import AllureClient
from src.services.launch_service import LaunchService
from src.services.test_case_service import TestCaseService
from src.services.test_result_service import AttachmentDetail, StepDetail, TestResultService
from src.tools.attachments import prepare_attachment_download
from src.tools.search import get_test_case_details
from src.utils.config import settings
from tests.e2e.helpers.cleanup import CleanupTracker
from tests.e2e.test_launch_manual_execution import _create_launch_with_test_case

pytestmark = pytest.mark.asyncio(loop_scope="module")


@pytest.fixture
def stdio_attachment_delivery() -> Iterator[None]:
    """Use Lucius's real stdio-mode loopback delivery during this test."""

    previous_mode = settings.MCP_MODE
    settings.MCP_MODE = "stdio"
    try:
        yield
    finally:
        settings.MCP_MODE = previous_mode


async def test_get_test_result_returns_exact_result_with_stable_result_url(
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    test_run_id: str,
    stdio_attachment_delivery: None,
) -> None:
    """Verify result and step evidence downloads through Lucius without a bearer token."""
    launch_service = LaunchService(allure_client)
    launch, test_case = await _create_launch_with_test_case(
        allure_client,
        cleanup_tracker,
        test_run_id,
        suffix="test-result-detail",
        steps=[{"action": "Open detail", "expected": "Detail opens"}],
    )
    launch_id = getattr(launch, "id", None)
    test_case_id = getattr(test_case, "id", None)
    assert isinstance(launch_id, int)
    assert isinstance(test_case_id, int)
    session = await launch_service.start_manual_test_session(launch_id)
    submission = await launch_service.submit_manual_test_results(
        session.test_session_id,
        results=[
            {
                "launch_id": launch_id,
                "test_case_id": test_case_id,
                "name": f"[{test_run_id}] Detail Result",
                "full_name": f"[{test_run_id}] Detail Result",
                "status": "passed",
                "steps": [
                    {"type": "body", "body": "Open detail", "status": "passed"},
                    {
                        "type": "attachment",
                        "attachment": {"name": "detail-step.txt", "content_type": "text/plain"},
                        "status": "passed",
                    },
                ],
            }
        ],
    )
    result_id = submission.result_ids[0]

    result_upload = await launch_service.add_test_result_attachment(
        result_id,
        attachment={
            "name": "detail-result.txt",
            "content_type": "text/plain",
            "content": "U2FuZGJveCByZXN1bHQgZGV0YWlsIGV2aWRlbmNl",
        },
    )
    step_upload = await launch_service.add_test_step_attachment(
        test_result_id=result_id,
        step_index=1,
        attachment={
            "name": "detail-step.txt",
            "content_type": "text/plain",
            "content": "U2FuZGJveCBzdGVwIGRldGFpbCBldmlkZW5jZQ==",
        },
    )
    assert result_upload.target_id == result_id
    assert step_upload.target_kind == "test_step"

    detail = await TestResultService(allure_client).get_test_result(result_id)

    assert detail.test_result_id == result_id
    assert detail.actual_launch_id == launch_id
    assert detail.result_url == f"{allure_client.get_base_url()}/launch/{launch_id}/tree/{result_id}"
    assert "treeId" not in detail.result_url

    result_attachment = next(item for item in detail.result_attachments if item.name == "detail-result.txt")
    step_attachment = next(
        item for item in _iter_step_attachments(detail.execution_steps) if item.name == "detail-step.txt"
    )
    await _download_and_verify_evidence(
        result_attachment,
        expected_content=b"Sandbox result detail evidence",
    )
    await _download_and_verify_evidence(
        step_attachment,
        expected_content=b"Sandbox step detail evidence",
    )


async def test_get_test_result_downloads_fixture_evidence_when_sandbox_provides_a_fixture(
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    test_run_id: str,
    stdio_attachment_delivery: None,
) -> None:
    """Verify fixture evidence through Lucius when the sandbox provides a fixture."""
    launch_service = LaunchService(allure_client)
    launch, test_case = await _create_launch_with_test_case(
        allure_client,
        cleanup_tracker,
        test_run_id,
        suffix="test-result-fixture-detail",
        steps=[{"action": "Open fixture detail", "expected": "Fixture detail opens"}],
    )
    launch_id = getattr(launch, "id", None)
    test_case_id = getattr(test_case, "id", None)
    assert isinstance(launch_id, int)
    assert isinstance(test_case_id, int)
    session = await launch_service.start_manual_test_session(launch_id)
    submission = await launch_service.submit_manual_test_results(
        session.test_session_id,
        results=[
            {
                "launch_id": launch_id,
                "test_case_id": test_case_id,
                "name": f"[{test_run_id}] Fixture Detail Result",
                "full_name": f"[{test_run_id}] Fixture Detail Result",
                "status": "passed",
            }
        ],
    )
    result_id = submission.result_ids[0]
    fixtures = await allure_client.get_test_result_fixtures(result_id)
    fixture = next((item for item in fixtures if item.id is not None), None)
    if fixture is None or not isinstance(fixture.id, int):
        pytest.skip("Sandbox did not create a fixture result for this exact test-result scenario")
    fixture_id = fixture.id

    await launch_service.add_test_step_attachment(
        test_result_id=result_id,
        fixture_result_id=fixture_id,
        attachment={
            "name": "detail-fixture.txt",
            "content_type": "text/plain",
            "content": "U2FuZGJveCBmaXh0dXJlIGRldGFpbCBldmlkZW5jZQ==",
        },
    )
    detail = await TestResultService(allure_client).get_test_result(result_id)
    fixture_attachment = next(
        item
        for detail_fixture in detail.fixtures
        if detail_fixture.id == fixture_id
        for item in detail_fixture.attachments
        if item.name == "detail-fixture.txt"
    )
    await _download_and_verify_evidence(
        fixture_attachment,
        expected_content=b"Sandbox fixture detail evidence",
    )


async def test_get_test_case_details_prepares_and_downloads_test_case_evidence(
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    test_run_id: str,
    stdio_attachment_delivery: None,
) -> None:
    """Verify the public read → prepare → GET workflow for test-case evidence."""
    test_case = await TestCaseService(allure_client).create_test_case(
        name=f"[{test_run_id}] Test Case Evidence",
        attachments=[
            {
                "name": "detail-test-case.txt",
                "content_type": "text/plain",
                "content": "U2FuZGJveCB0ZXN0IGNhc2UgZGV0YWlsIGV2aWRlbmNl",
            }
        ],
    )
    test_case_id = getattr(test_case, "id", None)
    assert isinstance(test_case_id, int)
    cleanup_tracker.track_test_case(test_case_id)

    detail = await get_test_case_details(test_case_id)
    attachments = detail.structured_content["attachments"]
    assert isinstance(attachments, list)
    attachment = next(item for item in attachments if item["name"] == "detail-test-case.txt")
    assert isinstance(attachment, dict)
    await _download_and_verify_evidence(
        attachment,
        expected_content=b"Sandbox test case detail evidence",
    )


def _iter_step_attachments(steps: Sequence[StepDetail]) -> Iterator[AttachmentDetail]:
    for step in steps:
        yield from step.attachments
        yield from _iter_step_attachments(step.steps)


async def _download_and_verify_evidence(
    attachment: AttachmentDetail | Mapping[str, object],
    *,
    expected_content: bytes,
) -> None:
    if isinstance(attachment, Mapping):
        attachment_id = attachment.get("attachment_id")
        attachment_kind = attachment.get("attachment_kind")
        test_result_id = attachment.get("test_result_id")
        test_case_id = attachment.get("test_case_id")
        content_type = attachment.get("content_type")
        content_length = attachment.get("content_length")
    else:
        attachment_id = attachment.attachment_id
        attachment_kind = attachment.attachment_kind
        test_result_id = attachment.test_result_id
        test_case_id = attachment.test_case_id
        content_type = attachment.content_type
        content_length = attachment.content_length

    assert isinstance(attachment_id, int)
    assert isinstance(attachment_kind, str)

    request = {
        "attachment_id": attachment_id,
        "attachment_kind": attachment_kind,
        "test_result_id": test_result_id if isinstance(test_result_id, int) else None,
        "test_case_id": test_case_id if isinstance(test_case_id, int) else None,
    }
    prepared = await prepare_attachment_download(**request)
    payload = prepared.structured_content
    download_url = payload["download_url"]
    assert isinstance(download_url, str)
    async with httpx.AsyncClient() as client:
        response = await client.get(download_url)
        reused = await client.get(download_url)

    response.raise_for_status()
    assert response.content == expected_content
    if isinstance(content_type, str):
        assert response.headers["content-type"].startswith(content_type)
    if isinstance(content_length, int):
        assert len(response.content) == content_length
    assert response.headers["content-disposition"] == f'attachment; filename="{payload["name"]}"'
    assert reused.status_code == 404

    refreshed = await prepare_attachment_download(**request)
    refreshed_url = refreshed.structured_content["download_url"]
    assert isinstance(refreshed_url, str)
    assert refreshed_url != download_url
    async with httpx.AsyncClient() as client:
        refreshed_response = await client.get(refreshed_url)
    assert refreshed_response.content == expected_content
