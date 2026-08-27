"""Sandbox coverage for the exact TestOps test-result read."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from pathlib import Path

import httpx
import pytest

from src.client import AllureClient
from src.services.attachment_download_gateway import LoopbackAttachmentDownloadGateway
from src.services.attachment_download_service import (
    AttachmentDownloadConfig,
    AttachmentDownloadRuntimeHolder,
    AttachmentDownloadService,
    AttachmentKind,
    AttachmentPreparationRequest,
)
from src.services.launch_service import LaunchService
from src.services.test_result_service import AttachmentDetail, StepDetail, TestResultService
from tests.e2e.helpers.cleanup import CleanupTracker
from tests.e2e.test_launch_manual_execution import _create_launch_with_test_case

pytestmark = pytest.mark.asyncio(loop_scope="module")


async def test_get_test_result_returns_exact_result_with_stable_result_url(
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    test_run_id: str,
    tmp_path: Path,
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
        allure_client=allure_client,
        target_path=tmp_path / "result-evidence.txt",
        expected_content=b"Sandbox result detail evidence",
    )
    await _download_and_verify_evidence(
        step_attachment,
        allure_client=allure_client,
        target_path=tmp_path / "step-evidence.txt",
        expected_content=b"Sandbox step detail evidence",
    )


async def test_get_test_result_downloads_fixture_evidence_when_sandbox_provides_a_fixture(
    allure_client: AllureClient,
    cleanup_tracker: CleanupTracker,
    test_run_id: str,
    tmp_path: Path,
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
        allure_client=allure_client,
        target_path=tmp_path / "fixture-evidence.txt",
        expected_content=b"Sandbox fixture detail evidence",
    )


def _iter_step_attachments(steps: Sequence[StepDetail]) -> Iterator[AttachmentDetail]:
    for step in steps:
        yield from step.attachments
        yield from _iter_step_attachments(step.steps)


async def _download_and_verify_evidence(
    attachment: AttachmentDetail,
    *,
    allure_client: AllureClient,
    target_path: Path,
    expected_content: bytes,
) -> None:
    assert attachment.attachment_id is not None
    assert attachment.attachment_kind is not None
    holder = AttachmentDownloadRuntimeHolder()
    gateway = LoopbackAttachmentDownloadGateway(holder)
    service = AttachmentDownloadService(
        allure_client,
        holder=holder,
        config=AttachmentDownloadConfig(cache_parent=target_path.parent),
    )

    try:
        base_url = await gateway.start()
        prepared = await service.prepare(
            AttachmentPreparationRequest(
                attachment_id=attachment.attachment_id,
                kind=AttachmentKind(attachment.attachment_kind),
                test_result_id=attachment.test_result_id,
                test_case_id=attachment.test_case_id,
            ),
            public_base_url=base_url,
        )
        async with httpx.AsyncClient() as client:
            response = await client.get(prepared.download_url)
        response.raise_for_status()
        target_path.write_bytes(response.content)

        assert target_path.read_bytes() == expected_content
        if attachment.content_type is not None:
            assert response.headers["content-type"].startswith(attachment.content_type)
        if attachment.content_length is not None:
            assert len(response.content) == attachment.content_length
        assert response.headers["content-disposition"] == f'attachment; filename="{prepared.filename}"'
        async with httpx.AsyncClient() as client:
            reused = await client.get(prepared.download_url)
        assert reused.status_code == 404
    finally:
        target_path.unlink(missing_ok=True)
        await gateway.close()
        await holder.close()
