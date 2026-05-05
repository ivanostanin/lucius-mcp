from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.client.generated.models.shared_step_step_dto import SharedStepStepDto
from src.tools.link_shared_step import link_shared_step
from src.tools.unlink_shared_step import unlink_shared_step


def _mock_url_context(project_id: int = 1) -> MagicMock:
    mock_client = MagicMock()
    mock_client.get_base_url.return_value = "https://example.com"
    mock_client.get_project.return_value = project_id
    return mock_client


def _scenario_with_shared_step(shared_step_id: int) -> SimpleNamespace:
    step = SimpleNamespace(actual_instance=SharedStepStepDto(type="SharedStepStepDto", shared_step_id=shared_step_id))
    return SimpleNamespace(steps=[step])


@pytest.mark.asyncio
async def test_link_shared_step_json_includes_entity_urls() -> None:
    with patch("src.tools.link_shared_step.AllureClient.from_env") as mock_client_ctx:
        mock_client = _mock_url_context(project_id=2)
        mock_client.get_test_case_scenario = AsyncMock(return_value=_scenario_with_shared_step(12))
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.link_shared_step.TestCaseService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_service.add_shared_step_to_case = AsyncMock()

            output = await link_shared_step(
                test_case_id=10,
                shared_step_id=12,
                confirm=True,
                output_format="json",
            )

            assert output.structured_content["test_case_url"] == "https://example.com/project/2/test-cases/10"
            assert output.structured_content["shared_step_url"] == "https://example.com/project/2/shared-steps/12"
            assert (
                output.structured_content["steps"][0]["shared_step_url"]
                == "https://example.com/project/2/shared-steps/12"
            )


@pytest.mark.asyncio
async def test_unlink_shared_step_plain_includes_entity_urls() -> None:
    with patch("src.tools.unlink_shared_step.AllureClient.from_env") as mock_client_ctx:
        mock_client = _mock_url_context(project_id=2)
        mock_client.get_test_case_scenario = AsyncMock(return_value=_scenario_with_shared_step(13))
        mock_client_ctx.return_value.__aenter__.return_value = mock_client

        with patch("src.tools.unlink_shared_step.TestCaseService") as mock_service_cls:
            mock_service = mock_service_cls.return_value
            mock_service.remove_shared_step_from_case = AsyncMock()

            output = await unlink_shared_step(
                test_case_id=10,
                shared_step_id=12,
                confirm=True,
                output_format="plain",
            )

            assert "Test Case URL: https://example.com/project/2/test-cases/10" in output
            assert "Shared Step URL: https://example.com/project/2/shared-steps/12" in output
            assert "https://example.com/project/2/shared-steps/13" in output
