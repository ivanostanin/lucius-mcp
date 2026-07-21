"""MCP tool for generating automated test code from TestOps test cases."""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.test_code_service import TestCodeService
from src.tools.output_contract import DEFAULT_OUTPUT_FORMAT, OutputFormat, ToolOutput, render_output
from src.tools.output_schemas import output_fields


@output_fields("test_case_id", "language", "framework", "code")
async def generate_test_code(
    test_case_id: Annotated[int, Field(description="ID of the TestOps test case to generate code for.")],
    language: Annotated[
        str,
        Field(description="Target programming language accepted by TestOps, for example 'python', 'ts', or 'java'."),
    ] = "python",
    framework: Annotated[
        str,
        Field(
            description="Target testing framework accepted by TestOps, for example 'pytest', 'playwright', or 'junit'."
        ),
    ] = "pytest",
    output_format: Annotated[
        OutputFormat | None,
        Field(description="Output format: 'json' (default) or 'plain'."),
    ] = DEFAULT_OUTPUT_FORMAT,
) -> ToolOutput:
    """Generate a current, framework-specific test snippet from a TestOps test case.

    TestOps synchronizes the test case's fields, name, tags, and scenario before
    generation. Language and framework values are passed to TestOps unchanged,
    allowing the server to report unsupported combinations precisely.

    Args:
        test_case_id: ID of the test case whose automation code should be generated.
        language: Target language, such as ``python``, ``ts``, or ``java``.
        framework: Target framework, such as ``pytest``, ``playwright``, or ``junit``.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        Generated source code with the requested language and framework metadata.
    """
    async with AllureClient.from_env() as client:
        code = await TestCodeService(client).generate_code(test_case_id, language, framework)
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
                "language": language,
                "framework": framework,
                "code": code,
            },
            output_format=output_format,
        )
