"""Integration tests for launch client wiring."""

import time
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from pydantic import SecretStr

from src.client import AllureClient
from src.client.exceptions import AllureNotFoundError, AllureValidationError
from src.client.generated.exceptions import ApiException
from src.client.generated.models.aql_validate_response_dto import AqlValidateResponseDto
from src.client.generated.models.external_run_response_dto import ExternalRunResponseDto
from src.client.generated.models.external_run_start_request_dto import ExternalRunStartRequestDto
from src.client.generated.models.find_all29200_response import FindAll29200Response
from src.client.generated.models.job import Job
from src.client.generated.models.job_run import JobRun
from src.client.generated.models.launch import Launch
from src.client.generated.models.launch_create_dto import LaunchCreateDto
from src.client.generated.models.launch_dto import LaunchDto
from src.client.generated.models.launch_upload_response_dto import LaunchUploadResponseDto
from src.client.generated.models.manual_session_request_dto import ManualSessionRequestDto
from src.client.generated.models.page_launch_dto import PageLaunchDto
from src.client.generated.models.page_launch_preview_dto import PageLaunchPreviewDto
from src.client.generated.models.page_test_result_flat_dto import PageTestResultFlatDto
from src.client.generated.models.test_fixture_result_v2_dto import TestFixtureResultV2Dto
from src.client.generated.models.test_result_attachment_patch_dto import TestResultAttachmentPatchDto
from src.client.generated.models.test_result_attachment_row_dto import TestResultAttachmentRowDto
from src.client.generated.models.test_result_bulk_rerun_dto import TestResultBulkRerunDto
from src.client.generated.models.test_result_create_v2_dto import TestResultCreateV2Dto
from src.client.generated.models.test_result_dto import TestResultDto
from src.client.generated.models.test_result_patch_dto import TestResultPatchDto
from src.client.generated.models.test_result_rerun_dto import TestResultRerunDto
from src.client.generated.models.test_result_scenario_v2_dto import TestResultScenarioV2Dto
from src.client.generated.models.test_result_tree_selection_dto import TestResultTreeSelectionDto
from src.client.generated.models.test_session_response_dto import TestSessionResponseDto
from src.client.generated.models.upload_fixtures_results_dto import UploadFixturesResultsDto
from src.client.generated.models.upload_results_dto import UploadResultsDto
from src.client.generated.models.upload_test_fixture_result_dto import UploadTestFixtureResultDto
from src.client.generated.rest import RESTResponse


@pytest.mark.asyncio
async def test_client_create_launch_calls_api() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._launch_api = MagicMock()
    client._launch_api.create31 = AsyncMock(return_value=LaunchDto(id=1, name="Launch"))

    data = LaunchCreateDto(name="Launch", project_id=1)
    result = await client.create_launch(data)

    assert result.id == 1
    client._launch_api.create31.assert_called_once()


@pytest.mark.asyncio
async def test_client_list_launches_calls_api() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._launch_api = MagicMock()
    page = PageLaunchDto(content=[LaunchDto(id=1, name="Launch")])
    client._launch_api.find_all29 = AsyncMock(return_value=FindAll29200Response(page))

    result = await client.list_launches(project_id=1, page=0, size=20)

    assert result.actual_instance is not None
    client._launch_api.find_all29.assert_called_once()
    client._launch_api.find_all29_without_preload_content.assert_not_called()


@pytest.mark.asyncio
async def test_client_list_launches_falls_back_on_oneof() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._launch_api = MagicMock()
    client._launch_api.find_all29 = AsyncMock(side_effect=ValueError("oneOf conflict"))
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {
        "content": [{"id": 1, "name": "Launch"}],
        "number": 0,
        "size": 20,
        "totalElements": 1,
        "totalPages": 1,
    }
    client._launch_api.find_all29_without_preload_content = AsyncMock(return_value=response)

    result = await client.list_launches(project_id=1, page=0, size=20)

    assert result.actual_instance is not None
    assert isinstance(result.actual_instance, (PageLaunchDto, PageLaunchPreviewDto))
    client._launch_api.find_all29.assert_called_once()
    client._launch_api.find_all29_without_preload_content.assert_called_once()


@pytest.mark.asyncio
async def test_client_get_launch_calls_api() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._launch_api = MagicMock()
    client._launch_api.find_one23 = AsyncMock(return_value=LaunchDto(id=2, name="Launch"))

    result = await client.get_launch(launch_id=2)

    assert result.id == 2
    client._launch_api.find_one23.assert_called_once()


@pytest.mark.asyncio
async def test_client_get_launch_not_found_raises() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._launch_api = MagicMock()
    client._launch_api.find_one23 = AsyncMock(side_effect=ApiException(status=404, reason="Not Found", body="{}"))

    with pytest.raises(AllureNotFoundError, match="Resource not found"):
        await client.get_launch(launch_id=404)


@pytest.mark.asyncio
async def test_client_close_launch_calls_api() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._launch_api = MagicMock()
    response = MagicMock()
    response.status_code = 204
    client._launch_api.close_with_http_info = AsyncMock(return_value=response)

    status_code = await client.close_launch(launch_id=3)

    assert status_code == 204
    client._launch_api.close_with_http_info.assert_called_once_with(id=3, _request_timeout=client._timeout)


@pytest.mark.asyncio
async def test_client_close_launch_invalid_id_raises() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._launch_api = MagicMock()

    with pytest.raises(AllureValidationError, match="Launch ID must be a positive integer"):
        await client.close_launch(launch_id=0)


@pytest.mark.asyncio
async def test_client_reopen_launch_calls_api() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._launch_api = MagicMock()
    client._launch_api.reopen = AsyncMock(return_value=None)

    await client.reopen_launch(launch_id=4)

    client._launch_api.reopen.assert_called_once_with(id=4, _request_timeout=client._timeout)


@pytest.mark.asyncio
async def test_client_reopen_launch_invalid_id_raises() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._launch_api = MagicMock()

    with pytest.raises(AllureValidationError, match="Launch ID must be a positive integer"):
        await client.reopen_launch(launch_id=0)


@pytest.mark.asyncio
async def test_client_upload_results_to_launch_uses_multipart_endpoint() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600

    api_client = MagicMock()

    def _param_serialize_side_effect(*args, **kwargs):
        path = kwargs.get("resource_path")
        return ("POST", f"https://example.com{path}", {}, None, [])

    api_client.param_serialize.side_effect = _param_serialize_side_effect

    httpx_response = MagicMock()
    httpx_response.status_code = 202
    httpx_response.reason_phrase = "Accepted"
    httpx_response.text = '{"launchId": 9, "filesCount": 1}'
    httpx_response.json.return_value = {"launchId": 9, "filesCount": 1}

    rest_response = RESTResponse(httpx_response)
    client._api_client = api_client
    api_client.call_api = AsyncMock(return_value=rest_response)

    result = await client.upload_results_to_launch(launch_id=9, files=[("results.json", b"{}")])

    assert isinstance(result, LaunchUploadResponseDto)
    assert result.launch_id == 9
    assert result.files_count == 1

    _, kwargs = api_client.param_serialize.call_args
    assert kwargs["resource_path"] == "/api/launch/9/upload/file"
    assert kwargs["header_params"]["Content-Type"] == "multipart/form-data"
    assert kwargs["files"] == {
        "file": [("results.json", b"{}")],
        "info": ("info.json", b"{}"),
    }


@pytest.mark.asyncio
async def test_client_list_launch_test_results_calls_api() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._test_result_flat_api = MagicMock()
    client._test_result_flat_api.get_test_cases1 = AsyncMock(return_value=PageTestResultFlatDto(content=[]))

    result = await client.list_launch_test_results(launch_id=5, page=0, size=20)

    assert result.content == []
    client._test_result_flat_api.get_test_cases1.assert_called_once_with(
        launch_id=5,
        search=None,
        filter_id=None,
        page=0,
        size=20,
        sort=None,
        _request_timeout=client._timeout,
    )


@pytest.mark.asyncio
async def test_client_test_result_wrappers_call_apis() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._test_result_api = MagicMock()
    client._test_result_api.find_one5 = AsyncMock(return_value=TestResultDto(id=33, name="Manual Result"))
    client._test_result_api.create5 = AsyncMock(return_value=TestResultDto(id=34, name="Created Result"))
    client._test_result_api.patch5 = AsyncMock(return_value=TestResultDto(id=34, name="Patched Result"))
    client._test_result_api.find_execution = AsyncMock(return_value=TestResultScenarioV2Dto(steps=[]))
    client._test_result_api.find_execution_without_preload_content = AsyncMock(
        return_value=httpx.Response(200, json={"steps": [{"status": "failed", "message": "broken"}]})
    )
    client._test_result_fixture_api = MagicMock()
    client._test_result_fixture_api.get_fixtures = AsyncMock(return_value=[TestFixtureResultV2Dto(id=77, name="After")])

    result = await client.get_test_result(33)
    created = await client.create_test_result(
        TestResultCreateV2Dto(launch_id=9, name="Created Result", status="failed")
    )
    patched = await client.patch_test_result(34, TestResultPatchDto(name="Patched Result"))
    execution = await client.get_test_result_execution(33)
    execution_raw = await client.get_test_result_execution_raw(33)
    fixtures = await client.get_test_result_fixtures(33)

    assert result.id == 33
    assert created.id == 34
    assert patched.id == 34
    assert execution.steps == []
    assert execution_raw["steps"] == [{"status": "failed", "message": "broken"}]
    assert fixtures[0].id == 77


@pytest.mark.asyncio
async def test_client_manual_execution_wrappers_call_apis() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._test_result_bulk_api = MagicMock()
    client._test_result_bulk_api.rerun = AsyncMock(return_value=None)
    client._test_result_rerun_api = MagicMock()
    client._test_result_rerun_api.retry = AsyncMock(return_value=None)
    client._upload_api = MagicMock()
    client._upload_api.start = AsyncMock(return_value=ExternalRunResponseDto(job_id=7, job_run_id=8, project_id=1))
    client._upload_api.session_job_run = AsyncMock(return_value=TestSessionResponseDto(id=44))
    client._upload_test_result_api = MagicMock()
    client._upload_test_result_api.upload_test_results_without_preload_content = AsyncMock(
        return_value=httpx.Response(200, json={"results": [{"id": 1}, {"id": 2}]})
    )
    client._upload_test_result_api.upload_test_fixture_results_without_preload_content = AsyncMock(
        return_value=httpx.Response(200, json={"results": [{"id": 9}]})
    )

    rerun_payload = TestResultBulkRerunDto(
        selection=TestResultTreeSelectionDto(launch_id=9, leafs_include=[10]),
        force_manual=True,
    )
    external_run_payload = ExternalRunStartRequestDto(
        project_id=1,
        launch=Launch(id=9),
        job=Job(uid="job-1"),
        job_run=JobRun(uid="run-1"),
    )
    session_start_payload = ManualSessionRequestDto(launch_id=9, project_id=1, job_uid="job-1", job_run_uid="run-1")
    session_results_payload = UploadResultsDto(test_session_id=44)
    fixture_payload = UploadFixturesResultsDto(fixtures=[UploadTestFixtureResultDto(name="after", status="PASSED")])

    await client.rerun_test_results_bulk(rerun_payload)
    await client.rerun_test_result(10, TestResultRerunDto(username="alice"))
    external_run = await client.start_external_run(external_run_payload)
    session = await client.start_manual_test_session(session_start_payload)
    upload = await client.submit_manual_test_results(session_results_payload)
    fixtures = await client.upload_test_fixture_results(44, fixture_payload)

    assert external_run.job_id == 7
    assert session.id == 44
    assert upload.result_ids == [1, 2]
    assert fixtures.result_ids == [9]
    client._test_result_bulk_api.rerun.assert_called_once()
    client._test_result_rerun_api.retry.assert_called_once()
    client._upload_api.start.assert_called_once()
    client._upload_api.session_job_run.assert_called_once()
    client._upload_test_result_api.upload_test_results_without_preload_content.assert_called_once()
    client._upload_test_result_api.upload_test_fixture_results_without_preload_content.assert_called_once()


@pytest.mark.asyncio
async def test_client_test_result_attachment_wrappers_use_expected_paths() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600

    attachment_api = MagicMock()
    attachment_api.find_all5_without_preload_content = AsyncMock(
        return_value=httpx.Response(
            200,
            json={
                "content": [
                    {
                        "entity": None,
                        "id": 77,
                        "name": "manual-step.txt",
                        "contentType": "text/plain",
                    }
                ]
            },
        )
    )
    attachment_api.patch6 = AsyncMock(
        return_value=TestResultAttachmentRowDto.model_validate(
            {
                "entity": "TestResultAttachmentRowDto",
                "id": 77,
                "name": "manual-step.txt",
                "contentType": "text/plain",
            }
        )
    )
    attachment_api.read_content_without_preload_content = AsyncMock(return_value=httpx.Response(200, content=b"A"))
    client._test_result_attachment_api = attachment_api

    attachments = await client.list_test_result_attachments(9, sort=["name,ASC"])
    patched = await client.patch_test_result_attachment(
        77,
        TestResultAttachmentPatchDto(name="manual-step.txt", content_type="text/plain"),
    )
    content = await client.read_test_result_attachment_content(77)

    assert attachments.content is not None
    assert attachments.content[0].id == 77
    assert patched.id == 77
    assert content == b"A"
    attachment_api.find_all5_without_preload_content.assert_awaited_once_with(
        test_result_id=9,
        page=0,
        size=10,
        sort=["name,ASC"],
        _request_timeout=client._timeout,
    )
    attachment_api.patch6.assert_awaited_once()
    attachment_api.read_content_without_preload_content.assert_awaited_once_with(
        id=77,
        inline=False,
        _request_timeout=client._timeout,
    )


@pytest.mark.asyncio
async def test_client_create_test_result_attachments_calls_generated_api() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._test_result_attachment_api = MagicMock()
    client._test_result_attachment_api.create6 = AsyncMock(
        return_value=[
            TestResultAttachmentRowDto.model_validate(
                {
                    "entity": "test_result",
                    "id": 9,
                    "name": "manual-step.txt",
                    "contentType": "text/plain",
                }
            )
        ]
    )

    result = await client.create_test_result_attachments(9, [("manual-step.txt", b"A")])

    assert result[0].id == 9
    client._test_result_attachment_api.create6.assert_awaited_once_with(
        test_result_id=9,
        file=[("manual-step.txt", b"A")],
        _request_timeout=client._timeout,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method_name", "resource_path", "status_code"),
    [
        ("add_test_result_attachment", "/api/upload/test-result/9/attachment", 200),
        ("add_test_result_attachment", "/api/upload/test-result/9/attachment", 202),
        ("add_test_fixture_attachment", "/api/upload/test-fixture-result/9/attachment", 200),
        ("add_test_fixture_attachment", "/api/upload/test-fixture-result/9/attachment", 202),
    ],
)
async def test_client_manual_attachment_uploads_use_expected_paths(
    method_name: str,
    resource_path: str,
    status_code: int,
) -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600

    api_client = MagicMock()

    def _param_serialize_side_effect(*args, **kwargs):
        path = kwargs.get("resource_path")
        method = kwargs.get("method")
        return (method, f"https://example.com{path}", {}, None, [])

    api_client.param_serialize.side_effect = _param_serialize_side_effect

    httpx_response = MagicMock()
    httpx_response.status_code = status_code
    httpx_response.reason_phrase = "Accepted" if status_code == 202 else "OK"
    httpx_response.text = ""
    httpx_response.json.return_value = {}

    rest_response = RESTResponse(httpx_response)
    client._api_client = api_client
    api_client.call_api = AsyncMock(return_value=rest_response)

    result_status_code = await getattr(client, method_name)(9, [("evidence.txt", b"A")])

    assert result_status_code == status_code
    _, kwargs = api_client.param_serialize.call_args
    assert kwargs["resource_path"] == resource_path
    assert kwargs["files"] == {"file": [("evidence.txt", b"A")]}


@pytest.mark.asyncio
async def test_client_update_test_result_attachment_content_calls_generated_api() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._test_result_attachment_api = MagicMock()
    client._test_result_attachment_api.update_content = AsyncMock(
        return_value=TestResultAttachmentRowDto.model_validate(
            {
                "entity": "TestResultAttachmentRowDto",
                "id": 9,
                "name": "manual-step.txt",
                "contentType": "text/plain",
            }
        )
    )

    result = await client.update_test_result_attachment_content(9, [("manual-step.txt", b"A")])

    assert result == 200
    client._test_result_attachment_api.update_content.assert_awaited_once_with(
        id=9,
        file=("manual-step.txt", b"A"),
        _request_timeout=client._timeout,
    )


@pytest.mark.asyncio
async def test_client_search_launches_aql_calls_api() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._launch_search_api = MagicMock()
    client._launch_search_api.search2 = AsyncMock(return_value=PageLaunchDto(content=[]))

    result = await client.search_launches_aql(project_id=1, rql='name="Launch"')

    assert result.content == []
    client._launch_search_api.search2.assert_called_once()


@pytest.mark.asyncio
async def test_client_delete_launch_calls_api() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._launch_api = MagicMock()
    client._launch_api.delete27 = AsyncMock(return_value=None)

    await client.delete_launch(launch_id=12)

    client._launch_api.delete27.assert_called_once_with(id=12, _request_timeout=client._timeout)


@pytest.mark.asyncio
async def test_client_delete_launch_not_found_raises() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._launch_api = MagicMock()
    client._launch_api.delete27 = AsyncMock(side_effect=ApiException(status=404, reason="Not Found", body="{}"))

    with pytest.raises(AllureNotFoundError, match="Resource not found"):
        await client.delete_launch(launch_id=404)


@pytest.mark.asyncio
async def test_client_validate_launch_query_calls_api() -> None:
    client = AllureClient(base_url="https://example.com", token=SecretStr("token"), project=1)
    client._is_entered = True
    client._token_expires_at = time.time() + 3600
    client._launch_search_api = MagicMock()
    client._launch_search_api.validate_query2 = AsyncMock(return_value=AqlValidateResponseDto(valid=True, count=1))

    result = await client.validate_launch_query(project_id=1, rql='name="Launch"')

    assert result.valid is True
    client._launch_search_api.validate_query2.assert_called_once()
