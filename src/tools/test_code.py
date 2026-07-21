"""MCP tool for generating automated test code from TestOps test cases."""

from typing import Annotated, Literal

from pydantic import Field

from src.client import AllureClient
from src.services.test_code_service import TestCodeService
from src.tools.output_contract import DEFAULT_OUTPUT_FORMAT, OutputFormat, ToolOutput, render_output
from src.tools.output_schemas import output_fields

type LanguageSelection = Literal[
    "Java", "Python", "TypeScript", "JavaScript", "Kotlin", "PHP", ".NET", "java", "python", "ts", "js", "dotnet"
]
type FrameworkSelection = Literal[
    "JUnit 5",
    "JUnit 4",
    "TestNG",
    "Cucumber",
    "Behave",
    "Pytest",
    "Pytest BDD",
    "CodeceptJS",
    "Jasmine",
    "Jest",
    "Mocha",
    "Playwright",
    "Vitest",
    "WebdriverIO",
    "ZeroStep",
    "PHPUnit",
    "Codeception",
    "NUnit",
    "XUnit",
    "SpecFlow",
    "junit",
    "junit5",
    "junit4",
    "testng",
    "cucumber-jvm",
    "behave",
    "pytest",
    "pytest-bdd",
    "codeceptjs",
    "cucumber-js",
    "jasmine",
    "jest",
    "mocha",
    "playwright",
    "vitest",
    "wdio",
    "zerostep",
    "phpunit",
    "codeception",
    "nunit",
    "xunit",
    "specflow",
]
type MetadataSelection = Literal["Name", "Tags", "Custom fields", "Members", "Issues", "Scenario"]


@output_fields("test_case_id", "language", "framework", "metadata", "code")
async def generate_test_code(
    test_case_id: Annotated[int, Field(description="ID of the TestOps test case to generate code for.")],
    language: Annotated[
        LanguageSelection,
        Field(
            description=(
                "Required target language. Choose Java, Python, TypeScript, JavaScript, Kotlin, PHP, or .NET. "
                "Backward-compatible aliases: java, python, ts, js, and dotnet."
            ),
        ),
    ],
    framework: Annotated[
        FrameworkSelection,
        Field(
            description=(
                "Required framework compatible with language. TypeScript choices: CodeceptJS, Cucumber, Jasmine, "
                "Jest, Mocha, Playwright, Vitest, WebdriverIO, ZeroStep. Compatibility is language-specific."
            )
        ),
    ],
    metadata: Annotated[
        list[MetadataSelection] | None,
        Field(
            description=(
                "Optional metadata to synchronize: Name, Tags, Custom fields, Members, Issues, Scenario. "
                "Omit for Name, Tags, Custom fields, Scenario; use [] to disable all."
            ),
        ),
    ] = None,
    output_format: Annotated[
        OutputFormat | None,
        Field(description="Output format: 'json' (default) or 'plain'."),
    ] = DEFAULT_OUTPUT_FORMAT,
) -> ToolOutput:
    """Generate a current, framework-specific test snippet from a TestOps test case.

    Both target selections are required. The tool validates verified TestOps
    language/framework compatibility locally and synchronizes only requested
    test-case metadata before generation.

    Args:
        test_case_id: ID of the test case whose automation code should be generated.
        language: Required language selection. Aliases ``python``, ``ts``, and ``java`` remain supported.
        framework: Required framework compatible with the selected language.
        metadata: Metadata selections; omitted selects Name, Tags, Custom fields, and Scenario.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        Generated source code with the requested language and framework metadata.
    """
    async with AllureClient.from_env() as client:
        service = TestCodeService(client)
        selection = service.resolve_selection(language, framework, metadata)
        code = await service.generate_code(test_case_id, language, framework, metadata)
        # Generated source can legitimately contain literal escape sequences
        # (for example, ``"\\n"`` in a Python string). The generic plain-text
        # renderer expands those sequences for human-readable tool responses,
        # so return source verbatim instead.
        if output_format == "plain":
            return code
        return render_output(
            plain=code,
            json_payload={
                "test_case_id": test_case_id,
                "language": selection.language,
                "framework": selection.framework,
                "metadata": list(selection.metadata),
                "code": code,
            },
            output_format=output_format,
        )
