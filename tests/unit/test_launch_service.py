"""Unit tests for LaunchService."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from src.client import AllureClient, LaunchUploadResponseDto
from src.client.exceptions import AllureAPIError, AllureNotFoundError, AllureValidationError, LaunchNotFoundError
from src.client.generated.models.aql_validate_response_dto import AqlValidateResponseDto
from src.client.generated.models.body_step_dto import BodyStepDto
from src.client.generated.models.find_all29200_response import FindAll29200Response
from src.client.generated.models.launch_dto import LaunchDto
from src.client.generated.models.launch_preview_dto import LaunchPreviewDto
from src.client.generated.models.page_launch_dto import PageLaunchDto
from src.client.generated.models.page_launch_preview_dto import PageLaunchPreviewDto
from src.client.generated.models.page_test_result_flat_dto import PageTestResultFlatDto
from src.client.generated.models.shared_step_scenario_dto_steps_inner import SharedStepScenarioDtoStepsInner
from src.client.generated.models.test_case_scenario_v2_dto import TestCaseScenarioV2Dto
from src.client.generated.models.test_fixture_result_v2_dto import TestFixtureResultV2Dto
from src.client.generated.models.test_result_attachment_row_dto import TestResultAttachmentRowDto
from src.client.generated.models.test_result_attachment_step_dto import TestResultAttachmentStepDto
from src.client.generated.models.test_result_attachment_step_dto_all_of_attachment import (
    TestResultAttachmentStepDtoAllOfAttachment,
)
from src.client.generated.models.test_result_body_step_dto import TestResultBodyStepDto
from src.client.generated.models.test_result_dto import TestResultDto
from src.client.generated.models.test_result_flat_dto import TestResultFlatDto
from src.client.generated.models.test_result_row_dto import TestResultRowDto
from src.client.generated.models.test_result_scenario_step_dto import TestResultScenarioStepDto
from src.client.generated.models.test_result_scenario_v2_dto import TestResultScenarioV2Dto
from src.client.generated.models.test_result_scenario_v2_dto_steps_inner import TestResultScenarioV2DtoStepsInner
from src.client.generated.models.test_session_response_dto import TestSessionResponseDto
from src.services.launch_service import LaunchDeleteResult, LaunchService


@pytest.fixture
def mock_client() -> MagicMock:
    client = MagicMock(spec=AllureClient)
    client.get_project.return_value = 1
    client.create_launch = AsyncMock()
    client.list_launches = AsyncMock()
    client.search_launches_aql = AsyncMock()
    client.validate_launch_query = AsyncMock(return_value=(True, 0))
    client.get_launch = AsyncMock()
    client.delete_launch = AsyncMock()
    client.close_launch = AsyncMock()
    client.reopen_launch = AsyncMock()
    client.list_launch_test_results = AsyncMock()
    client.rerun_test_results_bulk = AsyncMock()
    client.start_external_run = AsyncMock()
    client.start_manual_test_session = AsyncMock()
    client.submit_manual_test_results = AsyncMock()
    client.create_test_result = AsyncMock()
    client.resolve_test_result = AsyncMock()
    client.get_test_result = AsyncMock()
    client.get_test_result_execution = AsyncMock(return_value=TestResultScenarioV2Dto(steps=[]))
    client.get_test_result_execution_raw = AsyncMock(return_value={"steps": []})
    client.get_test_case_scenario = AsyncMock()
    client.add_test_result_attachment = AsyncMock()
    client.create_test_result_attachments = AsyncMock()
    client.add_test_fixture_attachment = AsyncMock()
    client.patch_test_result = AsyncMock()
    client.patch_test_result_attachment = AsyncMock()
    client.update_test_result_attachment_content = AsyncMock(return_value=200)
    client.get_test_result_fixtures = AsyncMock()
    client.list_launch_test_results.return_value = PageTestResultFlatDto(
        content=[],
        total_elements=0,
        number=0,
        size=100,
        total_pages=1,
    )
    return client


@pytest.fixture
def service(mock_client: MagicMock) -> LaunchService:
    return LaunchService(client=mock_client)


def _manual_execution_with_steps(*steps: TestResultScenarioV2DtoStepsInner) -> TestResultScenarioV2Dto:
    return TestResultScenarioV2Dto.model_construct(steps=list(steps))


def _body_step(body: str) -> TestResultScenarioV2DtoStepsInner:
    return TestResultScenarioV2DtoStepsInner.model_construct(
        actual_instance=TestResultBodyStepDto.model_construct(type="TestResultBodyStepDto", body=body)
    )


def _attachment_step(attachment_id: int, name: str) -> TestResultScenarioV2DtoStepsInner:
    attachment_row = TestResultAttachmentRowDto.model_construct(
        entity="TestResultAttachmentRowDto",
        id=attachment_id,
        name=name,
    )
    return TestResultScenarioV2DtoStepsInner.model_construct(
        actual_instance=TestResultAttachmentStepDto.model_construct(
            type="TestResultAttachmentStepDto",
            attachment_id=attachment_id,
            attachment=TestResultAttachmentStepDtoAllOfAttachment.model_construct(actual_instance=attachment_row),
        )
    )


def _scenario_body_step(body: str) -> SharedStepScenarioDtoStepsInner:
    return SharedStepScenarioDtoStepsInner(actual_instance=BodyStepDto.model_construct(type="BodyStepDto", body=body))


@pytest.mark.asyncio
async def test_create_launch_minimal(service: LaunchService, mock_client: MagicMock) -> None:
    launch = LaunchDto(id=10, name="Launch 1", project_id=1)
    mock_client.create_launch.return_value = launch

    result = await service.create_launch(name="Launch 1")

    assert result.id == 10
    assert result.name == "Launch 1"
    mock_client.create_launch.assert_called_once()


@pytest.mark.asyncio
async def test_create_launch_invalid_name(service: LaunchService) -> None:
    with pytest.raises(AllureValidationError, match="Launch name is required"):
        await service.create_launch(name="")


@pytest.mark.asyncio
async def test_create_launch_invalid_tag_type(service: LaunchService) -> None:
    with pytest.raises(AllureValidationError, match="Tags must be a list"):
        await service.create_launch(name="Launch", tags="tag")  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_list_launches_page_launch_dto(service: LaunchService, mock_client: MagicMock) -> None:
    page = PageLaunchDto(content=[LaunchDto(id=1, name="L1")], total_elements=1, number=0, size=20, total_pages=1)
    response = FindAll29200Response(page)
    mock_client.list_launches.return_value = response

    result = await service.list_launches(page=0, size=20)

    assert result.total == 1
    assert result.items[0].name == "L1"
    assert result.page == 0
    assert result.size == 20
    assert result.total_pages == 1


@pytest.mark.asyncio
async def test_list_launches_page_launch_preview_dto(service: LaunchService, mock_client: MagicMock) -> None:
    page = PageLaunchPreviewDto(
        content=[LaunchPreviewDto(id=2, name="Preview")], total_elements=1, number=0, size=20, total_pages=1
    )
    response = FindAll29200Response(page)
    mock_client.list_launches.return_value = response

    result = await service.list_launches(page=0, size=20)

    assert result.total == 1
    assert result.items[0].name == "Preview"
    assert result.page == 0
    assert result.size == 20
    assert result.total_pages == 1


@pytest.mark.asyncio
async def test_list_launches_falls_back_to_aql_when_search_is_rejected(
    service: LaunchService, mock_client: MagicMock
) -> None:
    page = PageLaunchDto(
        content=[LaunchDto(id=4, name="[Agent] Launch")],
        total_elements=1,
        number=0,
        size=20,
        total_pages=1,
    )
    mock_client.list_launches.side_effect = AllureValidationError("invalid search")
    mock_client.search_launches_aql.return_value = page

    result = await service.list_launches(search="[Agent]")

    assert result.total == 1
    mock_client.search_launches_aql.assert_awaited_once_with(
        project_id=1,
        rql='name ~= "[Agent]"',
        page=0,
        size=20,
        sort=None,
    )


@pytest.mark.asyncio
async def test_list_launches_does_not_fallback_when_filter_scope_is_present(
    service: LaunchService, mock_client: MagicMock
) -> None:
    mock_client.list_launches.side_effect = AllureValidationError("invalid search")

    with pytest.raises(AllureValidationError, match="invalid search"):
        await service.list_launches(search="[Agent]", filter_id=42)

    mock_client.search_launches_aql.assert_not_awaited()


@pytest.mark.asyncio
async def test_list_launches_treats_blank_search_as_no_filter(service: LaunchService, mock_client: MagicMock) -> None:
    page = PageLaunchDto(
        content=[LaunchDto(id=5, name="No Filter")],
        total_elements=1,
        number=0,
        size=20,
        total_pages=1,
    )
    mock_client.list_launches.return_value = FindAll29200Response(page)

    result = await service.list_launches(search="   ")

    assert result.total == 1
    mock_client.list_launches.assert_awaited_once_with(
        project_id=1,
        page=0,
        size=20,
        search=None,
        filter_id=None,
        sort=None,
    )
    mock_client.search_launches_aql.assert_not_awaited()


@pytest.mark.asyncio
async def test_search_launches_aql(service: LaunchService, mock_client: MagicMock) -> None:
    page = PageLaunchDto(content=[LaunchDto(id=3, name="AQL")], total_elements=1, number=0, size=20, total_pages=1)
    mock_client.search_launches_aql.return_value = page

    result = await service.search_launches_aql(rql='name="AQL"')

    assert result.total == 1
    assert result.items[0].name == "AQL"
    assert result.page == 0
    assert result.size == 20
    assert result.total_pages == 1
    mock_client.search_launches_aql.assert_called_once()


@pytest.mark.asyncio
async def test_list_launches_invalid_project_id(service: LaunchService) -> None:
    service._project_id = 0
    with pytest.raises(AllureValidationError, match="Project ID is required"):
        await service.list_launches()


@pytest.mark.asyncio
async def test_get_launch_valid(service: LaunchService, mock_client: MagicMock) -> None:
    launch = LaunchDto(id=12, name="Launch")
    mock_client.get_launch.return_value = launch

    result = await service.get_launch(12)

    assert result.id == 12
    mock_client.get_launch.assert_called_once_with(12)


@pytest.mark.asyncio
async def test_get_launch_invalid_id(service: LaunchService) -> None:
    with pytest.raises(AllureValidationError, match="Launch ID must be a positive integer"):
        await service.get_launch(0)


@pytest.mark.asyncio
async def test_get_launch_not_found_maps_error(service: LaunchService, mock_client: MagicMock) -> None:
    mock_client.get_launch.side_effect = AllureNotFoundError("Not found", status_code=404, response_body="{}")

    with pytest.raises(LaunchNotFoundError, match="Launch ID 99 not found"):
        await service.get_launch(99)


@pytest.mark.asyncio
async def test_delete_launch_success(service: LaunchService, mock_client: MagicMock) -> None:
    result = await service.delete_launch(88)

    assert isinstance(result, LaunchDeleteResult)
    assert result.launch_id == 88
    assert result.status == "deleted"
    assert result.message == "Launch 88 was deleted."
    mock_client.get_launch.assert_not_called()
    mock_client.delete_launch.assert_called_once_with(88)


@pytest.mark.asyncio
async def test_delete_launch_invalid_id(service: LaunchService) -> None:
    with pytest.raises(AllureValidationError, match="Launch ID must be a positive integer"):
        await service.delete_launch(0)


@pytest.mark.asyncio
async def test_delete_launch_already_deleted(service: LaunchService, mock_client: MagicMock) -> None:
    mock_client.delete_launch.side_effect = AllureNotFoundError("Not found", status_code=404, response_body="{}")

    result = await service.delete_launch(99)

    assert result.launch_id == 99
    assert result.status == "already_deleted"
    assert "already deleted" in result.message
    mock_client.get_launch.assert_not_called()
    mock_client.delete_launch.assert_called_once_with(99)


@pytest.mark.asyncio
async def test_delete_launch_repeated_success_does_not_fetch_deleted_launch(
    service: LaunchService, mock_client: MagicMock
) -> None:
    first_result = await service.delete_launch(99)
    second_result = await service.delete_launch(99)

    assert first_result.status == "deleted"
    assert second_result.status == "deleted"
    mock_client.get_launch.assert_not_called()
    assert mock_client.delete_launch.await_count == 2


@pytest.mark.asyncio
async def test_delete_launch_propagates_non_not_found_api_error(service: LaunchService, mock_client: MagicMock) -> None:
    mock_client.delete_launch.side_effect = AllureAPIError("Server error", status_code=500, response_body="{}")

    with pytest.raises(AllureAPIError, match="Server error"):
        await service.delete_launch(99)

    mock_client.get_launch.assert_not_called()
    mock_client.delete_launch.assert_called_once_with(99)


@pytest.mark.asyncio
async def test_validate_launch_query_returns_validation_tuple(service: LaunchService, mock_client: MagicMock) -> None:
    mock_client.validate_launch_query.return_value = AqlValidateResponseDto(valid=True, count=3)

    result = await service.validate_launch_query('name = "Run"')

    assert result == (True, 3)
    mock_client.validate_launch_query.assert_awaited_once_with(project_id=1, rql='name = "Run"')


@pytest.mark.asyncio
async def test_validate_launch_query_rejects_unexpected_api_payload(
    service: LaunchService, mock_client: MagicMock
) -> None:
    mock_client.validate_launch_query.return_value = object()

    with pytest.raises(AllureValidationError, match="Unexpected validation response from API"):
        await service.validate_launch_query('name = "Run"')


@pytest.mark.asyncio
async def test_close_launch_valid(service: LaunchService, mock_client: MagicMock) -> None:
    open_launch = LaunchDto(id=15, name="Launch 15", closed=False)
    closed_launch = LaunchDto(id=15, name="Launch 15", closed=True)
    mock_client.get_launch.side_effect = [open_launch, closed_launch]

    result = await service.close_launch(15)

    assert result.id == 15
    assert result.closed is True
    assert getattr(result, "close_report_generation", None) == "scheduled"
    mock_client.close_launch.assert_called_once_with(15)
    assert mock_client.get_launch.call_count == 2


@pytest.mark.asyncio
async def test_close_launch_when_already_closed_marks_report_state(
    service: LaunchService,
    mock_client: MagicMock,
) -> None:
    already_closed = LaunchDto(id=18, name="Launch 18", closed=True)
    mock_client.get_launch.side_effect = [already_closed, already_closed]

    result = await service.close_launch(18)

    assert result.closed is True
    assert getattr(result, "close_report_generation", None) == "already-closed"


@pytest.mark.asyncio
async def test_close_launch_invalid_id(service: LaunchService) -> None:
    with pytest.raises(AllureValidationError, match="Launch ID must be a positive integer"):
        await service.close_launch(0)


@pytest.mark.asyncio
async def test_close_launch_not_found_maps_error(service: LaunchService, mock_client: MagicMock) -> None:
    mock_client.close_launch.side_effect = AllureNotFoundError("Not found", status_code=404, response_body="{}")

    with pytest.raises(LaunchNotFoundError, match="Launch ID 41 not found"):
        await service.close_launch(41)


@pytest.mark.asyncio
async def test_close_launch_invalid_transition_bubbles_api_error(
    service: LaunchService, mock_client: MagicMock
) -> None:
    mock_client.close_launch.side_effect = AllureAPIError(
        "API request failed: Launch is already closed",
        status_code=409,
        response_body='{"message":"already closed"}',
    )

    with pytest.raises(AllureAPIError, match="already closed"):
        await service.close_launch(20)


@pytest.mark.asyncio
async def test_reopen_launch_valid(service: LaunchService, mock_client: MagicMock) -> None:
    reopened_launch = LaunchDto(id=16, name="Launch 16", closed=False)
    mock_client.get_launch.return_value = reopened_launch

    result = await service.reopen_launch(16)

    assert result.id == 16
    assert result.closed is False
    mock_client.reopen_launch.assert_called_once_with(16)
    mock_client.get_launch.assert_called_once_with(16)


@pytest.mark.asyncio
async def test_reopen_launch_unexpectedly_closed_raises(service: LaunchService, mock_client: MagicMock) -> None:
    mock_client.get_launch.return_value = LaunchDto(id=17, name="Launch 17", closed=True)

    with pytest.raises(AllureAPIError, match="was not reopened by API"):
        await service.reopen_launch(17)


@pytest.mark.asyncio
async def test_reopen_launch_invalid_id(service: LaunchService) -> None:
    with pytest.raises(AllureValidationError, match="Launch ID must be a positive integer"):
        await service.reopen_launch(0)


@pytest.mark.asyncio
async def test_reopen_launch_not_found_maps_error(service: LaunchService, mock_client: MagicMock) -> None:
    mock_client.reopen_launch.side_effect = AllureNotFoundError("Not found", status_code=404, response_body="{}")

    with pytest.raises(LaunchNotFoundError, match="Launch ID 42 not found"):
        await service.reopen_launch(42)


@pytest.mark.asyncio
async def test_reopen_launch_invalid_transition_bubbles_api_error(
    service: LaunchService, mock_client: MagicMock
) -> None:
    mock_client.reopen_launch.side_effect = AllureAPIError(
        "API request failed: Launch is already open",
        status_code=409,
        response_body='{"message":"already open"}',
    )

    with pytest.raises(AllureAPIError, match="already open"):
        await service.reopen_launch(21)


@pytest.mark.asyncio
async def test_upload_results_to_launch_calls_client(service: LaunchService, mock_client: MagicMock) -> None:
    upload_response = LaunchUploadResponseDto(launch_id=22, files_count=2)
    mock_client.upload_results_to_launch = AsyncMock(return_value=upload_response)

    result = await service.upload_results_to_launch(launch_id=22, files=[("a.json", b"{}")])

    assert result.launch_id == 22
    assert result.files_count == 2
    mock_client.upload_results_to_launch.assert_called_once()


@pytest.mark.asyncio
async def test_upload_results_to_launch_requires_files(service: LaunchService) -> None:
    with pytest.raises(AllureValidationError, match="files must be a non-empty list"):
        await service.upload_results_to_launch(launch_id=22, files=[])


@pytest.mark.asyncio
async def test_add_results_batches_normalized_results_for_a_launch(
    service: LaunchService, mock_client: MagicMock
) -> None:
    mock_client.create_test_result.side_effect = [TestResultDto(id=501), TestResultDto(id=502)]

    result = await service.add_results(
        launch_id=22,
        results=[
            {
                "test_case_id": 91,
                "status": "passed",
                "start": 1000,
                "stop": 1250,
                "message": "Completed",
            },
            {
                "test_case_id": 92,
                "status": "failed",
                "duration": 300,
            },
        ],
    )

    assert result.launch_id == 22
    assert result.requested_count == 2
    assert result.uploaded_count == 2
    assert result.result_ids == [501, 502]
    assert result.failures == []
    first_payload = mock_client.create_test_result.await_args_list[0].args[0]
    second_payload = mock_client.create_test_result.await_args_list[1].args[0]
    assert first_payload.launch_id == 22
    assert first_payload.test_case_id == 91
    assert first_payload.name == "Test case 91"
    assert first_payload.status.value == "passed"
    assert first_payload.duration == 250
    assert first_payload.message == "Completed"
    assert second_payload.duration == 300


@pytest.mark.asyncio
async def test_add_results_reports_partial_failures(service: LaunchService, mock_client: MagicMock) -> None:
    mock_client.create_test_result.side_effect = [
        TestResultDto(id=501),
        AllureAPIError("TestOps rejected the result"),
    ]

    result = await service.add_results(
        launch_id=22,
        results=[
            {"test_case_id": 91, "status": "passed"},
            {"test_case_id": 92, "status": "failed"},
        ],
    )

    assert result.requested_count == 2
    assert result.uploaded_count == 1
    assert result.result_ids == [501]
    assert [(failure.index, failure.message) for failure in result.failures] == [(1, "TestOps rejected the result")]


@pytest.mark.asyncio
async def test_add_results_rejects_batches_larger_than_limit(service: LaunchService, mock_client: MagicMock) -> None:
    with pytest.raises(AllureValidationError, match="at most 1000 items"):
        await service.add_results(
            launch_id=22,
            results=[{"test_case_id": 91, "status": "passed"}] * 1001,
        )

    mock_client.get_launch.assert_not_awaited()
    mock_client.create_test_result.assert_not_awaited()


@pytest.mark.asyncio
async def test_add_results_rejects_invalid_status_before_creating_a_session(
    service: LaunchService, mock_client: MagicMock
) -> None:
    with pytest.raises(AllureValidationError, match="Allowed values: failed, broken, passed, skipped, unknown"):
        await service.add_results(
            launch_id=22,
            results=[{"test_case_id": 91, "status": "Kinda Passed"}],
        )

    mock_client.get_launch.assert_not_awaited()
    mock_client.create_test_result.assert_not_awaited()


@pytest.mark.asyncio
async def test_add_results_maps_missing_launch_to_launch_not_found(
    service: LaunchService, mock_client: MagicMock
) -> None:
    mock_client.get_launch.side_effect = AllureNotFoundError("missing", status_code=404, response_body="{}")

    with pytest.raises(LaunchNotFoundError, match="Launch ID 22 not found"):
        await service.add_results(
            launch_id=22,
            results=[{"test_case_id": 91, "status": "passed"}],
        )

    mock_client.create_test_result.assert_not_awaited()


@pytest.mark.asyncio
async def test_list_launch_test_results_applies_manual_and_failed_filters(
    service: LaunchService, mock_client: MagicMock
) -> None:
    mock_client.list_launch_test_results.return_value = PageTestResultFlatDto(
        content=[
            TestResultFlatDto(id=101, test_case_id=11, name="Manual Failed", manual=True, status="failed"),
            TestResultFlatDto(id=102, test_case_id=12, name="Automated Passed", manual=False, status="passed"),
        ],
        total_elements=2,
        number=0,
        size=100,
        total_pages=1,
    )

    result = await service.list_launch_test_results(launch_id=9, manual_only=True, failed_only=True, size=20)

    assert result.total == 1
    assert len(result.items) == 1
    assert result.items[0].result_id == 101
    mock_client.list_launch_test_results.assert_awaited_once_with(
        9,
        page=0,
        size=100,
        search=None,
        filter_id=None,
        sort=None,
    )


@pytest.mark.asyncio
async def test_resolve_launch_test_result_for_test_case_returns_unique_active_match(
    service: LaunchService,
    mock_client: MagicMock,
) -> None:
    mock_client.list_launch_test_results.return_value = PageTestResultFlatDto(
        content=[
            TestResultFlatDto(id=101, test_case_id=11, name="Manual Failed", manual=True, status="failed"),
            TestResultFlatDto(id=102, test_case_id=11, name="Manual Active", manual=True, status=None),
            TestResultFlatDto(id=103, test_case_id=12, name="Other", manual=True, status=None),
        ],
        total_elements=3,
        number=0,
        size=100,
        total_pages=1,
    )

    result = await service.resolve_launch_test_result_for_test_case(launch_id=9, test_case_id=11, status=None)

    assert result.result_id == 102
    assert result.status is None


@pytest.mark.asyncio
async def test_resolve_launch_test_result_for_test_case_rejects_ambiguous_matches(
    service: LaunchService,
    mock_client: MagicMock,
) -> None:
    mock_client.list_launch_test_results.return_value = PageTestResultFlatDto(
        content=[
            TestResultFlatDto(id=101, test_case_id=11, name="Manual Active 1", manual=True, status=None),
            TestResultFlatDto(id=102, test_case_id=11, name="Manual Active 2", manual=True, status=None),
        ],
        total_elements=2,
        number=0,
        size=100,
        total_pages=1,
    )

    with pytest.raises(AllureValidationError, match="Expected exactly one visible manual launch result"):
        await service.resolve_launch_test_result_for_test_case(launch_id=9, test_case_id=11, status=None)


@pytest.mark.asyncio
async def test_resolve_launch_test_result_for_test_case_reports_missing_match(
    service: LaunchService,
    mock_client: MagicMock,
) -> None:
    mock_client.list_launch_test_results.return_value = PageTestResultFlatDto(
        content=[TestResultFlatDto(id=101, test_case_id=11, name="Manual Failed", manual=True, status="failed")],
        total_elements=1,
        number=0,
        size=100,
        total_pages=1,
    )

    with pytest.raises(AllureNotFoundError, match="No visible manual launch result found"):
        await service.resolve_launch_test_result_for_test_case(launch_id=9, test_case_id=11, status=None)


@pytest.mark.asyncio
async def test_rerun_test_results_manually_builds_bulk_payload(service: LaunchService, mock_client: MagicMock) -> None:
    mock_client.list_launch_test_results.return_value = PageTestResultFlatDto(
        content=[
            TestResultFlatDto(id=201, test_case_id=11, name="Manual Failed 1", manual=True, status="failed"),
            TestResultFlatDto(id=202, test_case_id=12, name="Manual Failed 2", manual=True, status="failed"),
        ],
        total_elements=2,
        number=0,
        size=100,
        total_pages=1,
    )

    result = await service.rerun_test_results_manually(
        launch_id=15,
        result_ids=[201, 202],
        assignees=["alice"],
        force_manual=True,
    )

    assert result.scheduled_count == 2
    payload = mock_client.rerun_test_results_bulk.await_args.args[0]
    assert payload.force_manual is True
    assert payload.assignees == ["alice"]
    assert payload.selection.launch_id == 15
    assert payload.selection.leafs_include == [201, 202]


@pytest.mark.asyncio
async def test_rerun_test_results_manually_identifies_missing_result_ids(
    service: LaunchService, mock_client: MagicMock
) -> None:
    mock_client.list_launch_test_results.return_value = PageTestResultFlatDto(
        content=[TestResultFlatDto(id=201, test_case_id=11, name="Manual Failed 1", manual=True, status="failed")],
        total_elements=1,
        number=0,
        size=100,
        total_pages=1,
    )

    with pytest.raises(AllureNotFoundError, match="Result ID 202 not found in launch ID 15"):
        await service.rerun_test_results_manually(launch_id=15, result_ids=[201, 202])

    mock_client.rerun_test_results_bulk.assert_not_awaited()


@pytest.mark.asyncio
async def test_rerun_test_results_manually_falls_back_to_direct_lookup_for_new_results(
    service: LaunchService, mock_client: MagicMock
) -> None:
    mock_client.list_launch_test_results.return_value = PageTestResultFlatDto(
        content=[],
        total_elements=0,
        number=0,
        size=100,
        total_pages=1,
    )
    mock_client.get_test_result.return_value = TestResultDto(id=201, launch_id=15, name="Manual Failed 1")

    result = await service.rerun_test_results_manually(
        launch_id=15,
        result_ids=[201],
        assignees=["alice"],
        force_manual=True,
    )

    assert result.scheduled_count == 1
    mock_client.get_test_result.assert_awaited_once_with(201)
    mock_client.rerun_test_results_bulk.assert_awaited_once()


@pytest.mark.asyncio
async def test_rerun_test_results_manually_rejects_results_from_other_launches(
    service: LaunchService, mock_client: MagicMock
) -> None:
    mock_client.list_launch_test_results.return_value = PageTestResultFlatDto(
        content=[],
        total_elements=0,
        number=0,
        size=100,
        total_pages=1,
    )
    mock_client.get_test_result.return_value = TestResultDto(id=202, launch_id=99, name="Manual Failed 2")

    with pytest.raises(AllureNotFoundError, match="Result ID 202 not found in launch ID 15"):
        await service.rerun_test_results_manually(launch_id=15, result_ids=[202])

    mock_client.rerun_test_results_bulk.assert_not_awaited()


@pytest.mark.asyncio
async def test_rerun_test_results_manually_reports_multiple_missing_ids_after_direct_lookup(
    service: LaunchService, mock_client: MagicMock
) -> None:
    mock_client.list_launch_test_results.return_value = PageTestResultFlatDto(
        content=[],
        total_elements=0,
        number=0,
        size=100,
        total_pages=1,
    )
    mock_client.get_test_result.side_effect = [
        AllureNotFoundError("Not found", status_code=404, response_body="{}"),
        AllureNotFoundError("Not found", status_code=404, response_body="{}"),
    ]

    with pytest.raises(AllureNotFoundError, match=r"Result IDs 203, 204 not found in launch ID 15"):
        await service.rerun_test_results_manually(launch_id=15, result_ids=[203, 204])

    assert mock_client.get_test_result.await_count == 2
    mock_client.rerun_test_results_bulk.assert_not_awaited()


@pytest.mark.asyncio
async def test_start_manual_test_session_maps_environment(service: LaunchService, mock_client: MagicMock) -> None:
    mock_client.start_manual_test_session.return_value = TestSessionResponseDto(
        id=44,
        launch_id=22,
        job_id=7,
        job_run_id=8,
        project_id=1,
    )

    result = await service.start_manual_test_session(
        22,
        environment=[{"key": "browser", "value": "chrome"}],
    )

    assert result.test_session_id == 44
    mock_client.start_external_run.assert_awaited_once()
    external_payload = mock_client.start_external_run.await_args.args[0]
    assert external_payload.project_id == 1
    assert external_payload.launch.id == 22
    assert isinstance(external_payload.job.uid, str)
    assert isinstance(external_payload.job_run.uid, str)
    payload = mock_client.start_manual_test_session.await_args.args[0]
    assert payload.launch_id == 22
    assert payload.project_id == 1
    assert payload.job_uid == external_payload.job.uid
    assert payload.job_run_uid == external_payload.job_run.uid
    assert payload.environment[0].key == "browser"
    assert payload.environment[0].value == "chrome"


@pytest.mark.asyncio
async def test_submit_manual_test_results_maps_nested_steps(service: LaunchService, mock_client: MagicMock) -> None:
    mock_client.get_test_result.return_value = TestResultDto(
        id=91,
        launch_id=12,
        test_case_id=91,
        name="Manual login test",
        full_name="Manual login test",
        manual=True,
    )
    mock_client.resolve_test_result.return_value = TestResultRowDto(
        id=91,
        name="Manual login test",
        test_case_id=91,
        status="passed",
    )

    result = await service.submit_manual_test_results(
        44,
        results=[
            {
                "result_id": 91,
                "status": "passed",
                "start": 1000,
                "stop": 2000,
                "message": "Completed",
                "steps": [
                    {
                        "type": "body",
                        "body": "Open the launch",
                        "status": "passed",
                    }
                ],
            }
        ],
    )

    assert result.result_ids == [91]
    resolve_payload = mock_client.resolve_test_result.await_args.args[1]
    assert resolve_payload["status"] == "passed"
    assert resolve_payload["start"] == 1000
    assert resolve_payload["stop"] == 2000
    assert resolve_payload["duration"] == 1000
    assert resolve_payload["message"] == "Completed"
    execution = resolve_payload["execution"]
    assert isinstance(execution, dict)
    steps = execution["steps"]
    assert isinstance(steps, list)
    assert steps[0]["type"] == "body"
    assert steps[0]["body"] == "Open the launch"
    mock_client.create_test_result.assert_not_awaited()
    mock_client.patch_test_result.assert_not_awaited()


@pytest.mark.asyncio
async def test_submit_manual_test_results_rejects_payload_without_result_or_launch_context(
    service: LaunchService,
) -> None:
    with pytest.raises(AllureValidationError, match=r"results\[0\]\.result_id is required"):
        await service.submit_manual_test_results(
            44,
            results=[
                {
                    "status": "passed",
                }
            ],
        )


@pytest.mark.asyncio
async def test_submit_manual_test_results_uses_create_fallback_without_result_id(
    service: LaunchService,
    mock_client: MagicMock,
) -> None:
    mock_client.create_test_result.return_value = TestResultDto(
        id=401,
        name="Fallback manual result",
        full_name="Fallback manual result",
    )

    result = await service.submit_manual_test_results(
        45,
        results=[
            {
                "launch_id": 13,
                "test_case_id": 92,
                "name": "Fallback manual result",
                "status": "passed",
            }
        ],
    )

    assert result.result_ids == [401]
    create_payload = mock_client.create_test_result.await_args.args[0]
    assert create_payload.launch_id == 13
    assert create_payload.test_case_id == 92
    assert create_payload.status == "passed"
    mock_client.resolve_test_result.assert_not_awaited()


def test_build_upload_test_result_maps_full_payload(service: LaunchService) -> None:
    upload_payload = service._build_upload_test_result(
        {
            "test_case_id": 92,
            "name": "Fallback manual result",
            "status": "failed",
            "start": 1000,
            "stop": 2300,
            "message": "Observed a failure",
            "trace": "stacktrace",
            "description": "Longer operator notes",
            "precondition": "Session started",
            "expected_result": "User reaches the dashboard",
            "parameters": [
                {
                    "name": "browser",
                    "value": "chrome",
                }
            ],
            "steps": [
                {
                    "type": "body",
                    "body": "Open login page",
                    "message": "Page loaded",
                    "trace": "body-step-trace",
                    "status": "passed",
                    "start": 1000,
                    "stop": 1200,
                },
                {
                    "type": "expected",
                    "body": "Dashboard is visible",
                    "message": "Expected outcome",
                    "status": "failed",
                    "start": 1200,
                    "stop": 1800,
                },
                {
                    "type": "attachment",
                    "status": "failed",
                    "start": 1800,
                    "stop": 2300,
                    "attachment": {
                        "name": "screenshot.txt",
                        "content_type": "text/plain",
                    },
                },
            ],
        },
        index=0,
    )

    assert upload_payload.test_case_id == "92"
    assert upload_payload.name == "Fallback manual result"
    assert upload_payload.full_name == "Fallback manual result"
    assert upload_payload.uuid is None
    assert upload_payload.history_id is None
    assert upload_payload.status is not None
    assert upload_payload.status.value.lower() == "failed"
    assert upload_payload.start == 1000
    assert upload_payload.stop == 2300
    assert upload_payload.message == "Observed a failure"
    assert upload_payload.trace == "stacktrace"
    assert upload_payload.description == "Longer operator notes"
    assert upload_payload.precondition == "Session started"
    assert upload_payload.expected_result == "User reaches the dashboard"
    assert upload_payload.parameters is not None
    assert len(upload_payload.parameters) == 1
    assert upload_payload.parameters[0].name == "browser"
    assert upload_payload.parameters[0].value == "chrome"
    assert upload_payload.steps is not None
    assert len(upload_payload.steps) == 3

    body_step = upload_payload.steps[0].actual_instance
    assert body_step is not None
    assert body_step.type == "UploadTestResultBodyStepDto"
    assert body_step.body == "Open login page"
    assert body_step.message == "Page loaded"
    assert body_step.trace == "body-step-trace"

    expected_step = upload_payload.steps[1].actual_instance
    assert expected_step is not None
    assert expected_step.type == "UploadTestResultExpectedBodyStepDto"
    assert expected_step.body == "Dashboard is visible"
    assert expected_step.message == "Expected outcome"

    attachment_step = upload_payload.steps[2].actual_instance
    assert attachment_step is not None
    assert attachment_step.type == "UploadTestResultAttachmentStepDto"
    assert attachment_step.attachment.name == "screenshot.txt"
    assert attachment_step.attachment.content_type == "text/plain"


def test_build_upload_test_result_requires_status(service: LaunchService) -> None:
    with pytest.raises(AllureValidationError, match=r"results\[0\]\.status is required"):
        service._build_upload_test_result({"test_case_id": 92}, index=0)


def test_build_upload_test_result_rejects_unsupported_upload_identities(service: LaunchService) -> None:
    with pytest.raises(AllureValidationError, match=r"results\[0\]\.uuid is not supported"):
        service._build_upload_test_result({"test_case_id": 92, "status": "passed", "uuid": "external-id"}, index=0)


def test_build_upload_step_validation_paths(service: LaunchService) -> None:
    with pytest.raises(AllureValidationError, match=r"results\[0\]\.steps\[0\] must be a dictionary"):
        service._build_upload_step("bad-step", result_index=0, step_index=0)  # type: ignore[arg-type]

    with pytest.raises(AllureValidationError, match=r"results\[0\]\.steps\[1\]\.type is required"):
        service._build_upload_step({}, result_index=0, step_index=1)

    with pytest.raises(AllureValidationError, match="attachment is required for attachment steps"):
        service._build_upload_step({"type": "attachment"}, result_index=0, step_index=2)

    with pytest.raises(AllureValidationError, match="must be one of: body, expected, attachment"):
        service._build_upload_step({"type": "mystery"}, result_index=0, step_index=3)


@pytest.mark.asyncio
async def test_submit_manual_test_results_maps_expected_attachment_steps_and_parameters(
    service: LaunchService, mock_client: MagicMock
) -> None:
    mock_client.get_test_result.return_value = TestResultDto(
        id=92,
        launch_id=13,
        test_case_id=92,
        name="Manual upload with evidence",
        full_name="Manual upload with evidence",
        manual=True,
    )
    mock_client.resolve_test_result.return_value = TestResultRowDto(
        id=92,
        name="Manual upload with evidence",
        test_case_id=92,
        status="failed",
    )

    result = await service.submit_manual_test_results(
        45,
        results=[
            {
                "result_id": 92,
                "status": "failed",
                "start": 1000,
                "stop": 2000,
                "steps": [
                    {
                        "type": "expected",
                        "body": "Verify error banner",
                        "status": "passed",
                        "message": "Banner visible",
                    },
                    {
                        "type": "attachment",
                        "status": "failed",
                        "attachment": {
                            "name": "evidence.txt",
                            "content_type": "text/plain",
                        },
                    },
                ],
                "parameters": [
                    {
                        "name": "browser",
                        "value": "chrome",
                    }
                ],
            }
        ],
    )

    resolve_payload = mock_client.resolve_test_result.await_args.args[1]
    execution = resolve_payload["execution"]
    assert isinstance(execution, dict)
    steps = execution["steps"]
    assert isinstance(steps, list)
    assert len(steps) == 2
    assert steps[0]["type"] == "expected_body"
    assert steps[0]["body"] == "Verify error banner"
    assert steps[1]["type"] == "attachment"
    assert steps[1]["attachment"]["entity"] == "test_result"
    assert steps[1]["attachment"]["name"] == "evidence.txt"
    assert result.result_ids == [92]


@pytest.mark.asyncio
async def test_submit_manual_test_results_rejects_attachment_step_without_metadata(service: LaunchService) -> None:
    service._client.create_test_result.return_value = TestResultDto(id=999, name="Manual login test")
    with pytest.raises(AllureValidationError, match="attachment is required"):
        await service.submit_manual_test_results(
            44,
            results=[
                {
                    "launch_id": 12,
                    "test_case_id": 91,
                    "name": "Manual login test",
                    "status": "failed",
                    "steps": [
                        {
                            "type": "attachment",
                            "status": "failed",
                        }
                    ],
                }
            ],
        )


@pytest.mark.asyncio
async def test_add_test_result_attachment_prepares_base64_file(service: LaunchService, mock_client: MagicMock) -> None:
    mock_client.create_test_result_attachments.return_value = [
        TestResultAttachmentRowDto.model_construct(entity="test_result", id=1001, name="evidence.txt")
    ]

    result = await service.add_test_result_attachment(
        test_result_id=77,
        attachment={
            "name": "evidence.txt",
            "content_type": "text/plain",
            "content": "QQ==",
        },
    )

    assert result.file_names == ["evidence.txt"]
    assert result.status_code == 200
    mock_client.create_test_result_attachments.assert_awaited_once_with(77, [("evidence.txt", b"A")])


@pytest.mark.asyncio
async def test_add_test_result_attachment_maps_missing_test_result(
    service: LaunchService, mock_client: MagicMock
) -> None:
    mock_client.create_test_result_attachments.side_effect = AllureNotFoundError(
        "missing",
        status_code=404,
        response_body="{}",
    )

    with pytest.raises(AllureNotFoundError, match="Test result ID 77 not found"):
        await service.add_test_result_attachment(
            test_result_id=77,
            attachment={
                "name": "evidence.txt",
                "content_type": "text/plain",
                "content": "QQ==",
            },
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("attachment", "message"),
    [
        (
            {
                "name": "evidence.txt",
                "content_type": "text/plain",
                "content": "QQ==",
                "url": "https://example.com/evidence.txt",
            },
            "Cannot specify both 'content' and 'url'",
        ),
        (
            {
                "name": "evidence.bin",
                "content_type": "application/octet-stream",
                "content": "QQ==",
            },
            "is not allowed or supported",
        ),
    ],
)
async def test_add_test_result_attachment_validation_paths(
    service: LaunchService,
    attachment: dict[str, str],
    message: str,
) -> None:
    with pytest.raises(AllureValidationError, match=message):
        await service.add_test_result_attachment(test_result_id=77, attachment=attachment)


@pytest.mark.asyncio
async def test_add_test_step_attachment_resolves_manual_attachment_step_by_name(
    service: LaunchService, mock_client: MagicMock
) -> None:
    mock_client.get_test_result.return_value = TestResultDto(
        id=55,
        name="Manual Result",
        full_name="Manual Result",
        test_case_id=501,
    )
    mock_client.get_test_result_execution_raw.return_value = {
        "steps": [
            {
                "name": "manual-step.txt",
                "status": "failed",
            }
        ]
    }
    mock_client.create_test_result_attachments.return_value = [
        TestResultAttachmentRowDto.model_construct(entity="test_result", id=701, name="manual-step.txt")
    ]

    result = await service.add_test_step_attachment(
        test_result_id=55,
        step_name="manual-step.txt",
        attachment={
            "name": "manual-step.txt",
            "content_type": "text/plain",
            "content": "QQ==",
        },
    )

    assert result.target_id == 701
    mock_client.create_test_result_attachments.assert_awaited_once_with(55, [("manual-step.txt", b"A")])
    mock_client.patch_test_result.assert_awaited_once()
    mock_client.add_test_fixture_attachment.assert_not_awaited()


@pytest.mark.asyncio
async def test_add_test_step_attachment_requires_unambiguous_manual_step_selection(
    service: LaunchService, mock_client: MagicMock
) -> None:
    mock_client.get_test_result.return_value = TestResultDto(
        id=55,
        name="Manual Result",
        full_name="Manual Result",
    )
    mock_client.get_test_result_execution_raw.return_value = {
        "steps": [
            {"name": "manual-step.txt"},
            {"name": "manual-step-2.txt"},
        ]
    }

    with pytest.raises(AllureValidationError, match="Attachment step selection is ambiguous"):
        await service.add_test_step_attachment(
            test_result_id=55,
            attachment={
                "name": "evidence.txt",
                "content_type": "text/plain",
                "content": "QQ==",
            },
        )


@pytest.mark.asyncio
async def test_add_test_step_attachment_uses_test_case_scenario_when_runtime_names_are_missing(
    service: LaunchService, mock_client: MagicMock
) -> None:
    mock_client.get_test_result.return_value = TestResultDto(
        id=55,
        name="Manual Result",
        full_name="Manual Result",
        test_case_id=901,
    )
    mock_client.get_test_result_execution_raw.return_value = {"steps": [{"status": "failed"}]}
    mock_client.get_test_case_scenario.return_value = TestCaseScenarioV2Dto(steps=[_scenario_body_step("Open app")])
    mock_client.create_test_result_attachments.return_value = [
        TestResultAttachmentRowDto.model_construct(entity="test_result", id=702, name="evidence.txt")
    ]

    result = await service.add_test_step_attachment(
        test_result_id=55,
        step_name="Open app",
        attachment={
            "name": "evidence.txt",
            "content_type": "text/plain",
            "content": "QQ==",
        },
    )

    assert result.target_id == 702


@pytest.mark.asyncio
async def test_add_test_step_attachment_maps_missing_manual_test_result(
    service: LaunchService, mock_client: MagicMock
) -> None:
    mock_client.get_test_result.side_effect = AllureNotFoundError(
        "missing",
        status_code=404,
        response_body="{}",
    )

    with pytest.raises(AllureNotFoundError, match="Test result ID 55 not found"):
        await service.add_test_step_attachment(
            test_result_id=55,
            attachment={
                "name": "evidence.txt",
                "content_type": "text/plain",
                "content": "QQ==",
            },
        )


@pytest.mark.asyncio
async def test_add_test_step_attachment_maps_missing_attachment_slot(
    service: LaunchService, mock_client: MagicMock
) -> None:
    mock_client.get_test_result.return_value = TestResultDto(id=55, name="Manual Result", full_name="Manual Result")
    mock_client.get_test_result_execution_raw.return_value = {"steps": [{"name": "manual-step.txt"}]}

    with pytest.raises(AllureValidationError, match="step_index 1 is out of range"):
        await service.add_test_step_attachment(
            test_result_id=55,
            step_index=1,
            attachment={
                "name": "manual-step.txt",
                "content_type": "text/plain",
                "content": "QQ==",
            },
        )


@pytest.mark.asyncio
async def test_add_test_step_attachment_rejects_mixed_manual_and_fixture_selectors(service: LaunchService) -> None:
    with pytest.raises(AllureValidationError, match="Specify either manual step selectors"):
        await service.add_test_step_attachment(
            test_result_id=55,
            step_index=0,
            fixture_result_id=501,
            attachment={
                "name": "evidence.txt",
                "content_type": "text/plain",
                "content": "QQ==",
            },
        )


@pytest.mark.asyncio
async def test_add_test_step_attachment_resolves_fixture_fallback_by_name(
    service: LaunchService, mock_client: MagicMock
) -> None:
    mock_client.get_test_result_fixtures.return_value = [
        TestFixtureResultV2Dto(id=501, name="After screenshot", type="after")
    ]
    mock_client.add_test_fixture_attachment.return_value = 202

    result = await service.add_test_step_attachment(
        test_result_id=55,
        fixture_name="After screenshot",
        fixture_type="after",
        attachment={
            "name": "evidence.txt",
            "content_type": "text/plain",
            "content": "QQ==",
        },
    )

    assert result.target_id == 501
    mock_client.add_test_fixture_attachment.assert_awaited_once_with(501, [("evidence.txt", b"A")])


@pytest.mark.asyncio
async def test_add_test_step_attachment_rejects_invalid_fixture_type(service: LaunchService) -> None:
    with pytest.raises(AllureValidationError, match="fixture_type must be 'before' or 'after'"):
        await service.add_test_step_attachment(
            test_result_id=55,
            fixture_name="After screenshot",
            fixture_type="during",
            attachment={
                "name": "evidence.txt",
                "content_type": "text/plain",
                "content": "QQ==",
            },
        )


@pytest.mark.asyncio
async def test_build_manual_step_attachment_patch_scenario_merges_runtime_steps_with_test_case_template(
    service: LaunchService,
    mock_client: MagicMock,
) -> None:
    test_result = TestResultDto(
        id=55,
        name="Manual Result",
        full_name="Manual Result",
        test_case_id=901,
    )
    mock_client.get_test_result_execution_raw.return_value = {
        "steps": [
            {
                "status": "failed",
                "attachments": [{"id": 701, "name": "existing-evidence.txt"}],
                "steps": [{"body": "Nested runtime step", "status": "passed"}],
            }
        ]
    }
    mock_client.get_test_case_scenario.return_value = TestCaseScenarioV2Dto(steps=[_scenario_body_step("Open app")])

    scenario = await service._build_manual_step_attachment_patch_scenario(
        test_result=test_result,
        attachment_row=TestResultAttachmentRowDto.model_construct(
            entity="test_result",
            id=702,
            name="new-evidence.txt",
        ),
        attachment_id=701,
        step_name=None,
        step_index=None,
    )

    assert scenario.steps is not None
    assert len(scenario.steps) == 1
    top_step = scenario.steps[0]
    assert top_step.name == "Open app"
    assert top_step.status == "failed"
    assert top_step.attachments is not None
    assert [attachment.actual_instance.id for attachment in top_step.attachments] == [701, 702]
    assert top_step.steps is not None
    assert top_step.steps[0].name == "Nested runtime step"


@pytest.mark.asyncio
async def test_build_patchable_manual_result_steps_returns_template_when_runtime_steps_are_empty(
    service: LaunchService,
    mock_client: MagicMock,
) -> None:
    mock_client.get_test_result_execution_raw.return_value = {"steps": []}
    mock_client.get_test_case_scenario.return_value = TestCaseScenarioV2Dto(
        steps=[_scenario_body_step("Only template")]
    )

    steps = await service._build_patchable_manual_result_steps(TestResultDto(id=55, test_case_id=901))

    assert len(steps) == 1
    assert steps[0].name == "Only template"


def test_select_manual_patch_step_supports_attachment_id_name_index_and_default(service: LaunchService) -> None:
    first_attachment = TestResultAttachmentRowDto.model_construct(entity="test_result", id=701, name="First evidence")
    second_attachment = TestResultAttachmentRowDto.model_construct(entity="test_result", id=702, name="Second evidence")
    first_step = TestResultScenarioStepDto.model_construct(
        name="Capture first evidence",
        attachments=[TestResultAttachmentStepDtoAllOfAttachment.model_construct(actual_instance=first_attachment)],
    )
    second_step = TestResultScenarioStepDto.model_construct(
        name="Capture second evidence",
        attachments=[TestResultAttachmentStepDtoAllOfAttachment.model_construct(actual_instance=second_attachment)],
    )

    assert (
        service._select_manual_patch_step(
            [first_step, second_step],
            test_result_id=55,
            attachment_id=701,
            step_name=None,
            step_index=None,
        )
        is first_step
    )
    assert (
        service._select_manual_patch_step(
            [first_step, second_step],
            test_result_id=55,
            attachment_id=None,
            step_name="Capture second evidence",
            step_index=None,
        )
        is second_step
    )
    assert (
        service._select_manual_patch_step(
            [first_step, second_step],
            test_result_id=55,
            attachment_id=None,
            step_name=None,
            step_index=0,
        )
        is first_step
    )
    assert (
        service._select_manual_patch_step(
            [first_step],
            test_result_id=55,
            attachment_id=None,
            step_name=None,
            step_index=None,
        )
        is first_step
    )


def test_select_manual_patch_step_validation_errors(service: LaunchService) -> None:
    first_attachment = TestResultAttachmentRowDto.model_construct(entity="test_result", id=701, name="Shared evidence")
    duplicate_attachment = TestResultAttachmentRowDto.model_construct(
        entity="test_result", id=701, name="Shared evidence"
    )
    shared_name_step = TestResultScenarioStepDto.model_construct(
        name="Shared name",
        attachments=[TestResultAttachmentStepDtoAllOfAttachment.model_construct(actual_instance=first_attachment)],
    )
    duplicate_id_step = TestResultScenarioStepDto.model_construct(
        name="Other step",
        attachments=[TestResultAttachmentStepDtoAllOfAttachment.model_construct(actual_instance=duplicate_attachment)],
    )
    duplicate_name_step = TestResultScenarioStepDto.model_construct(
        name="Shared name",
        attachments=[TestResultAttachmentStepDtoAllOfAttachment.model_construct(actual_instance=duplicate_attachment)],
    )

    with pytest.raises(AllureNotFoundError, match="Attachment step ID 999 not found"):
        service._select_manual_patch_step(
            [shared_name_step],
            test_result_id=55,
            attachment_id=999,
            step_name=None,
            step_index=None,
        )

    with pytest.raises(
        AllureValidationError, match=r"Attachment step selection is ambiguous\. Provide step_name or step_index\."
    ):
        service._select_manual_patch_step(
            [shared_name_step, duplicate_id_step],
            test_result_id=55,
            attachment_id=701,
            step_name=None,
            step_index=None,
        )

    with pytest.raises(AllureValidationError, match="step_index must be a non-negative integer"):
        service._select_manual_patch_step(
            [shared_name_step],
            test_result_id=55,
            attachment_id=None,
            step_name=None,
            step_index=-1,
        )

    with pytest.raises(AllureNotFoundError, match="No step named 'Missing' found"):
        service._select_manual_patch_step(
            [shared_name_step],
            test_result_id=55,
            attachment_id=None,
            step_name="Missing",
            step_index=None,
        )

    with pytest.raises(AllureValidationError, match=r"Provide attachment_id or step_index\."):
        service._select_manual_patch_step(
            [shared_name_step, duplicate_name_step],
            test_result_id=55,
            attachment_id=None,
            step_name="Shared name",
            step_index=None,
        )

    with pytest.raises(AllureNotFoundError, match="has no manual scenario steps"):
        service._select_manual_patch_step(
            [],
            test_result_id=55,
            attachment_id=None,
            step_name=None,
            step_index=None,
        )


@pytest.mark.asyncio
async def test_resolve_manual_step_attachment_target_supports_all_selectors(
    service: LaunchService,
    mock_client: MagicMock,
) -> None:
    mock_client.get_test_result_execution.return_value = _manual_execution_with_steps(
        _attachment_step(701, "First evidence"),
        _attachment_step(702, "Second evidence"),
    )

    by_id = await service._resolve_manual_step_attachment_target(
        test_result_id=55,
        attachment_id=702,
        step_name=None,
        step_index=None,
    )
    by_index = await service._resolve_manual_step_attachment_target(
        test_result_id=55,
        attachment_id=None,
        step_name=None,
        step_index=0,
    )
    by_name = await service._resolve_manual_step_attachment_target(
        test_result_id=55,
        attachment_id=None,
        step_name="Second evidence",
        step_index=None,
    )

    assert by_id.attachment_id == 702
    assert by_id.step_index == 1
    assert by_id.name == "Second evidence"
    assert by_index.attachment_id == 701
    assert by_index.step_index == 0
    assert by_name.attachment_id == 702


@pytest.mark.asyncio
async def test_resolve_manual_step_attachment_target_without_selector_requires_single_attachment_step(
    service: LaunchService,
    mock_client: MagicMock,
) -> None:
    mock_client.get_test_result_execution.return_value = _manual_execution_with_steps(
        _attachment_step(701, "Only evidence")
    )

    target = await service._resolve_manual_step_attachment_target(
        test_result_id=55,
        attachment_id=None,
        step_name=None,
        step_index=None,
    )

    assert target.attachment_id == 701
    assert target.step_index == 0
    assert target.name == "Only evidence"


@pytest.mark.asyncio
async def test_resolve_manual_step_attachment_target_validation_errors(
    service: LaunchService,
    mock_client: MagicMock,
) -> None:
    mock_client.get_test_result_execution.return_value = _manual_execution_with_steps(
        _body_step("Not an attachment step"),
        _attachment_step(701, "Shared evidence"),
        _attachment_step(702, "Shared evidence"),
    )

    with pytest.raises(AllureNotFoundError, match="Attachment step ID 999 not found"):
        await service._resolve_manual_step_attachment_target(
            test_result_id=55,
            attachment_id=999,
            step_name=None,
            step_index=None,
        )

    with pytest.raises(AllureValidationError, match="step_index must be a non-negative integer"):
        await service._resolve_manual_step_attachment_target(
            test_result_id=55,
            attachment_id=None,
            step_name=None,
            step_index=-1,
        )

    with pytest.raises(AllureValidationError, match="step_index 10 is out of range"):
        await service._resolve_manual_step_attachment_target(
            test_result_id=55,
            attachment_id=None,
            step_name=None,
            step_index=10,
        )

    with pytest.raises(AllureValidationError, match="Step at index 0 is not an attachment step"):
        await service._resolve_manual_step_attachment_target(
            test_result_id=55,
            attachment_id=None,
            step_name=None,
            step_index=0,
        )

    with pytest.raises(AllureNotFoundError, match="No attachment step named 'Missing' found"):
        await service._resolve_manual_step_attachment_target(
            test_result_id=55,
            attachment_id=None,
            step_name="Missing",
            step_index=None,
        )

    with pytest.raises(AllureValidationError, match=r"Provide attachment_id or step_index\."):
        await service._resolve_manual_step_attachment_target(
            test_result_id=55,
            attachment_id=None,
            step_name="Shared evidence",
            step_index=None,
        )

    with pytest.raises(AllureValidationError, match=r"Provide attachment_id, step_name, or step_index\."):
        await service._resolve_manual_step_attachment_target(
            test_result_id=55,
            attachment_id=None,
            step_name=None,
            step_index=None,
        )


@pytest.mark.asyncio
async def test_resolve_manual_step_attachment_target_without_attachment_steps_raises_not_found(
    service: LaunchService,
    mock_client: MagicMock,
) -> None:
    mock_client.get_test_result_execution.return_value = _manual_execution_with_steps(_body_step("Only body step"))

    with pytest.raises(AllureNotFoundError, match="has no attachment steps"):
        await service._resolve_manual_step_attachment_target(
            test_result_id=55,
            attachment_id=None,
            step_name=None,
            step_index=None,
        )


def test_manual_step_attachment_target_from_step_ignores_non_attachment_or_missing_ids() -> None:
    assert LaunchService._manual_step_attachment_target_from_step(_body_step("Only body step"), step_index=0) is None

    unresolved_attachment = TestResultScenarioV2DtoStepsInner.model_construct(
        actual_instance=TestResultAttachmentStepDto.model_construct(
            type="TestResultAttachmentStepDto",
            attachment_id=0,
        )
    )
    assert LaunchService._manual_step_attachment_target_from_step(unresolved_attachment, step_index=1) is None


@pytest.mark.asyncio
async def test_test_result_lookup_wrappers_map_not_found_errors(
    service: LaunchService,
    mock_client: MagicMock,
) -> None:
    not_found = AllureNotFoundError("missing", status_code=404, response_body="{}")
    mock_client.get_test_result.side_effect = not_found
    mock_client.get_test_result_execution.side_effect = not_found
    mock_client.get_test_result_execution_raw.side_effect = not_found
    mock_client.get_test_case_scenario.side_effect = not_found

    with pytest.raises(AllureNotFoundError, match="Test result ID 55 not found"):
        await service._get_test_result_or_raise(55)

    with pytest.raises(AllureNotFoundError, match="Test result ID 55 not found"):
        await service._get_test_result_execution_or_raise(55)

    with pytest.raises(AllureNotFoundError, match="Test result ID 55 not found"):
        await service._get_test_result_execution_raw_or_raise(55, v2=True)

    with pytest.raises(AllureNotFoundError, match="Test case ID 901 not found"):
        await service._get_test_case_scenario_or_raise(901)


def test_attachment_helper_validation_edges(service: LaunchService) -> None:
    with pytest.raises(AllureValidationError, match="attachment must be a dictionary"):
        service._normalize_attachment_metadata("bad")  # type: ignore[arg-type]

    with pytest.raises(AllureValidationError, match=r"attachment\.content_type is required"):
        service._normalize_attachment_metadata({"name": "evidence.txt"})

    with pytest.raises(AllureValidationError, match=r"attachment\.url is required"):
        service._validate_attachment_url(None)

    with pytest.raises(AllureValidationError, match="Attachment URL must use http or https"):
        service._validate_attachment_url("ftp://example.com/evidence.txt")

    with pytest.raises(AllureValidationError, match="Attachment URL must include a hostname"):
        service._validate_attachment_url("https:///evidence.txt")

    with pytest.raises(AllureValidationError, match="must not target localhost or local network hostnames"):
        service._validate_attachment_url("https://localhost/evidence.txt")

    assert service._validate_attachment_url("https://8.8.8.8/evidence.txt") == "https://8.8.8.8/evidence.txt"
    service._validate_attachment_download_response(
        _StreamingResponse(url="https://example.com/evidence.txt", headers={"Content-Length": "oops"})
    )


@pytest.mark.asyncio
async def test_downloaded_attachment_content_rejects_stream_overflow(
    service: LaunchService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("src.services.launch_service.MAX_ATTACHMENT_SIZE", 4)

    with pytest.raises(AllureValidationError, match="Attachment size exceeds limit"):
        await service._read_downloaded_attachment_content(
            _StreamingResponse(url="https://example.com/evidence.txt", chunks=[b"abc", b"de"])
        )


@pytest.mark.asyncio
async def test_prepare_attachment_file_requires_name(service: LaunchService) -> None:
    with pytest.raises(AllureValidationError, match=r"attachment\.name is required"):
        await service._prepare_attachment_file(
            {
                "content_type": "text/plain",
                "content": "QQ==",
            }
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("attachment", "message"),
    [
        (
            {
                "content_type": "text/plain",
                "content": "not-base64**",
            },
            "Invalid base64 content",
        ),
        (
            {
                "name": "evidence.txt",
                "content_type": "text/plain",
            },
            "Attachment must have either 'content' or 'url'",
        ),
    ],
)
async def test_retrieve_attachment_content_validation_paths(
    service: LaunchService,
    attachment: dict[str, str],
    message: str,
) -> None:
    with pytest.raises(AllureValidationError, match=message):
        await service._retrieve_attachment_content(attachment)


class _AsyncClientSuccess:
    def __init__(self, *_args: object, **_kwargs: object) -> None:
        pass

    async def __aenter__(self) -> "_AsyncClientSuccess":
        return self

    async def __aexit__(self, *_args: object) -> None:
        return None

    def stream(self, method: str, url: str, *, follow_redirects: bool, timeout: float) -> "_AsyncStreamContext":
        assert method == "GET"
        assert follow_redirects is False
        assert timeout == 10.0
        return _AsyncStreamContext(_StreamingResponse(url=url, chunks=[b"evidence"]))


class _AsyncClientHTTPError:
    def __init__(self, *_args: object, **_kwargs: object) -> None:
        pass

    async def __aenter__(self) -> "_AsyncClientHTTPError":
        return self

    async def __aexit__(self, *_args: object) -> None:
        return None

    def stream(self, method: str, url: str, *, follow_redirects: bool, timeout: float) -> "_AsyncStreamContext":
        assert method == "GET"
        assert follow_redirects is False
        assert timeout == 10.0
        return _AsyncStreamContext(_StreamingResponse(url=url, status_code=502))


class _AsyncStreamContext:
    def __init__(self, response: "_StreamingResponse") -> None:
        self._response = response

    async def __aenter__(self) -> "_StreamingResponse":
        return self._response

    async def __aexit__(self, *_args: object) -> None:
        return None


class _StreamingResponse:
    def __init__(
        self,
        *,
        url: str,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        chunks: list[bytes] | None = None,
    ) -> None:
        self.request = httpx.Request("GET", url)
        self.status_code = status_code
        self.headers = headers or {}
        self._chunks = chunks or []

    @property
    def is_redirect(self) -> bool:
        return 300 <= self.status_code < 400

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            response = httpx.Response(self.status_code, request=self.request)
            raise httpx.HTTPStatusError("http error", request=self.request, response=response)

    async def aiter_bytes(self):
        for chunk in self._chunks:
            yield chunk


@pytest.mark.asyncio
async def test_retrieve_attachment_content_downloads_from_url(
    service: LaunchService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("src.services.launch_service.httpx.AsyncClient", _AsyncClientSuccess)

    content = await service._retrieve_attachment_content({"url": "https://example.com/evidence.txt"})

    assert content == b"evidence"


@pytest.mark.asyncio
async def test_retrieve_attachment_content_maps_http_status_errors(
    service: LaunchService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("src.services.launch_service.httpx.AsyncClient", _AsyncClientHTTPError)

    with pytest.raises(AllureValidationError, match="HTTP 502"):
        await service._retrieve_attachment_content({"url": "https://example.com/evidence.txt"})


@pytest.mark.asyncio
async def test_retrieve_attachment_content_rejects_private_ip_targets(service: LaunchService) -> None:
    with pytest.raises(AllureValidationError, match="private, loopback, or reserved IP ranges"):
        await service._retrieve_attachment_content({"url": "http://127.0.0.1/evidence.txt"})


@pytest.mark.asyncio
async def test_retrieve_attachment_content_rejects_redirects(
    service: LaunchService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _AsyncClientRedirect:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            pass

        async def __aenter__(self) -> "_AsyncClientRedirect":
            return self

        async def __aexit__(self, *_args: object) -> None:
            return None

        def stream(self, method: str, url: str, *, follow_redirects: bool, timeout: float) -> _AsyncStreamContext:
            assert method == "GET"
            assert follow_redirects is False
            assert timeout == 10.0
            return _AsyncStreamContext(
                _StreamingResponse(
                    url=url,
                    status_code=302,
                    headers={"Location": "https://redirected.example.com/file.txt"},
                )
            )

    monkeypatch.setattr("src.services.launch_service.httpx.AsyncClient", _AsyncClientRedirect)

    with pytest.raises(AllureValidationError, match="redirects are not allowed"):
        await service._retrieve_attachment_content({"url": "https://example.com/evidence.txt"})


@pytest.mark.asyncio
async def test_retrieve_attachment_content_rejects_oversized_remote_payload_by_header(
    service: LaunchService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _AsyncClientOversized:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            pass

        async def __aenter__(self) -> "_AsyncClientOversized":
            return self

        async def __aexit__(self, *_args: object) -> None:
            return None

        def stream(self, method: str, url: str, *, follow_redirects: bool, timeout: float) -> _AsyncStreamContext:
            assert method == "GET"
            assert follow_redirects is False
            assert timeout == 10.0
            return _AsyncStreamContext(
                _StreamingResponse(
                    url=url,
                    headers={"Content-Length": str(10 * 1024 * 1024 + 1)},
                    chunks=[b"ignored"],
                )
            )

    monkeypatch.setattr("src.services.launch_service.httpx.AsyncClient", _AsyncClientOversized)

    with pytest.raises(AllureValidationError, match="exceeds limit"):
        await service._retrieve_attachment_content({"url": "https://example.com/evidence.txt"})
