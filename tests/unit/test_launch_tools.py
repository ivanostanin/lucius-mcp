# ruff: noqa: S105,S106,S107
"""Unit tests for launch tools formatting."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import SecretStr

from src.tools.launches import (
    add_test_result_attachment,
    close_launch,
    create_launch,
    delete_launch,
    get_launch,
    list_launch_test_results,
    list_launches,
    reopen_launch,
    start_manual_test_session,
    submit_manual_test_results,
)


def _resolved_auth(*, endpoint: str = "https://example.com", token: str = "token", project_id: int = 1) -> object:
    return SimpleNamespace(endpoint=endpoint, api_token=SecretStr(token), project_id=project_id)


def _mock_url_context(project_id: int = 1) -> MagicMock:
    mock_client = MagicMock()
    mock_client.get_base_url.return_value = "https://example.com"
    mock_client.get_project.return_value = project_id
    return mock_client


@pytest.mark.asyncio
async def test_create_launch_output_format() -> None:
    with patch("src.tools.launches.AllureClient.from_env") as mock_client_ctx:
        mock_client = _mock_url_context()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.launches.LaunchService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_launch = type("LaunchDto", (), {"id": 10, "name": "Launch"})
            mock_service.create_launch = AsyncMock(return_value=mock_launch)

            output = await create_launch(name="Launch", output_format="plain")

            assert "✅ Launch created successfully!" in output
            assert "ID: 10" in output
            assert "Name: Launch" in output


@pytest.mark.asyncio
async def test_list_launches_output_format() -> None:
    with patch("src.tools.launches.AllureClient.from_env") as mock_client_ctx:
        mock_client = _mock_url_context()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.launches.LaunchService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            result = type(
                "LaunchListResult",
                (),
                {
                    "items": [type("Launch", (), {"id": 1, "name": "L1", "created_date": 123, "closed": False})],
                    "total": 1,
                    "page": 0,
                    "size": 20,
                    "total_pages": 1,
                },
            )
            mock_service.list_launches = AsyncMock(return_value=result)

            output = await list_launches(page=0, size=20, output_format="plain")

            assert "Found 1 launches" in output
            assert "#1" in output
            assert "L1" in output


@pytest.mark.asyncio
async def test_list_launches_empty() -> None:
    with patch("src.tools.launches.AllureClient.from_env") as mock_client_ctx:
        mock_client = _mock_url_context()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.launches.LaunchService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            result = type(
                "LaunchListResult",
                (),
                {"items": [], "total": 0, "page": 0, "size": 20, "total_pages": 0},
            )
            mock_service.list_launches = AsyncMock(return_value=result)

            output = await list_launches(page=0, size=20, output_format="plain")

            assert "No launches found" in output


@pytest.mark.asyncio
async def test_get_launch_project_id_fallback_uses_zero_override() -> None:
    with patch(
        "src.tools.launches.resolve_auth_settings",
        return_value=_resolved_auth(token="runtime-token", project_id=0),
    ):
        with patch("src.tools.launches.AllureClient") as mock_client_cls:
            mock_client = _mock_url_context(project_id=0)
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            with patch("src.tools.launches.LaunchService") as mock_service_cls:
                mock_service = mock_service_cls.return_value
                mock_service.get_launch = AsyncMock(
                    return_value=type("LaunchDto", (), {"id": 10, "name": "Launch", "closed": False})
                )

                await get_launch(launch_id=10, project_id=0)

                assert mock_client_cls.call_args.kwargs["project"] == 0


@pytest.mark.asyncio
async def test_get_launch_output_format() -> None:
    with patch(
        "src.tools.launches.resolve_auth_settings",
        return_value=_resolved_auth(token="runtime-token"),
    ):
        with patch("src.tools.launches.AllureClient") as mock_client_cls:
            mock_client = _mock_url_context()
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            with patch("src.tools.launches.LaunchService") as mock_service_cls:
                mock_service = mock_service_cls.return_value
                mock_launch = type(
                    "LaunchDto",
                    (),
                    {
                        "id": 10,
                        "name": "Launch",
                        "closed": False,
                        "created_date": 123,
                        "last_modified_date": 456,
                        "known_defects_count": 2,
                        "new_defects_count": 1,
                        "statistic": [
                            type("Stat", (), {"status": "passed", "count": 7}),
                            type("Stat", (), {"status": "failed", "count": 1}),
                        ],
                    },
                )
                mock_service.get_launch = AsyncMock(return_value=mock_launch)

                output = await get_launch(launch_id=10, output_format="plain")

                assert "Launch details" in output
                assert "ID: 10" in output
                assert "Status: open" in output
                assert "Started: 123" in output
                assert "Ended: 456" in output
                assert "Known defects: 2" in output
                assert "New defects: 1" in output
                assert "Summary: passed=7, failed=1" in output


@pytest.mark.asyncio
async def test_list_launch_test_results_output_format() -> None:
    with patch("src.tools.launches.resolve_auth_settings", return_value=_resolved_auth()):
        with patch("src.tools.launches.AllureClient") as mock_client_cls:
            mock_client = _mock_url_context()
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            with patch("src.tools.launches.LaunchService") as mock_service_cls:
                mock_service = mock_service_cls.return_value
                mock_service.list_launch_test_results = AsyncMock(
                    return_value=type(
                        "LaunchTestResultListResult",
                        (),
                        {
                            "items": [
                                type(
                                    "LaunchTestResultListItem",
                                    (),
                                    {
                                        "result_id": 101,
                                        "test_case_id": 11,
                                        "name": "Manual Failed",
                                        "manual": True,
                                        "status": "failed",
                                        "assignee": "alice",
                                        "tested_by": "qa",
                                    },
                                )
                            ],
                            "total": 1,
                            "page": 0,
                            "size": 20,
                            "total_pages": 1,
                        },
                    )
                )

                output = await list_launch_test_results(
                    launch_id=10,
                    manual_only=True,
                    failed_only=True,
                    output_format="plain",
                )

                assert "Found 1 launch test results" in output
                assert "Result #101" in output
                assert "alice" in output


@pytest.mark.asyncio
async def test_start_manual_test_session_output_format() -> None:
    with patch("src.tools.launches.resolve_auth_settings", return_value=_resolved_auth()):
        with patch("src.tools.launches.AllureClient") as mock_client_cls:
            mock_client = _mock_url_context()
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            with patch("src.tools.launches.LaunchService") as mock_service_cls:
                mock_service = mock_service_cls.return_value
                mock_service.start_manual_test_session = AsyncMock(
                    return_value=type(
                        "ManualTestSessionResult",
                        (),
                        {
                            "test_session_id": 44,
                            "launch_id": 10,
                            "job_id": 7,
                            "job_run_id": 8,
                            "project_id": 1,
                            "environment": [{"key": "browser", "value": "chrome"}],
                        },
                    )
                )

                output = await start_manual_test_session(
                    launch_id=10,
                    environment=[{"key": "browser", "value": "chrome"}],
                    output_format="plain",
                )

                assert "Test session ID: 44" in output
                assert "browser=chrome" in output


@pytest.mark.asyncio
async def test_submit_manual_test_results_and_attachment_outputs() -> None:
    with patch("src.tools.launches.resolve_auth_settings", return_value=_resolved_auth()):
        with patch("src.tools.launches.AllureClient") as mock_client_cls:
            mock_client = _mock_url_context()
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            with patch("src.tools.launches.LaunchService") as mock_service_cls:
                mock_service = mock_service_cls.return_value
                mock_service.submit_manual_test_results = AsyncMock(
                    return_value=type(
                        "ManualTestSubmissionResult",
                        (),
                        {"test_session_id": 44, "result_ids": [101], "submitted_count": 1},
                    )
                )
                mock_service.add_test_result_attachment = AsyncMock(
                    return_value=type(
                        "AttachmentUploadResult",
                        (),
                        {
                            "target_kind": "test_result",
                            "target_id": 101,
                            "file_names": ["evidence.txt"],
                            "status_code": 202,
                        },
                    )
                )

                submit_output = await submit_manual_test_results(
                    test_session_id=44,
                    results=[{"result_id": 9, "status": "passed"}],
                    output_format="plain",
                )
                attachment_output = await add_test_result_attachment(
                    test_result_id=101,
                    attachment={"name": "evidence.txt", "content_type": "text/plain", "content": "QQ=="},
                    output_format="plain",
                )

                assert "Result IDs: 101" in submit_output
                assert "HTTP status: 202" in attachment_output


@pytest.mark.asyncio
async def test_delete_launch_output_deleted() -> None:
    with patch("src.tools.launches.resolve_auth_settings", return_value=_resolved_auth()):
        with patch("src.tools.launches.AllureClient") as mock_client_cls:
            mock_client = _mock_url_context()
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            with patch("src.tools.launches.LaunchService") as mock_service_cls:
                mock_service = mock_service_cls.return_value
                mock_result = type(
                    "LaunchDeleteResult",
                    (),
                    {"launch_id": 42, "status": "deleted", "message": "Deleted"},
                )
                mock_service.delete_launch = AsyncMock(return_value=mock_result)

                output = await delete_launch(launch_id=42, output_format="plain")

                assert "Deleted Launch 42" in output
                assert "Launch URL" not in output


@pytest.mark.asyncio
async def test_delete_launch_output_already_deleted() -> None:
    with patch("src.tools.launches.resolve_auth_settings", return_value=_resolved_auth()):
        with patch("src.tools.launches.AllureClient") as mock_client_cls:
            mock_client = _mock_url_context()
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            with patch("src.tools.launches.LaunchService") as mock_service_cls:
                mock_service = mock_service_cls.return_value
                mock_result = type(
                    "LaunchDeleteResult",
                    (),
                    {
                        "launch_id": 77,
                        "status": "already_deleted",
                        "message": "Already deleted",
                    },
                )
                mock_service.delete_launch = AsyncMock(return_value=mock_result)

                output = await delete_launch(launch_id=77, output_format="plain")

                assert "Launch 77" in output
                assert "already deleted or doesn't exist" in output


@pytest.mark.asyncio
async def test_close_launch_project_id_fallback_uses_zero_override() -> None:
    runtime_api_token = "runtime-token"
    with patch(
        "src.tools.launches.resolve_auth_settings",
        return_value=_resolved_auth(token=runtime_api_token, project_id=0),
    ):
        with patch("src.tools.launches.AllureClient") as mock_client_cls:
            mock_client = _mock_url_context(project_id=0)
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            with patch("src.tools.launches.LaunchService") as mock_service_cls:
                mock_service = mock_service_cls.return_value
                mock_service.close_launch = AsyncMock(
                    return_value=type("LaunchDto", (), {"id": 20, "name": "Launch 20", "closed": True})
                )

                await close_launch(launch_id=20, project_id=0, api_token=runtime_api_token)

                assert mock_client_cls.call_args.kwargs["project"] == 0


@pytest.mark.asyncio
async def test_close_launch_output_format() -> None:
    runtime_api_token = "runtime-token"
    with patch(
        "src.tools.launches.resolve_auth_settings",
        return_value=_resolved_auth(token=runtime_api_token),
    ):
        with patch("src.tools.launches.AllureClient") as mock_client_cls:
            mock_client = _mock_url_context()
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            with patch("src.tools.launches.LaunchService") as mock_service_cls:
                mock_service = mock_service_cls.return_value
                mock_launch = type(
                    "LaunchDto",
                    (),
                    {
                        "id": 20,
                        "name": "Launch 20",
                        "closed": True,
                        "created_date": 100,
                        "last_modified_date": 200,
                    },
                )
                mock_service.close_launch = AsyncMock(return_value=mock_launch)
                mock_launch.close_report_generation = "scheduled"

                output = await close_launch(
                    launch_id=20,
                    project_id=1,
                    api_token=runtime_api_token,
                    output_format="plain",
                )

                mock_service.close_launch.assert_called_once_with(20)
                assert output.startswith("Launch closed successfully.")
                assert "Close report generation: scheduled" in output
                assert "Status: closed" in output


@pytest.mark.asyncio
async def test_reopen_launch_project_id_fallback_uses_zero_override() -> None:
    runtime_api_token = "runtime-token"
    with patch(
        "src.tools.launches.resolve_auth_settings",
        return_value=_resolved_auth(token=runtime_api_token, project_id=0),
    ):
        with patch("src.tools.launches.AllureClient") as mock_client_cls:
            mock_client = _mock_url_context(project_id=0)
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            with patch("src.tools.launches.LaunchService") as mock_service_cls:
                mock_service = mock_service_cls.return_value
                mock_service.reopen_launch = AsyncMock(
                    return_value=type("LaunchDto", (), {"id": 21, "name": "Launch 21", "closed": False})
                )

                await reopen_launch(launch_id=21, project_id=0, api_token=runtime_api_token)

                assert mock_client_cls.call_args.kwargs["project"] == 0


@pytest.mark.asyncio
async def test_reopen_launch_output_format() -> None:
    runtime_api_token = "runtime-token"
    with patch(
        "src.tools.launches.resolve_auth_settings",
        return_value=_resolved_auth(token=runtime_api_token),
    ):
        with patch("src.tools.launches.AllureClient") as mock_client_cls:
            mock_client = _mock_url_context()
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            with patch("src.tools.launches.LaunchService") as mock_service_cls:
                mock_service = mock_service_cls.return_value
                mock_launch = type(
                    "LaunchDto",
                    (),
                    {
                        "id": 21,
                        "name": "Launch 21",
                        "closed": False,
                        "created_date": 101,
                        "last_modified_date": 201,
                    },
                )
                mock_service.reopen_launch = AsyncMock(return_value=mock_launch)

                output = await reopen_launch(
                    launch_id=21,
                    project_id=1,
                    api_token=runtime_api_token,
                    output_format="plain",
                )

                mock_service.reopen_launch.assert_called_once_with(21)
                assert output.startswith("Launch reopened successfully.")
                assert "Status: open" in output
