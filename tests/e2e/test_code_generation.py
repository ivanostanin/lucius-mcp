"""End-to-end coverage for native TestOps test-code generation."""

from src.tools.create_test_case import create_test_case
from src.tools.test_code import generate_test_code
from tests.e2e.helpers.cleanup import CleanupTracker


async def test_generate_python_pytest_code_for_a_test_case(
    cleanup_tracker: CleanupTracker,
    project_id: int,
    test_run_id: str,
) -> None:
    """Create a test case and generate its Python/pytest automation snippet."""
    created = await create_test_case(
        name=f"[{test_run_id}] Code Generation",
        steps=[{"action": "Open login page", "expected": "Login form is visible"}],
        project_id=project_id,
        output_format="plain",
    )

    import re

    match = re.search(r"ID: (\d+)", created)
    assert match, f"Could not extract test-case ID from: {created}"
    test_case_id = int(match.group(1))
    cleanup_tracker.track_test_case(test_case_id)

    code = await generate_test_code(test_case_id=test_case_id, output_format="plain")

    assert "import" in code.lower() or "test" in code.lower()
