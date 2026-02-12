"""Integration tests for launch tools."""

from unittest.mock import AsyncMock, patch

import pytest

from src.tools.launches import close_launch, create_launch, get_launch, list_launches, reopen_launch


@pytest.mark.asyncio
async def test_create_launch_tool_success() -> None:
    with patch("src.tools.launches.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.launches.LaunchService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_launch = type("LaunchDto", (), {"id": 55, "name": "Launch 55"})
            mock_service.create_launch = AsyncMock(return_value=mock_launch)

            output = await create_launch(name="Launch 55")

            assert "Launch created successfully" in output
            assert "ID: 55" in output
            assert "Name: Launch 55" in output
            mock_service.create_launch.assert_called_once()


@pytest.mark.asyncio
async def test_list_launches_tool_output() -> None:
    with patch("src.tools.launches.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.launches.LaunchService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            result = type(
                "LaunchListResult",
                (),
                {
                    "items": [type("Launch", (), {"id": 9, "name": "Launch 9", "created_date": 321, "closed": True})],
                    "total": 1,
                    "page": 0,
                    "size": 20,
                    "total_pages": 1,
                },
            )
            mock_service.list_launches = AsyncMock(return_value=result)

            output = await list_launches(page=0, size=20)

            assert "Found 1 launches" in output
            assert "#9" in output
            assert "Launch 9" in output
            mock_service.list_launches.assert_called_once_with(page=0, size=20, search=None, filter_id=None, sort=None)


@pytest.mark.asyncio
async def test_get_launch_tool_output() -> None:
    with patch("src.tools.launches.get_auth_context") as mock_auth_context:
        mock_auth_context.return_value = type("AuthContext", (), {"api_token": "runtime-token", "project_id": 1})
        with patch(
            "src.tools.launches.settings",
            type("Settings", (), {"ALLURE_ENDPOINT": "https://example.com", "ALLURE_PROJECT_ID": 1}),
        ):
            with patch("src.tools.launches.AllureClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client_cls.return_value.__aenter__.return_value = mock_client

                with patch("src.tools.launches.LaunchService") as mock_service_cls:
                    mock_service = mock_service_cls.return_value
                    mock_launch = type(
                        "LaunchDto",
                        (),
                        {
                            "id": 12,
                            "name": "Launch 12",
                            "closed": True,
                            "created_date": 100,
                            "last_modified_date": 200,
                        },
                    )
                    mock_service.get_launch = AsyncMock(return_value=mock_launch)

                    output = await get_launch(launch_id=12)

                    mock_auth_context.assert_called_once_with(project_id=None)
                    assert "Launch details" in output
                    assert "ID: 12" in output
                    assert "Status: closed" in output
                    assert "Started: 100" in output
                    assert "Ended: 200" in output


@pytest.mark.asyncio
async def test_close_launch_tool_output() -> None:
    with patch("src.tools.launches.get_auth_context") as mock_auth_context:
        mock_auth_context.return_value = type("AuthContext", (), {"api_token": "runtime-token", "project_id": 1})
        with patch(
            "src.tools.launches.settings",
            type("Settings", (), {"ALLURE_ENDPOINT": "https://example.com", "ALLURE_PROJECT_ID": 1}),
        ):
            with patch("src.tools.launches.AllureClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client_cls.return_value.__aenter__.return_value = mock_client

                with patch("src.tools.launches.LaunchService") as mock_service_cls:
                    mock_service = mock_service_cls.return_value
                    mock_launch = type(
                        "LaunchDto",
                        (),
                        {
                            "id": 13,
                            "name": "Launch 13",
                            "closed": True,
                            "created_date": 110,
                            "last_modified_date": 210,
                        },
                    )
                    mock_service.close_launch = AsyncMock(return_value=mock_launch)

                    runtime_api_token = mock_auth_context.return_value.api_token
                    output = await close_launch(launch_id=13, project_id=1, api_token=runtime_api_token)

                    mock_auth_context.assert_called_once_with(api_token=runtime_api_token, project_id=1)
                    mock_service.close_launch.assert_called_once_with(13)
                    assert output.startswith("Launch closed successfully.")
                    assert "Status: closed" in output


@pytest.mark.asyncio
async def test_reopen_launch_tool_output() -> None:
    with patch("src.tools.launches.get_auth_context") as mock_auth_context:
        mock_auth_context.return_value = type("AuthContext", (), {"api_token": "runtime-token", "project_id": 1})
        with patch(
            "src.tools.launches.settings",
            type("Settings", (), {"ALLURE_ENDPOINT": "https://example.com", "ALLURE_PROJECT_ID": 1}),
        ):
            with patch("src.tools.launches.AllureClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client_cls.return_value.__aenter__.return_value = mock_client

                with patch("src.tools.launches.LaunchService") as mock_service_cls:
                    mock_service = mock_service_cls.return_value
                    mock_launch = type(
                        "LaunchDto",
                        (),
                        {
                            "id": 14,
                            "name": "Launch 14",
                            "closed": False,
                            "created_date": 120,
                            "last_modified_date": 220,
                        },
                    )
                    mock_service.reopen_launch = AsyncMock(return_value=mock_launch)

                    runtime_api_token = mock_auth_context.return_value.api_token
                    output = await reopen_launch(launch_id=14, project_id=1, api_token=runtime_api_token)

                    mock_auth_context.assert_called_once_with(api_token=runtime_api_token, project_id=1)
                    mock_service.reopen_launch.assert_called_once_with(14)
                    assert output.startswith("Launch reopened successfully.")
                    assert "Status: open" in output
