"""MCP tool definitions for Defect and Defect Matcher management.

Thin wrappers around DefectService — no business logic here.
"""

from typing import Annotated

from src.client import AllureClient
from src.services.defect_service import DefectService


async def create_defect(
    name: Annotated[str, "Name / title of the defect"],
    description: Annotated[str | None, "Optional markdown description"] = None,
) -> str:
    """Create a new defect in the current project.

    Use this tool to register a known defect that can later be linked
    to failing test results through defect matchers (automation rules).

    Args:
        name: Human-readable defect title. Must be non-empty.
        description: Optional markdown description providing context
            about the defect (root cause, impact, workaround, etc.).

    Returns:
        A success message containing the ID and name of the created defect.
    """
    async with AllureClient.from_env() as client:
        service = DefectService(client)
        defect = await service.create_defect(name=name, description=description)
        return f"Created Defect #{defect.id}: '{defect.name}'"


async def get_defect(
    defect_id: Annotated[int, "ID of the defect to retrieve"],
) -> str:
    """Retrieve detailed information about a specific defect.

    Args:
        defect_id: Numeric ID of the defect.

    Returns:
        Formatted defect details: ID, name, status, description.
    """
    async with AllureClient.from_env() as client:
        service = DefectService(client)
        defect = await service.get_defect(defect_id)
        status = "Closed" if defect.closed else "Open"
        lines = [
            f"Defect #{defect.id}: {defect.name}",
            f"Status: {status}",
        ]
        if defect.description:
            lines.append(f"Description: {defect.description}")
        return "\n".join(lines)


async def update_defect(
    defect_id: Annotated[int, "ID of the defect to update"],
    name: Annotated[str | None, "New defect name"] = None,
    description: Annotated[str | None, "New markdown description"] = None,
    closed: Annotated[bool | None, "Set to true to close, false to reopen"] = None,
) -> str:
    """Update an existing defect's name, description, or status.

    At least one field must be provided. Fields set to null/None are
    left unchanged.

    Args:
        defect_id: Numeric ID of the defect to update.
        name: New defect title (optional).
        description: New markdown description (optional).
        closed: Set to true to close the defect, false to reopen (optional).

    Returns:
        A success message with the updated defect ID and current status.
    """
    async with AllureClient.from_env() as client:
        service = DefectService(client)
        defect = await service.update_defect(
            defect_id=defect_id,
            name=name,
            description=description,
            closed=closed,
        )
        status = "Closed" if defect.closed else "Open"
        return f"Updated Defect #{defect.id}: '{defect.name}' (Status: {status})"


async def delete_defect(
    defect_id: Annotated[int, "ID of the defect to delete"],
    confirm: Annotated[
        bool,
        "Safety flag — must be set to true to confirm deletion",
    ] = False,
) -> str:
    """Permanently delete a defect and all its associated matchers.

    This is a destructive operation. The ``confirm`` parameter must be
    set to ``true`` to actually perform the deletion.

    Args:
        defect_id: Numeric ID of the defect to delete.
        confirm: Must be explicitly set to true. Prevents accidental
            deletion when the agent misinterprets the user's intent.

    Returns:
        Confirmation or rejection message.
    """
    if not confirm:
        return f"Deletion aborted. Set confirm=true to permanently delete Defect #{defect_id}."
    async with AllureClient.from_env() as client:
        service = DefectService(client)
        await service.delete_defect(defect_id)
        return f"Deleted Defect #{defect_id}"


async def list_defects() -> str:
    """List all defects in the current project.

    Returns:
        A formatted list of defects with their IDs, names, and status.
        Returns a message if no defects exist.
    """
    async with AllureClient.from_env() as client:
        service = DefectService(client)
        defects = await service.list_defects()
        if not defects:
            return "No defects found in the current project."
        lines: list[str] = [f"Found {len(defects)} defect(s):"]
        for d in defects:
            status = "Closed" if d.closed else "Open"
            lines.append(f"  • #{d.id}: {d.name} ({status})")
        return "\n".join(lines)


async def link_defect_to_test_case(
    defect_id: Annotated[int, "ID of the defect to link"],
    test_case_id: Annotated[int, "ID of the test case to link"],
    issue_key: Annotated[
        str | None,
        "Issue key to use for linking (for example, PROJ-123). "
        "If omitted, the defect's existing issue mapping is reused.",
    ] = None,
    integration_id: Annotated[
        int | None,
        "Optional integration ID for issue mapping. Mutually exclusive with integration_name.",
    ] = None,
    integration_name: Annotated[
        str | None,
        "Optional integration name for issue mapping. Mutually exclusive with integration_id.",
    ] = None,
) -> str:
    """Link a defect to a test case through a shared issue mapping.

    This operation ensures defect governance and test coverage are connected:
    the issue is linked to the defect and to the specified test case.

    Args:
        defect_id: Numeric ID of the defect.
        test_case_id: Numeric ID of the test case.
        issue_key: Optional issue key. If omitted, uses existing defect issue mapping.
        integration_id: Optional integration ID for issue mapping.
        integration_name: Optional integration name for issue mapping.

    Returns:
        Confirmation message including defect, test case, and issue mapping details.
    """
    async with AllureClient.from_env() as client:
        service = DefectService(client)
        result = await service.link_defect_to_test_case(
            defect_id=defect_id,
            test_case_id=test_case_id,
            issue_key=issue_key,
            integration_id=integration_id,
            integration_name=integration_name,
        )

        if result.already_linked:
            return (
                f"Defect #{result.defect_id} is already linked to Test Case #{result.test_case_id} "
                f"via issue '{result.issue_key}' (integration ID: {result.integration_id}). No changes made."
            )

        return (
            f"Linked Defect #{result.defect_id} to Test Case #{result.test_case_id} "
            f"via issue '{result.issue_key}' (integration ID: {result.integration_id})."
        )


async def list_defect_test_cases(
    defect_id: Annotated[int, "ID of the defect whose linked test cases should be listed"],
    page: Annotated[int, "Zero-based page index"] = 0,
    size: Annotated[int, "Page size (1..100)"] = 20,
) -> str:
    """List test cases currently linked to a defect.

    Args:
        defect_id: Numeric ID of the defect.
        page: Zero-based page index.
        size: Page size (1..100).

    Returns:
        Paginated list of linked test cases with ID, name, and status.
    """
    async with AllureClient.from_env() as client:
        service = DefectService(client)
        result = await service.list_defect_test_cases(defect_id=defect_id, page=page, size=size)

        if not result.items:
            return f"No test cases linked to Defect #{defect_id}."

        total_pages = result.total_pages if result.total_pages > 0 else 1
        lines = [
            f"Found {result.total} linked test case(s) for Defect #{defect_id} "
            f"(page {result.page + 1} of {total_pages}):"
        ]
        for case in result.items:
            case_id = case.id if case.id is not None else "N/A"
            case_name = case.name or "(unnamed)"
            status_name = case.status.name if case.status and case.status.name else "Unknown"
            lines.append(f"  • #{case_id}: {case_name} [{status_name}]")
        return "\n".join(lines)


# ── Defect Matcher tools ──────────────────────────────────────────


async def create_defect_matcher(
    defect_id: Annotated[int, "ID of the parent defect"],
    name: Annotated[str, "Human-readable matcher rule name"],
    message_regex: Annotated[
        str | None,
        "Regex to match against error messages",
    ] = None,
    trace_regex: Annotated[
        str | None,
        "Regex to match against stack traces",
    ] = None,
) -> str:
    """Create a defect matcher (automation rule) for a defect.

    Matchers automatically link future failing test results to a defect
    when the test failure's error message or stack trace matches the
    provided regex patterns.

    At least one of ``message_regex`` or ``trace_regex`` must be
    supplied.

    Args:
        defect_id: Numeric ID of the parent defect.
        name: Short descriptive name for the matcher rule.
        message_regex: Regular expression matched against error messages
            of failing test results. Optional if trace_regex is given.
        trace_regex: Regular expression matched against stack traces of
            failing test results. Optional if message_regex is given.

    Returns:
        A success message with the created matcher ID.
    """
    async with AllureClient.from_env() as client:
        service = DefectService(client)
        matcher = await service.create_defect_matcher(
            defect_id=defect_id,
            name=name,
            message_regex=message_regex,
            trace_regex=trace_regex,
        )
        return f"Created Defect Matcher #{matcher.id}: '{matcher.name}' for Defect #{defect_id}"


async def update_defect_matcher(
    matcher_id: Annotated[int, "ID of the matcher to update"],
    name: Annotated[str | None, "New matcher name"] = None,
    message_regex: Annotated[str | None, "New message regex"] = None,
    trace_regex: Annotated[str | None, "New trace regex"] = None,
) -> str:
    """Update a defect matcher's name or regex patterns.

    At least one field must be provided.

    Args:
        matcher_id: Numeric ID of the matcher to update.
        name: New matcher name (optional).
        message_regex: New error message regex (optional).
        trace_regex: New stack trace regex (optional).

    Returns:
        A success message with the updated matcher ID.
    """
    async with AllureClient.from_env() as client:
        service = DefectService(client)
        matcher = await service.update_defect_matcher(
            matcher_id=matcher_id,
            name=name,
            message_regex=message_regex,
            trace_regex=trace_regex,
        )
        return f"Updated Defect Matcher #{matcher.id}: '{matcher.name}'"


async def delete_defect_matcher(
    matcher_id: Annotated[int, "ID of the matcher to delete"],
    confirm: Annotated[
        bool,
        "Safety flag — must be set to true to confirm deletion",
    ] = False,
) -> str:
    """Permanently delete a defect matcher (automation rule).

    This is a destructive operation. The ``confirm`` parameter must be
    set to ``true`` to actually perform the deletion.

    Args:
        matcher_id: Numeric ID of the matcher to delete.
        confirm: Must be explicitly set to true. Prevents accidental
            deletion when the agent misinterprets the user's intent.

    Returns:
        Confirmation or rejection message.
    """
    if not confirm:
        return f"Deletion aborted. Set confirm=true to permanently delete Defect Matcher #{matcher_id}."
    async with AllureClient.from_env() as client:
        service = DefectService(client)
        await service.delete_defect_matcher(matcher_id)
        return f"Deleted Defect Matcher #{matcher_id}"


async def list_defect_matchers(
    defect_id: Annotated[int, "ID of the parent defect"],
) -> str:
    """List all matchers (automation rules) for a given defect.

    Args:
        defect_id: Numeric ID of the parent defect.

    Returns:
        Formatted list of matchers with names and regex patterns.
    """
    async with AllureClient.from_env() as client:
        service = DefectService(client)
        matchers = await service.list_defect_matchers(defect_id)
        if not matchers:
            return f"No matchers found for Defect #{defect_id}."
        lines: list[str] = [f"Found {len(matchers)} matcher(s) for Defect #{defect_id}:"]
        for m in matchers:
            parts = [f"  • #{m.id}: {m.name}"]
            if m.message_regex:
                parts.append(f"    message: {m.message_regex}")
            if m.trace_regex:
                parts.append(f"    trace: {m.trace_regex}")
            lines.extend(parts)
        return "\n".join(lines)
