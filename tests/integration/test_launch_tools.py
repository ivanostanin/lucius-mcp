"""Integration tests for launch tools."""

from unittest.mock import AsyncMock, patch

import pytest

from src.tools.launches import create_launch, get_launch, list_launches


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
        mock_auth_context.return_value = type("AuthContext", (), {"api_token": "token", "project_id": 1})
        with patch(
            "src.tools.launches.settings",
            type("Settings", (), {"ALLURE_ENDPOINT": "https://example.com", "ALLURE_PROJECT_ID": 1}),
        ):
            with patch("src.tools.launches.AllureClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client_cls.return_value.__aenter__.return_value = mock_client

                with patch("src.tools.launches.LaunchService") as mock_service_cls:
                    mock_service = mock_service_cls.return_value
                    mock_launch = type("LaunchDto", (), {"id": 12, "name": "Launch 12", "closed": True})
                    mock_service.get_launch = AsyncMock(return_value=mock_launch)

                    output = await get_launch(launch_id=12)

                    assert "Launch details" in output
                    assert "ID: 12" in output
                    assert "Status: closed" in output
