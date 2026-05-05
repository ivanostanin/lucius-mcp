# ruff: noqa: S105,S106,S107
"""Unit tests for launch tools formatting."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import SecretStr

from src.tools.launches import close_launch, create_launch, delete_launch, get_launch, list_launches, reopen_launch


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
async def test_delete_launch_output_archived() -> None:
    with patch("src.tools.launches.resolve_auth_settings", return_value=_resolved_auth()):
        with patch("src.tools.launches.AllureClient") as mock_client_cls:
            mock_client = _mock_url_context()
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            with patch("src.tools.launches.LaunchService") as mock_service_cls:
                mock_service = mock_service_cls.return_value
                mock_result = type(
                    "LaunchDeleteResult",
                    (),
                    {"launch_id": 42, "status": "archived", "name": "Launch 42", "message": "Archived"},
                )
                mock_service.delete_launch = AsyncMock(return_value=mock_result)

                output = await delete_launch(launch_id=42, output_format="plain")

                assert "Archived Launch 42" in output
                assert "Launch 42" in output


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
                        "name": None,
                        "message": "Already deleted",
                    },
                )
                mock_service.delete_launch = AsyncMock(return_value=mock_result)

                output = await delete_launch(launch_id=77, output_format="plain")

                assert "Launch 77" in output
                assert "already archived or doesn't exist" in output


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
