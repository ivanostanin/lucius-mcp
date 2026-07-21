"""Service for generating automated test code from TestOps test cases."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Final

from src.client import AllureClient
from src.client.exceptions import AllureValidationError
from src.client.generated.api.ide_controller_api import IdeControllerApi
from src.client.generated.models.test_code_generation_request_dto import TestCodeGenerationRequestDto

LANGUAGE_LABELS: Final[tuple[str, ...]] = (
    "Java",
    "Python",
    "TypeScript",
    "JavaScript",
    "Kotlin",
    "PHP",
    ".NET",
)
METADATA_LABELS: Final[tuple[str, ...]] = ("Name", "Tags", "Custom fields", "Members", "Issues", "Scenario")
DEFAULT_METADATA: Final[tuple[str, ...]] = ("Name", "Tags", "Custom fields", "Scenario")

_LANGUAGES: Final[dict[str, tuple[str, str]]] = {
    "java": ("Java", "java"),
    "python": ("Python", "python"),
    "typescript": ("TypeScript", "ts"),
    "ts": ("TypeScript", "ts"),
    "javascript": ("JavaScript", "js"),
    "js": ("JavaScript", "js"),
    "kotlin": ("Kotlin", "kotlin"),
    "php": ("PHP", "php"),
    ".net": (".NET", "dotnet"),
    "dotnet": (".NET", "dotnet"),
}

# These mappings are verified against the authenticated TestOps UI and its
# loaded code-generation module. Keys include public aliases retained from 7.7.
_FRAMEWORKS: Final[dict[str, dict[str, tuple[str, str]]]] = {
    "Java": {
        "junit 5": ("JUnit 5", "junit5"),
        "junit5": ("JUnit 5", "junit5"),
        "junit": ("JUnit 5", "junit5"),
        "junit 4": ("JUnit 4", "junit4"),
        "junit4": ("JUnit 4", "junit4"),
        "testng": ("TestNG", "testng"),
        "cucumber": ("Cucumber", "cucumber-jvm"),
        "cucumber-jvm": ("Cucumber", "cucumber-jvm"),
    },
    "Python": {
        "behave": ("Behave", "behave"),
        "pytest": ("Pytest", "pytest"),
        "pytest bdd": ("Pytest BDD", "pytest-bdd"),
        "pytest-bdd": ("Pytest BDD", "pytest-bdd"),
    },
    "TypeScript": {
        "codeceptjs": ("CodeceptJS", "codeceptjs"),
        "cucumber": ("Cucumber", "cucumber-js"),
        "cucumber-js": ("Cucumber", "cucumber-js"),
        "jasmine": ("Jasmine", "jasmine"),
        "jest": ("Jest", "jest"),
        "mocha": ("Mocha", "mocha"),
        "playwright": ("Playwright", "playwright"),
        "vitest": ("Vitest", "vitest"),
        "webdriverio": ("WebdriverIO", "wdio"),
        "wdio": ("WebdriverIO", "wdio"),
        "zerostep": ("ZeroStep", "zerostep"),
    },
    "JavaScript": {
        "codeceptjs": ("CodeceptJS", "codeceptjs"),
        "cucumber": ("Cucumber", "cucumber-js"),
        "cucumber-js": ("Cucumber", "cucumber-js"),
        "jasmine": ("Jasmine", "jasmine"),
        "jest": ("Jest", "jest"),
        "mocha": ("Mocha", "mocha"),
        "playwright": ("Playwright", "playwright"),
        "vitest": ("Vitest", "vitest"),
        "webdriverio": ("WebdriverIO", "wdio"),
        "wdio": ("WebdriverIO", "wdio"),
    },
    "Kotlin": {
        "junit 5": ("JUnit 5", "junit5"),
        "junit5": ("JUnit 5", "junit5"),
        "junit": ("JUnit 5", "junit5"),
        "junit 4": ("JUnit 4", "junit4"),
        "junit4": ("JUnit 4", "junit4"),
        "testng": ("TestNG", "testng"),
    },
    "PHP": {
        "phpunit": ("PHPUnit", "phpunit"),
        "codeception": ("Codeception", "codeception"),
    },
    ".NET": {
        "nunit": ("NUnit", "nunit"),
        "xunit": ("XUnit", "xunit"),
        "specflow": ("SpecFlow", "specflow"),
    },
}
_METADATA: Final[dict[str, str]] = {label.casefold(): label for label in METADATA_LABELS}


@dataclass(frozen=True)
class CodeGenerationSelection:
    """Canonical labels and verified wire values for one generation request."""

    language: str
    language_wire: str
    framework: str
    framework_wire: str
    metadata: tuple[str, ...]


class TestCodeService:
    """Generate framework-specific test code using the TestOps IDE API."""

    def __init__(self, client: AllureClient) -> None:
        """Initialize the service with an authenticated TestOps client."""
        self._client = client

    @property
    def _api(self) -> IdeControllerApi:
        """Return the generated controller for the IDE API."""
        return IdeControllerApi(self._client.api_client)

    def resolve_selection(
        self,
        lang: str | None,
        framework: str | None,
        metadata: Sequence[str] | None = None,
    ) -> CodeGenerationSelection:
        """Validate user choices and resolve them to canonical labels and wire values."""
        if not isinstance(lang, str) or not lang.strip():
            raise AllureValidationError(f"Language is required. Supported languages: {', '.join(LANGUAGE_LABELS)}")
        language = _LANGUAGES.get(lang.strip().casefold())
        if language is None:
            raise AllureValidationError(
                f"Unsupported language '{lang}'. Supported languages: {', '.join(LANGUAGE_LABELS)}"
            )

        language_label, language_wire = language
        if not isinstance(framework, str) or not framework.strip():
            raise AllureValidationError(
                f"Framework is required for {language_label}. Compatible frameworks: "
                f"{', '.join(self._framework_labels(language_label))}"
            )
        framework_option = _FRAMEWORKS[language_label].get(framework.strip().casefold())
        if framework_option is None:
            raise AllureValidationError(
                f"Unsupported framework '{framework}' for {language_label}. Compatible frameworks: "
                f"{', '.join(self._framework_labels(language_label))}"
            )

        return CodeGenerationSelection(
            language=language_label,
            language_wire=language_wire,
            framework=framework_option[0],
            framework_wire=framework_option[1],
            metadata=self._normalize_metadata(metadata),
        )

    @staticmethod
    def _framework_labels(language: str) -> tuple[str, ...]:
        return tuple(dict.fromkeys(label for label, _ in _FRAMEWORKS[language].values()))

    @staticmethod
    def _normalize_metadata(metadata: Sequence[str] | None) -> tuple[str, ...]:
        if metadata is None:
            return DEFAULT_METADATA
        if isinstance(metadata, (str, bytes)):
            raise AllureValidationError(f"Metadata must be a list containing: {', '.join(METADATA_LABELS)}")

        selected: set[str] = set()
        for value in metadata:
            if not isinstance(value, str) or not value.strip():
                raise AllureValidationError(
                    f"Unsupported metadata value. Supported values: {', '.join(METADATA_LABELS)}"
                )
            canonical = _METADATA.get(value.strip().casefold())
            if canonical is None:
                raise AllureValidationError(
                    f"Unsupported metadata '{value}'. Supported values: {', '.join(METADATA_LABELS)}"
                )
            selected.add(canonical)
        return tuple(label for label in METADATA_LABELS if label in selected)

    async def generate_code(
        self,
        test_case_id: int,
        lang: str | None,
        framework: str | None,
        metadata: Sequence[str] | None = None,
    ) -> str:
        """Generate code for one test case in the requested language and framework.

        The IDE endpoint synchronizes all test-case fields before generating the
        snippet, so callers always receive code for the current TestOps state.

        Args:
            test_case_id: ID of the source TestOps test case.
            lang: Target programming language selection or retained canonical alias.
            framework: Target test framework selection or retained canonical alias.
            metadata: Metadata selections, or ``None`` for the story default.

        Returns:
            The generated source-code snippet.

        Raises:
            AllureValidationError: If the test case ID, language, or framework is blank.
        """
        if not isinstance(test_case_id, int) or isinstance(test_case_id, bool) or test_case_id <= 0:
            raise AllureValidationError("Test Case ID must be a positive integer")
        selection = self.resolve_selection(lang, framework, metadata)
        selected_metadata = set(selection.metadata)

        request = TestCodeGenerationRequestDto(
            lang=selection.language_wire,
            test_framework=selection.framework_wire,
            sync_fields="Custom fields" in selected_metadata,
            sync_name="Name" in selected_metadata,
            sync_tags="Tags" in selected_metadata,
            sync_members="Members" in selected_metadata,
            sync_issues="Issues" in selected_metadata,
            sync_scenario="Scenario" in selected_metadata,
        )
        response = await self._client._call_api(
            self._api.generate_test_code(
                id=test_case_id,
                test_code_generation_request_dto=request,
                _request_timeout=self._client._timeout,
            )
        )
        return response.code
