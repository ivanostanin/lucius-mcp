"""Unit tests for launch tools formatting."""

from unittest.mock import AsyncMock, patch

import pytest

from src.tools.launches import create_launch, list_launches


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
