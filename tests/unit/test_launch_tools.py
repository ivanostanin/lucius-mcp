"""Unit tests for launch tools formatting."""

from unittest.mock import AsyncMock, patch

import pytest

from src.tools.launches import create_launch, get_launch, list_launches


@pytest.mark.asyncio
async def test_create_launch_output_format() -> None:
    with patch("src.tools.launches.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.launches.LaunchService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_launch = type("LaunchDto", (), {"id": 10, "name": "Launch"})
            mock_service.create_launch = AsyncMock(return_value=mock_launch)

            output = await create_launch(name="Launch")

            assert "✅ Launch created successfully!" in output
            assert "ID: 10" in output
            assert "Name: Launch" in output


@pytest.mark.asyncio
async def test_list_launches_output_format() -> None:
    with patch("src.tools.launches.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
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

            output = await list_launches(page=0, size=20)

            assert "Found 1 launches" in output
            assert "#1" in output
            assert "L1" in output


@pytest.mark.asyncio
async def test_list_launches_empty() -> None:
    with patch("src.tools.launches.AllureClient.from_env") as mock_client_ctx:
        mock_client = AsyncMock()
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.launches.LaunchService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            result = type(
                "LaunchListResult",
                (),
                {"items": [], "total": 0, "page": 0, "size": 20, "total_pages": 0},
            )
            mock_service.list_launches = AsyncMock(return_value=result)

            output = await list_launches(page=0, size=20)

            assert "No launches found" in output


@pytest.mark.asyncio
async def test_get_launch_output_format() -> None:
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

                    output = await get_launch(launch_id=10)

                    assert "Launch details" in output
                    assert "ID: 10" in output
                    assert "Status: open" in output
                    assert "Started: 123" in output
                    assert "Ended: 456" in output
                    assert "Known defects: 2" in output
                    assert "New defects: 1" in output
                    assert "Summary: passed=7, failed=1" in output
