"""Unit tests for TestCodeService."""

from collections.abc import Awaitable
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.client import AllureClient
from src.client.exceptions import AllureValidationError
from src.client.generated.models.test_code_generation_response_dto import TestCodeGenerationResponseDto
from src.services.test_code_service import DEFAULT_METADATA, METADATA_LABELS, TestCodeService


@pytest.fixture
def client() -> MagicMock:
    client = MagicMock(spec=AllureClient)
    client.api_client = MagicMock()
    client._timeout = 30.0

    async def call_api(coro: Awaitable[TestCodeGenerationResponseDto]) -> TestCodeGenerationResponseDto:
        return await coro

    client._call_api = AsyncMock(side_effect=call_api)
    return client


@pytest.mark.parametrize(
    ("language", "framework", "language_wire", "framework_wire"),
    [
        ("Java", "JUnit 5", "java", "junit5"),
        ("Java", "JUnit 4", "java", "junit4"),
        ("Java", "TestNG", "java", "testng"),
        ("Java", "Cucumber", "java", "cucumber-jvm"),
        ("Python", "Behave", "python", "behave"),
        ("Python", "Pytest", "python", "pytest"),
        ("Python", "Pytest BDD", "python", "pytest-bdd"),
        ("TypeScript", "CodeceptJS", "ts", "codeceptjs"),
        ("TypeScript", "Cucumber", "ts", "cucumber-js"),
        ("TypeScript", "Jasmine", "ts", "jasmine"),
        ("TypeScript", "Jest", "ts", "jest"),
        ("TypeScript", "Mocha", "ts", "mocha"),
        ("TypeScript", "Playwright", "ts", "playwright"),
        ("TypeScript", "Vitest", "ts", "vitest"),
        ("TypeScript", "WebdriverIO", "ts", "wdio"),
        ("TypeScript", "ZeroStep", "ts", "zerostep"),
        ("JavaScript", "CodeceptJS", "js", "codeceptjs"),
        ("JavaScript", "Cucumber", "js", "cucumber-js"),
        ("JavaScript", "Jasmine", "js", "jasmine"),
        ("JavaScript", "Jest", "js", "jest"),
        ("JavaScript", "Mocha", "js", "mocha"),
        ("JavaScript", "Playwright", "js", "playwright"),
        ("JavaScript", "Vitest", "js", "vitest"),
        ("JavaScript", "WebdriverIO", "js", "wdio"),
        ("Kotlin", "JUnit 5", "kotlin", "junit5"),
        ("Kotlin", "JUnit 4", "kotlin", "junit4"),
        ("Kotlin", "TestNG", "kotlin", "testng"),
        ("PHP", "PHPUnit", "php", "phpunit"),
        ("PHP", "Codeception", "php", "codeception"),
        (".NET", "NUnit", "dotnet", "nunit"),
        (".NET", "XUnit", "dotnet", "xunit"),
        (".NET", "SpecFlow", "dotnet", "specflow"),
    ],
)
def test_resolve_selection_maps_each_verified_pair_to_testops_wire_values(
    client: MagicMock, language: str, framework: str, language_wire: str, framework_wire: str
) -> None:
    selection = TestCodeService(client).resolve_selection(language, framework)

    assert selection.language_wire == language_wire
    assert selection.framework_wire == framework_wire
    assert selection.metadata == DEFAULT_METADATA


@pytest.mark.parametrize(
    ("language", "framework", "expected_language", "expected_framework"),
    [
        ("python", "pytest", "Python", "Pytest"),
        ("ts", "playwright", "TypeScript", "Playwright"),
        ("java", "junit", "Java", "JUnit 5"),
    ],
)
def test_resolve_selection_retains_existing_aliases(
    client: MagicMock, language: str, framework: str, expected_language: str, expected_framework: str
) -> None:
    selection = TestCodeService(client).resolve_selection(language, framework)

    assert (selection.language, selection.framework) == (expected_language, expected_framework)


@pytest.mark.parametrize("metadata", [None, [], ["Scenario", "Name", "Name", "Tags"]])
async def test_generate_code_builds_complete_metadata_payload(client: MagicMock, metadata: list[str] | None) -> None:
    response = TestCodeGenerationResponseDto(code="def test_login():\n    pass")
    with patch("src.services.test_code_service.IdeControllerApi") as api_class:
        api_class.return_value.generate_test_code = AsyncMock(return_value=response)

        code = await TestCodeService(client).generate_code(42, "Python", "Pytest", metadata)

    assert code == "def test_login():\n    pass"
    request = api_class.return_value.generate_test_code.await_args.kwargs["test_code_generation_request_dto"]
    selected = set(DEFAULT_METADATA if metadata is None else metadata)
    assert request.model_dump(by_alias=True) == {
        "lang": "python",
        "testFramework": "pytest",
        "syncFields": "Custom fields" in selected,
        "syncName": "Name" in selected,
        "syncTags": "Tags" in selected,
        "syncMembers": "Members" in selected,
        "syncIssues": "Issues" in selected,
        "syncScenario": "Scenario" in selected,
    }
    api_class.return_value.generate_test_code.assert_awaited_once_with(
        id=42,
        test_code_generation_request_dto=request,
        _request_timeout=30.0,
    )


@pytest.mark.parametrize("metadata", [[label] for label in METADATA_LABELS])
async def test_generate_code_enables_each_metadata_flag_independently(client: MagicMock, metadata: list[str]) -> None:
    response = TestCodeGenerationResponseDto(code="code")
    with patch("src.services.test_code_service.IdeControllerApi") as api_class:
        api_class.return_value.generate_test_code = AsyncMock(return_value=response)

        await TestCodeService(client).generate_code(42, "Python", "Pytest", metadata)

    request = api_class.return_value.generate_test_code.await_args.kwargs["test_code_generation_request_dto"]
    enabled = {
        "Name": "syncName",
        "Tags": "syncTags",
        "Custom fields": "syncFields",
        "Members": "syncMembers",
        "Issues": "syncIssues",
        "Scenario": "syncScenario",
    }
    assert all(
        value is (field == enabled[metadata[0]])
        for field, value in request.model_dump(by_alias=True).items()
        if field.startswith("sync")
    )


@pytest.mark.parametrize(
    ("metadata", "expected"),
    [
        (list(METADATA_LABELS), METADATA_LABELS),
        (["Scenario", "Name", "Name", "Tags"], ("Name", "Tags", "Scenario")),
    ],
)
def test_resolve_selection_normalizes_all_and_duplicate_metadata_in_canonical_order(
    client: MagicMock, metadata: list[str], expected: tuple[str, ...]
) -> None:
    selection = TestCodeService(client).resolve_selection("Python", "Pytest", metadata)

    assert selection.metadata == expected


@pytest.mark.parametrize("test_case_id", [0, -1, True, "42"])
async def test_generate_code_requires_a_positive_integer_test_case_id(client: MagicMock, test_case_id: object) -> None:
    with pytest.raises(AllureValidationError, match="positive integer"):
        await TestCodeService(client).generate_code(test_case_id, "python", "pytest")  # type: ignore[arg-type]
    client._call_api.assert_not_awaited()


@pytest.mark.parametrize(
    ("language", "framework", "metadata", "message"),
    [
        (None, "pytest", None, "Language is required"),
        ("unknown", "pytest", None, "Supported languages"),
        ("Python", None, None, "Framework is required"),
        ("Python", "Playwright", None, "Compatible frameworks"),
        ("Python", "Pytest", ["Unknown"], "Unsupported metadata"),
        ("Python", "Pytest", "Name", "Metadata must be a list"),
    ],
)
async def test_generate_code_rejects_invalid_selections_without_an_api_call(
    client: MagicMock, language: str | None, framework: str | None, metadata: object, message: str
) -> None:
    with pytest.raises(AllureValidationError, match=message):
        await TestCodeService(client).generate_code(42, language, framework, metadata)  # type: ignore[arg-type]
    client._call_api.assert_not_awaited()


async def test_generate_code_preserves_api_validation_errors(client: MagicMock) -> None:
    async def raise_api_error(coro: Awaitable[TestCodeGenerationResponseDto]) -> TestCodeGenerationResponseDto:
        await coro
        raise AllureValidationError("Unsupported framework: unknown")

    client._call_api = AsyncMock(side_effect=raise_api_error)
    with patch("src.services.test_code_service.IdeControllerApi") as api_class:
        api_class.return_value.generate_test_code = AsyncMock()

        with pytest.raises(AllureValidationError, match="Unsupported framework: unknown"):
            await TestCodeService(client).generate_code(42, "python", "pytest")
