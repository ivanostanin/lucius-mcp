"""Unit tests for TestCodeService."""

from collections.abc import Awaitable
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.client import AllureClient
from src.client.exceptions import AllureValidationError
from src.client.generated.models.test_code_generation_response_dto import TestCodeGenerationResponseDto
from src.services.test_code_service import TestCodeService


@pytest.fixture
def client() -> MagicMock:
    client = MagicMock(spec=AllureClient)
    client.api_client = MagicMock()
    client._timeout = 30.0

    async def call_api(coro: Awaitable[TestCodeGenerationResponseDto]) -> TestCodeGenerationResponseDto:
        return await coro

    client._call_api = AsyncMock(side_effect=call_api)
    return client


async def test_generate_code_builds_generated_api_request_with_all_sync_flags(client: MagicMock) -> None:
    response = TestCodeGenerationResponseDto(code="def test_login():\n    pass")
    with patch("src.services.test_code_service.IdeControllerApi") as api_class:
        api_class.return_value.generate_test_code = AsyncMock(return_value=response)

        code = await TestCodeService(client).generate_code(42, "python", "pytest")

    assert code == "def test_login():\n    pass"
    api_class.assert_called_once_with(client.api_client)
    request = api_class.return_value.generate_test_code.await_args.kwargs["test_code_generation_request_dto"]
    assert request.model_dump(by_alias=True) == {
        "lang": "python",
        "testFramework": "pytest",
        "syncFields": True,
        "syncName": True,
        "syncTags": True,
        "syncScenario": True,
    }
    api_class.return_value.generate_test_code.assert_awaited_once_with(
        id=42,
        test_code_generation_request_dto=request,
        _request_timeout=30.0,
    )


@pytest.mark.parametrize("test_case_id", [0, -1, True, "42"])
async def test_generate_code_requires_a_positive_integer_test_case_id(client: MagicMock, test_case_id: object) -> None:
    with pytest.raises(AllureValidationError, match="positive integer"):
        await TestCodeService(client).generate_code(test_case_id, "python", "pytest")  # type: ignore[arg-type]


@pytest.mark.parametrize(("lang", "framework", "message"), [("", "pytest", "Language"), ("python", " ", "Framework")])
async def test_generate_code_requires_non_blank_target_values(
    client: MagicMock, lang: str, framework: str, message: str
) -> None:
    with pytest.raises(AllureValidationError, match=message):
        await TestCodeService(client).generate_code(42, lang, framework)


async def test_generate_code_preserves_api_validation_errors(client: MagicMock) -> None:
    async def raise_api_error(coro: Awaitable[TestCodeGenerationResponseDto]) -> TestCodeGenerationResponseDto:
        await coro
        raise AllureValidationError("Unsupported framework: unknown")

    client._call_api = AsyncMock(side_effect=raise_api_error)
    with patch("src.services.test_code_service.IdeControllerApi") as api_class:
        api_class.return_value.generate_test_code = AsyncMock()

        with pytest.raises(AllureValidationError, match="Unsupported framework: unknown"):
            await TestCodeService(client).generate_code(42, "python", "unknown")
