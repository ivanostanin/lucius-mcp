"""Unit tests for LaunchService."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from src.client import AllureClient, LaunchUploadResponseDto
from src.client.exceptions import AllureAPIError, AllureNotFoundError, AllureValidationError, LaunchNotFoundError
from src.client.generated.models.aql_validate_response_dto import AqlValidateResponseDto
from src.client.generated.models.find_all29200_response import FindAll29200Response
from src.client.generated.models.launch_dto import LaunchDto
from src.client.generated.models.launch_preview_dto import LaunchPreviewDto
from src.client.generated.models.page_launch_dto import PageLaunchDto
from src.client.generated.models.page_launch_preview_dto import PageLaunchPreviewDto
from src.client.generated.models.page_test_result_flat_dto import PageTestResultFlatDto
from src.client.generated.models.test_fixture_result_v2_dto import TestFixtureResultV2Dto
from src.client.generated.models.test_result_attachment_row_dto import TestResultAttachmentRowDto
from src.client.generated.models.test_result_attachment_step_dto import TestResultAttachmentStepDto
from src.client.generated.models.test_result_attachment_step_dto_all_of_attachment import (
    TestResultAttachmentStepDtoAllOfAttachment,
)
from src.client.generated.models.test_result_body_step_dto import TestResultBodyStepDto
from src.client.generated.models.test_result_dto import TestResultDto
from src.client.generated.models.test_result_flat_dto import TestResultFlatDto
from src.client.generated.models.test_result_scenario_v2_dto import TestResultScenarioV2Dto
from src.client.generated.models.test_result_scenario_v2_dto_steps_inner import TestResultScenarioV2DtoStepsInner
from src.client.generated.models.test_session_response_dto import TestSessionResponseDto
from src.client.generated.models.upload_results_response_dto import UploadResultsResponseDto
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
    client.get_test_result = AsyncMock()
    client.get_test_result_execution = AsyncMock(return_value=TestResultScenarioV2Dto(steps=[]))
    client.add_test_result_attachment = AsyncMock()
    client.add_test_fixture_attachment = AsyncMock()
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
    launch = LaunchDto(id=88, name="To Delete")
    mock_client.get_launch.return_value = launch

    result = await service.delete_launch(88)

    assert isinstance(result, LaunchDeleteResult)
    assert result.launch_id == 88
    assert result.status == "archived"
    assert result.name == "To Delete"
    mock_client.delete_launch.assert_called_once_with(88)


@pytest.mark.asyncio
async def test_delete_launch_invalid_id(service: LaunchService) -> None:
    with pytest.raises(AllureValidationError, match="Launch ID must be a positive integer"):
        await service.delete_launch(0)


@pytest.mark.asyncio
async def test_delete_launch_already_deleted(service: LaunchService, mock_client: MagicMock) -> None:
    mock_client.get_launch.side_effect = AllureNotFoundError("Not found", status_code=404, response_body="{}")

    result = await service.delete_launch(99)

    assert result.launch_id == 99
    assert result.status == "already_deleted"
    assert "already archived" in result.message
    mock_client.delete_launch.assert_not_called()


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
    mock_client.submit_manual_test_results.return_value = UploadResultsResponseDto(result_ids=[301])

    result = await service.submit_manual_test_results(
        44,
        results=[
            {
                "test_case_id": 91,
                "name": "Manual login test",
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

    assert result.result_ids == [301]
    payload = mock_client.submit_manual_test_results.await_args.args[0]
    assert payload.test_session_id == 44
    assert payload.results[0].test_case_id == "91"
    assert payload.results[0].name == "Manual login test"
    assert payload.results[0].full_name == "Manual login test"
    assert isinstance(payload.results[0].uuid, str)
    assert isinstance(payload.results[0].history_id, str)
    assert payload.results[0].steps is not None
    assert len(payload.results[0].steps) == 1


@pytest.mark.asyncio
async def test_submit_manual_test_results_rejects_payload_without_name_or_full_name(service: LaunchService) -> None:
    with pytest.raises(AllureValidationError, match=r"results\[0\]\.name is required"):
        await service.submit_manual_test_results(
            44,
            results=[
                {
                    "test_case_id": 91,
                    "status": "passed",
                }
            ],
        )


@pytest.mark.asyncio
async def test_submit_manual_test_results_maps_expected_attachment_steps_and_parameters(
    service: LaunchService, mock_client: MagicMock
) -> None:
    mock_client.submit_manual_test_results.return_value = UploadResultsResponseDto(result_ids=[401])

    result = await service.submit_manual_test_results(
        45,
        results=[
            {
                "test_case_id": 92,
                "name": "Manual upload with evidence",
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

    payload = mock_client.submit_manual_test_results.await_args.args[0]
    steps = payload.results[0].steps
    assert steps is not None
    assert len(steps) == 2
    assert steps[0].actual_instance.type == "UploadTestResultExpectedBodyStepDto"
    assert steps[1].actual_instance.type == "UploadTestResultAttachmentStepDto"
    assert steps[1].actual_instance.attachment.name == "evidence.txt"
    assert payload.results[0].parameters is not None
    assert payload.results[0].parameters[0].name == "browser"
    assert result.result_ids == [401]


@pytest.mark.asyncio
async def test_submit_manual_test_results_rejects_attachment_step_without_metadata(service: LaunchService) -> None:
    with pytest.raises(AllureValidationError, match="attachment is required"):
        await service.submit_manual_test_results(
            44,
            results=[
                {
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
    mock_client.add_test_result_attachment.return_value = 202

    result = await service.add_test_result_attachment(
        test_result_id=77,
        attachment={
            "name": "evidence.txt",
            "content_type": "text/plain",
            "content": "QQ==",
        },
    )

    assert result.file_names == ["evidence.txt"]
    assert result.status_code == 202
    mock_client.add_test_result_attachment.assert_awaited_once_with(77, [("evidence.txt", b"A")])


@pytest.mark.asyncio
async def test_add_test_result_attachment_maps_missing_test_result(
    service: LaunchService, mock_client: MagicMock
) -> None:
    mock_client.add_test_result_attachment.side_effect = AllureNotFoundError(
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
    mock_client.get_test_result_execution.return_value = _manual_execution_with_steps(
        _body_step("Open app"),
        _attachment_step(701, "manual-step.txt"),
    )

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
    mock_client.patch_test_result_attachment.assert_awaited_once()
    mock_client.update_test_result_attachment_content.assert_awaited_once_with(701, [("manual-step.txt", b"A")])
    mock_client.add_test_fixture_attachment.assert_not_awaited()


@pytest.mark.asyncio
async def test_add_test_step_attachment_requires_unambiguous_manual_step_selection(
    service: LaunchService, mock_client: MagicMock
) -> None:
    mock_client.get_test_result_execution.return_value = _manual_execution_with_steps(
        _attachment_step(701, "manual-step.txt"),
        _attachment_step(702, "manual-step-2.txt"),
    )

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
async def test_add_test_step_attachment_maps_missing_manual_test_result(
    service: LaunchService, mock_client: MagicMock
) -> None:
    mock_client.get_test_result_execution.side_effect = AllureNotFoundError(
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
    mock_client.get_test_result_execution.return_value = _manual_execution_with_steps(
        _attachment_step(701, "manual-step.txt")
    )
    mock_client.patch_test_result_attachment.side_effect = AllureNotFoundError(
        "missing",
        status_code=404,
        response_body="{}",
    )

    with pytest.raises(AllureNotFoundError, match="Step attachment ID 701 not found"):
        await service.add_test_step_attachment(
            test_result_id=55,
            step_index=0,
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
