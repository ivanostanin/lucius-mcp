"""End-to-end coverage for native TestOps test-code generation."""

import re

import pytest

from src.tools.create_test_case import create_test_case
from src.tools.test_code import FrameworkSelection, LanguageSelection, generate_test_code
from tests.e2e.helpers.cleanup import CleanupTracker


@pytest.mark.parametrize(
    ("language", "framework"),
    [
        ("Java", "JUnit 5"),
        ("Java", "JUnit 4"),
        ("Java", "TestNG"),
        ("Java", "Cucumber"),
        ("Python", "Behave"),
        ("Python", "Pytest"),
        ("Python", "Pytest BDD"),
        ("TypeScript", "CodeceptJS"),
        ("TypeScript", "Cucumber"),
        ("TypeScript", "Jasmine"),
        ("TypeScript", "Jest"),
        ("TypeScript", "Mocha"),
        ("TypeScript", "Playwright"),
        ("TypeScript", "Vitest"),
        ("TypeScript", "WebdriverIO"),
        ("TypeScript", "ZeroStep"),
        ("JavaScript", "CodeceptJS"),
        ("JavaScript", "Cucumber"),
        ("JavaScript", "Jasmine"),
        ("JavaScript", "Jest"),
        ("JavaScript", "Mocha"),
        ("JavaScript", "Playwright"),
        ("JavaScript", "Vitest"),
        ("JavaScript", "WebdriverIO"),
        ("Kotlin", "JUnit 5"),
        ("Kotlin", "JUnit 4"),
        ("Kotlin", "TestNG"),
        ("PHP", "PHPUnit"),
        ("PHP", "Codeception"),
        (".NET", "NUnit"),
        (".NET", "XUnit"),
        (".NET", "SpecFlow"),
    ],
)
async def test_generate_code_for_every_verified_language_framework_pair(
    cleanup_tracker: CleanupTracker,
    project_id: int,
    test_run_id: str,
    language: LanguageSelection,
    framework: FrameworkSelection,
) -> None:
    """Create a test case and generate code for every verified sandbox target."""
    created = await create_test_case(
        name=f"[{test_run_id}] Code Generation",
        steps=[{"action": "Open login page", "expected": "Login form is visible"}],
        project_id=project_id,
        output_format="plain",
    )

    match = re.search(r"ID: (\d+)", created)
    assert match, f"Could not extract test-case ID from: {created}"
    test_case_id = int(match.group(1))
    cleanup_tracker.track_test_case(test_case_id)

    code = await generate_test_code(
        test_case_id=test_case_id,
        language=language,
        framework=framework,
        metadata=["Name", "Tags", "Custom fields", "Scenario"],
        output_format="plain",
    )

    assert code.strip(), "TestOps returned an empty generated-code snippet"
