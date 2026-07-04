"""Launch management tools."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.launch_service import (
    AttachmentUploadResult,
    LaunchDeleteResult,
    LaunchListResult,
    LaunchService,
    LaunchTestResultListResult,
    ManualRerunResult,
    ManualTestSessionResult,
    ManualTestSubmissionResult,
)
from src.tools.output_contract import DEFAULT_OUTPUT_FORMAT, OutputFormat, ToolOutput, render_output
from src.utils.auth_resolution import resolve_auth_settings
from src.utils.links import launch_url


async def create_launch(
    name: Annotated[str, Field(description="Launch name (required).")],
    autoclose: Annotated[bool | None, Field(description="Whether the launch auto-closes.")] = None,
    external: Annotated[bool | None, Field(description="Whether the launch is external.")] = None,
    issues: Annotated[
        list[dict[str, object]] | None,
        Field(description="Optional list of issue dictionaries."),
    ] = None,
    links: Annotated[
        list[dict[str, str]] | None,
        Field(description="Optional list of external links (name, url, type)."),
    ] = None,
    tags: Annotated[list[str] | None, Field(description="Optional list of tags.")] = None,
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """Create a new launch in Allure TestOps.

    Args:
        name: Launch name.
        autoclose: Whether the launch auto-closes.
        external: Whether the launch is external.
        issues: Optional list of issue dictionaries.
        links: Optional list of external link dictionaries.
        tags: Optional list of launch tags.
        project_id: Optional override for the default Project ID.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        Confirmation message with launch ID and name.
    """
    async with AllureClient.from_env(project=project_id) as client:
        service = LaunchService(client=client)
        launch = await service.create_launch(
            name=name,
            autoclose=autoclose,
            external=external,
            issues=issues,
            links=links,
            tags=tags,
        )
        base_url = client.get_base_url()
        resolved_project_id = client.get_project()

    if launch.id is None:
        raise ValueError("Created launch is missing an ID")
    url = launch_url(base_url, resolved_project_id, launch.id)
    message = f"✅ Launch created successfully! ID: {launch.id}, Name: {launch.name}\nLaunch URL: {url}"
    return render_output(
        plain=message,
        json_payload=_launch_payload(launch, base_url=base_url, project_id=resolved_project_id),
        output_format=output_format,
    )


async def list_launches(
    page: Annotated[int, Field(description="Zero-based page index.")] = 0,
    size: Annotated[int, Field(description="Number of results per page (max 100).", le=100)] = 20,
    search: Annotated[str | None, Field(description="Optional name search.")] = None,
    filter_id: Annotated[int | None, Field(description="Optional filter ID.")] = None,
    sort: Annotated[
        list[str] | None,
        Field(description=("Sorting criteria in the format: property(,asc|desc). Example: ['createdDate,DESC']")),
    ] = None,
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """List launches in a project.

    Args:
        page: Zero-based page index.
        size: Number of results per page (max 100).
        search: Optional name search.
        filter_id: Optional filter ID.
        sort: Optional sort criteria.
        project_id: Optional override for the default Project ID.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        Formatted list of launches with pagination info.
    """
    async with AllureClient.from_env(project=project_id) as client:
        service = LaunchService(client=client)
        result = await service.list_launches(
            page=page,
            size=size,
            search=search,
            filter_id=filter_id,
            sort=sort,
        )
        base_url = client.get_base_url()
        resolved_project_id = client.get_project()

    items = [_launch_payload(launch, base_url=base_url, project_id=resolved_project_id) for launch in result.items]
    return render_output(
        plain=_format_launch_list(result, base_url=base_url, project_id=resolved_project_id),
        json_payload={
            "total": result.total,
            "page": result.page,
            "size": result.size,
            "total_pages": result.total_pages,
            "items": items,
        },
        output_format=output_format,
    )


async def get_launch(
    launch_id: Annotated[int, Field(description="Launch ID (required).")],
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """Retrieve a specific launch and summarize its details.

    Args:
        launch_id: The unique ID of the launch.
        project_id: Optional override for the default Project ID.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        LLM-friendly summary of the launch details.
    """
    async with _launch_client_context(project_id=project_id) as client:
        service = LaunchService(client=client)
        launch = await service.get_launch(launch_id)
        base_url = client.get_base_url()
        resolved_project_id = client.get_project()

    return render_output(
        plain=_format_launch_detail(launch, base_url=base_url, project_id=resolved_project_id),
        json_payload=_launch_payload(launch, base_url=base_url, project_id=resolved_project_id),
        output_format=output_format,
    )


async def list_launch_test_results(
    launch_id: Annotated[int, Field(description="Launch ID (required).")],
    manual_only: Annotated[
        bool,
        Field(description="When true, return only manual results. Filtering is handled for you."),
    ] = False,
    failed_only: Annotated[
        bool,
        Field(description="When true, return only failed or broken results. Filtering is handled for you."),
    ] = False,
    page: Annotated[int, Field(description="Zero-based page index after optional filtering.")] = 0,
    size: Annotated[int, Field(description="Number of results per page (max 100).", le=100)] = 20,
    search: Annotated[str | None, Field(description="Optional result-name search term.")] = None,
    filter_id: Annotated[int | None, Field(description="Optional saved filter ID from TestOps.")] = None,
    sort: Annotated[
        list[str] | None,
        Field(description="Optional sort directives such as ['name,ASC'] or ['createdDate,DESC']."),
    ] = None,
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """List test results inside a launch, including manual execution metadata.

    Args:
        launch_id: Launch ID.
        manual_only: Restrict results to manual tests.
        failed_only: Restrict results to failed/broken tests.
        page: Zero-based page index after optional filtering.
        size: Number of results per page.
        search: Optional result-name search term.
        filter_id: Optional saved filter ID.
        sort: Optional sort directives.
        project_id: Optional override for the default Project ID.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        Launch result summaries with result IDs, test case IDs, statuses, and assignee/tester fields.
    """
    async with _launch_client_context(project_id=project_id) as client:
        service = LaunchService(client=client)
        result = await service.list_launch_test_results(
            launch_id,
            page=page,
            size=size,
            search=search,
            filter_id=filter_id,
            sort=sort,
            manual_only=manual_only,
            failed_only=failed_only,
        )

    items = [
        {
            "result_id": item.result_id,
            "test_case_id": item.test_case_id,
            "name": item.name,
            "manual": item.manual,
            "status": item.status,
            "assignee": item.assignee,
            "tested_by": item.tested_by,
        }
        for item in result.items
    ]
    return render_output(
        plain=_format_launch_test_result_list(result),
        json_payload={
            "launch_id": launch_id,
            "manual_only": manual_only,
            "failed_only": failed_only,
            "total": result.total,
            "page": result.page,
            "size": result.size,
            "total_pages": result.total_pages,
            "items": items,
        },
        output_format=output_format,
    )


async def rerun_test_results_manually(
    launch_id: Annotated[int, Field(description="Launch ID containing the failed results (required).")],
    result_ids: Annotated[
        list[int],
        Field(description="One or more launch result IDs to schedule for manual rerun."),
    ],
    assignees: Annotated[
        list[str] | None,
        Field(description="Optional usernames to assign during manual rerun scheduling."),
    ] = None,
    force_manual: Annotated[
        bool,
        Field(description="Force manual rerun mode when the upstream API supports it."),
    ] = True,
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """Schedule manual reruns for selected launch results.

    Args:
        launch_id: Launch ID.
        result_ids: Selected result IDs to rerun.
        assignees: Optional usernames to assign.
        force_manual: Force manual rerun mode.
        project_id: Optional override for the default Project ID.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        Confirmation that manual reruns were scheduled.
    """
    async with _launch_client_context(project_id=project_id) as client:
        service = LaunchService(client=client)
        result = await service.rerun_test_results_manually(
            launch_id,
            result_ids=result_ids,
            assignees=assignees,
            force_manual=force_manual,
        )

    return render_output(
        plain=_format_manual_rerun_result(result),
        json_payload={
            "launch_id": result.launch_id,
            "result_ids": result.result_ids,
            "scheduled_count": result.scheduled_count,
            "assignees": result.assignees,
            "force_manual": result.force_manual,
        },
        output_format=output_format,
    )


async def start_manual_test_session(
    launch_id: Annotated[int, Field(description="Launch ID (required).")],
    environment: Annotated[
        list[dict[str, str]] | None,
        Field(description="Optional environment variables as [{key, value}, ...]."),
    ] = None,
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """Start a manual execution session for a launch.

    Args:
        launch_id: Launch ID.
        environment: Optional environment key/value pairs.
        project_id: Optional override for the default Project ID.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        The manual test session ID required for result submission.
    """
    async with _launch_client_context(project_id=project_id) as client:
        service = LaunchService(client=client)
        result = await service.start_manual_test_session(launch_id, environment=environment)

    return render_output(
        plain=_format_manual_test_session_result(result),
        json_payload={
            "test_session_id": result.test_session_id,
            "launch_id": result.launch_id,
            "job_id": result.job_id,
            "job_run_id": result.job_run_id,
            "project_id": result.project_id,
            "environment": result.environment,
        },
        output_format=output_format,
    )


async def submit_manual_test_results(
    test_session_id: Annotated[int, Field(description="Manual test session ID (required).")],
    results: Annotated[
        list[dict[str, object]],
        Field(
            description=(
                "Manual result payloads. Each item must include test_case_id plus name or full_name, and may include "
                "status/start/stop/message/trace/description/precondition/expected_result/steps/parameters/"
                "uuid/history_id."
            )
        ),
    ],
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """Submit manual execution results for a manual session.

    Args:
        test_session_id: Manual test session ID.
        results: Manual result payloads. Each result must include `test_case_id` plus `name` or `full_name`.
        project_id: Optional override for the default Project ID.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        Created or updated test result IDs for follow-up actions.
    """
    async with _launch_client_context(project_id=project_id) as client:
        service = LaunchService(client=client)
        result = await service.submit_manual_test_results(test_session_id, results=results)

    return render_output(
        plain=_format_manual_test_submission_result(result),
        json_payload={
            "test_session_id": result.test_session_id,
            "result_ids": result.result_ids,
            "submitted_count": result.submitted_count,
        },
        output_format=output_format,
    )


async def add_test_result_attachment(
    test_result_id: Annotated[int, Field(description="Manual test result ID (required).")],
    attachment: Annotated[
        dict[str, str],
        Field(
            description=("Attachment payload using the repo-standard pattern: {name, content_type, content? | url?}.")
        ),
    ],
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """Upload evidence to a manual test result.

    Args:
        test_result_id: Manual test result ID.
        attachment: Attachment payload using content or url.
        project_id: Optional override for the default Project ID.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        Confirmation that the attachment was accepted for the result.
    """
    async with _launch_client_context(project_id=project_id) as client:
        service = LaunchService(client=client)
        result = await service.add_test_result_attachment(test_result_id, attachment=attachment)

    return render_output(
        plain=_format_attachment_upload_result(result),
        json_payload={
            "target_kind": result.target_kind,
            "target_id": result.target_id,
            "file_names": result.file_names,
            "status_code": result.status_code,
        },
        output_format=output_format,
    )


async def add_test_step_attachment(
    test_result_id: Annotated[int, Field(description="Parent test result ID (required).")],
    attachment: Annotated[
        dict[str, str],
        Field(
            description=("Attachment payload using the repo-standard pattern: {name, content_type, content? | url?}.")
        ),
    ],
    attachment_id: Annotated[
        int | None,
        Field(description="Optional explicit manual step attachment ID resolved from the test result execution."),
    ] = None,
    step_name: Annotated[
        str | None,
        Field(description="Optional attachment-step name to resolve within the manual test result."),
    ] = None,
    step_index: Annotated[
        int | None,
        Field(description="Optional zero-based manual step index to resolve within the test result execution."),
    ] = None,
    fixture_result_id: Annotated[
        int | None,
        Field(description="Optional explicit fixture result ID for legacy fixture-step fallback."),
    ] = None,
    fixture_name: Annotated[
        str | None,
        Field(description="Optional fixture name used only for the legacy fixture-step fallback."),
    ] = None,
    fixture_type: Annotated[
        str | None,
        Field(description="Optional fixture type hint for the legacy fixture-step fallback: 'before' or 'after'."),
    ] = None,
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """Upload evidence to a manual attachment step inside a test result.

    Args:
        test_result_id: Parent test result ID.
        attachment: Attachment payload using content or url.
        attachment_id: Optional explicit manual step attachment ID.
        step_name: Optional attachment-step name to resolve within the result execution.
        step_index: Optional zero-based step index to resolve within the result execution.
        fixture_result_id: Optional explicit fixture result ID for legacy fallback.
        fixture_name: Optional fixture name for legacy fallback.
        fixture_type: Optional fixture type hint ('before' or 'after') for legacy fallback.
        project_id: Optional override for the default Project ID.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        Confirmation that the attachment was accepted for the manual step context.
    """
    normalized_fixture_type = fixture_type.lower() if isinstance(fixture_type, str) else None
    async with _launch_client_context(project_id=project_id) as client:
        service = LaunchService(client=client)
        result = await service.add_test_step_attachment(
            test_result_id=test_result_id,
            attachment=attachment,
            attachment_id=attachment_id,
            step_name=step_name,
            step_index=step_index,
            fixture_result_id=fixture_result_id,
            fixture_name=fixture_name,
            fixture_type=normalized_fixture_type,  # type: ignore[arg-type]
        )

    return render_output(
        plain=_format_attachment_upload_result(result),
        json_payload={
            "target_kind": result.target_kind,
            "target_id": result.target_id,
            "file_names": result.file_names,
            "status_code": result.status_code,
        },
        output_format=output_format,
    )


async def delete_launch(
    launch_id: Annotated[int, Field(description="Launch ID to delete/archive (required).")],
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """Delete/archive a launch by ID.
    ⚠️ CAUTION: Destructive.

    Args:
        launch_id: The unique ID of the launch to archive.
        project_id: Optional override for the default Project ID.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        Confirmation message with launch ID and idempotent status.
    """
    async with _launch_client_context(project_id=project_id) as client:
        service = LaunchService(client=client)
        result = await service.delete_launch(launch_id)
        base_url = client.get_base_url()
        resolved_project_id = client.get_project()
        url = launch_url(base_url, resolved_project_id, result.launch_id)

    return render_output(
        plain=f"{_format_launch_delete(result)}\nLaunch URL: {url}",
        json_payload={
            "launch_id": result.launch_id,
            "name": result.name,
            "status": result.status,
            "message": result.message,
            "url": url,
        },
        output_format=output_format,
    )


async def close_launch(
    launch_id: Annotated[int, Field(description="Launch ID (required).")],
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    api_token: Annotated[str | None, Field(description="Optional runtime API token override.")] = None,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """Close a launch and return updated launch details.

    Args:
        launch_id: The unique ID of the launch.
        project_id: Optional override for the default Project ID.
        api_token: Optional runtime API token override.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        LLM-friendly summary of the closed launch.
    """
    async with _launch_client_context(project_id=project_id, api_token=api_token) as client:
        service = LaunchService(client=client)
        launch = await service.close_launch(launch_id)
        base_url = client.get_base_url()
        resolved_project_id = client.get_project()

    message = (
        f"Launch closed successfully.\n"
        f"{_format_launch_detail(launch, base_url=base_url, project_id=resolved_project_id)}"
    )
    payload = _launch_payload(launch, base_url=base_url, project_id=resolved_project_id)
    payload["operation"] = "closed"
    return render_output(
        plain=message,
        json_payload=payload,
        output_format=output_format,
    )


async def reopen_launch(
    launch_id: Annotated[int, Field(description="Launch ID (required).")],
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    api_token: Annotated[str | None, Field(description="Optional runtime API token override.")] = None,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """Reopen a launch and return updated launch details.

    Args:
        launch_id: The unique ID of the launch.
        project_id: Optional override for the default Project ID.
        api_token: Optional runtime API token override.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        LLM-friendly summary of the reopened launch.
    """
    async with _launch_client_context(project_id=project_id, api_token=api_token) as client:
        service = LaunchService(client=client)
        launch = await service.reopen_launch(launch_id)
        base_url = client.get_base_url()
        resolved_project_id = client.get_project()

    message = (
        f"Launch reopened successfully.\n"
        f"{_format_launch_detail(launch, base_url=base_url, project_id=resolved_project_id)}"
    )
    payload = _launch_payload(launch, base_url=base_url, project_id=resolved_project_id)
    payload["operation"] = "reopened"
    return render_output(
        plain=message,
        json_payload=payload,
        output_format=output_format,
    )


def _launch_payload(launch: object, *, base_url: str, project_id: int) -> dict[str, object]:
    launch_id = getattr(launch, "id", None)
    payload: dict[str, object] = {
        "id": launch_id,
        "name": getattr(launch, "name", None),
        "closed": getattr(launch, "closed", None),
        "created_date": getattr(launch, "created_date", None) or getattr(launch, "createdDate", None),
        "last_modified_date": getattr(launch, "last_modified_date", None) or getattr(launch, "lastModifiedDate", None),
        "project_id": getattr(launch, "project_id", None) or getattr(launch, "projectId", None),
        "autoclose": getattr(launch, "autoclose", None),
        "external": getattr(launch, "external", None),
        "known_defects_count": getattr(launch, "known_defects_count", None)
        or getattr(launch, "knownDefectsCount", None),
        "new_defects_count": getattr(launch, "new_defects_count", None) or getattr(launch, "newDefectsCount", None),
        "manual_execution_guidance": (
            "Use list_launch_test_results for result-level manual execution work, "
            "then start_manual_test_session and submit_manual_test_results for interactive updates."
        ),
    }
    if isinstance(launch_id, int):
        payload["url"] = launch_url(base_url, project_id, launch_id)
    return payload


@asynccontextmanager
async def _launch_client_context(
    *,
    project_id: int | None = None,
    api_token: str | None = None,
) -> AsyncIterator[AllureClient]:
    resolved = resolve_auth_settings(api_token=api_token, project_id=project_id)
    if not resolved.endpoint:
        raise ValueError("ALLURE_ENDPOINT is required for launch operations")
    if resolved.api_token is None:
        raise ValueError("ALLURE_API_TOKEN is required for launch operations")
    if resolved.project_id is None:
        raise ValueError("Project ID is required for launch operations")

    async with AllureClient(
        base_url=resolved.endpoint,
        token=resolved.api_token,
        project=resolved.project_id,
    ) as client:
        yield client


def _format_launch_list(result: LaunchListResult, *, base_url: str, project_id: int) -> str:
    if not result.items:
        return "No launches found in this project."

    lines = [f"Found {result.total} launches (page {result.page + 1} of {result.total_pages}):"]

    for launch in result.items:
        name = getattr(launch, "name", None) or "(unnamed)"
        launch_id = getattr(launch, "id", None)
        created_date = getattr(launch, "created_date", None) or getattr(launch, "createdDate", None)
        closed = getattr(launch, "closed", None)

        status = "closed" if closed else "open"
        created = f"created: {created_date}" if created_date is not None else "created: unknown"
        launch_id_text = str(launch_id) if launch_id is not None else "unknown"

        lines.append(f"- [#{launch_id_text}] {name} ({status}; {created})")
        if isinstance(launch_id, int):
            lines.append(f"  Launch URL: {launch_url(base_url, project_id, launch_id)}")

    if result.page < result.total_pages - 1:
        lines.append(f"\nUse page={result.page + 1} to see more results.")

    return "\n".join(lines)


def _format_launch_detail(launch: object, *, base_url: str, project_id: int) -> str:
    launch_id = getattr(launch, "id", None)
    name = getattr(launch, "name", None) or "(unnamed)"
    closed = getattr(launch, "closed", None)
    status = "closed" if closed else "open"

    lines = ["Launch details:"]
    _append_close_report_line(lines, launch)
    lines.append(f"- ID: {launch_id if launch_id is not None else 'unknown'}")
    if isinstance(launch_id, int):
        lines.append(f"- URL: {launch_url(base_url, project_id, launch_id)}")
    lines.append(f"- Name: {name}")
    lines.append(f"- Status: {status}")

    _append_timing_lines(lines, launch)
    _append_metadata_lines(lines, launch)
    _append_statistic_lines(lines, launch)
    lines.append(
        "- Manual execution: use list_launch_test_results for result discovery, "
        "then start_manual_test_session and submit_manual_test_results."
    )

    return "\n".join(lines)


def _append_close_report_line(lines: list[str], launch: object) -> None:
    close_report_generation = getattr(launch, "close_report_generation", None)
    if close_report_generation is not None:
        lines.append(f"- Close report generation: {close_report_generation}")


def _append_timing_lines(lines: list[str], launch: object) -> None:
    started_at = getattr(launch, "created_date", None) or getattr(launch, "createdDate", None)
    ended_at = getattr(launch, "last_modified_date", None) or getattr(launch, "lastModifiedDate", None)

    if started_at is not None:
        lines.append(f"- Started: {started_at}")
    if ended_at is not None:
        lines.append(f"- Ended: {ended_at}")


def _append_metadata_lines(lines: list[str], launch: object) -> None:
    field_labels = [
        ("project_id", "Project ID"),
        ("projectId", "Project ID"),
        ("autoclose", "Autoclose"),
        ("external", "External"),
        ("known_defects_count", "Known defects"),
        ("knownDefectsCount", "Known defects"),
        ("new_defects_count", "New defects"),
        ("newDefectsCount", "New defects"),
    ]

    seen_labels: set[str] = set()
    for field_name, label in field_labels:
        value = getattr(launch, field_name, None)
        if value is None or label in seen_labels:
            continue
        lines.append(f"- {label}: {value}")
        seen_labels.add(label)


def _append_statistic_lines(lines: list[str], launch: object) -> None:
    statistic = getattr(launch, "statistic", None)
    if not statistic:
        return

    summary_parts: list[str] = []
    for item in statistic:
        status_label = getattr(item, "status", None)
        count = getattr(item, "count", None)
        if status_label is None or count is None:
            continue
        summary_parts.append(f"{status_label!s}={count}")

    if summary_parts:
        lines.append(f"- Summary: {', '.join(summary_parts)}")


def _format_launch_delete(result: LaunchDeleteResult) -> str:
    if result.status == "already_deleted":
        return f"ℹ️ Launch {result.launch_id} was already archived or doesn't exist."  # noqa: RUF001

    name_part = f": '{result.name}'" if result.name else ""
    return f"✅ Archived Launch {result.launch_id}{name_part}"


def _format_launch_test_result_list(result: LaunchTestResultListResult) -> str:
    if not result.items:
        return "No matching launch test results found."

    lines = [f"Found {result.total} launch test results (page {result.page + 1} of {result.total_pages}):"]
    for item in result.items:
        name = item.name or "(unnamed)"
        result_id = item.result_id if item.result_id is not None else "unknown"
        test_case_id = item.test_case_id if item.test_case_id is not None else "unknown"
        manual = "manual" if item.manual else "automated"
        status = item.status or "unknown"
        lines.append(f"- Result #{result_id}: {name} (test case #{test_case_id}; {manual}; status={status})")
        if item.assignee:
            lines.append(f"  Assignee: {item.assignee}")
        if item.tested_by:
            lines.append(f"  Tested by: {item.tested_by}")
    return "\n".join(lines)


def _format_manual_rerun_result(result: ManualRerunResult) -> str:
    lines = [
        f"Scheduled {result.scheduled_count} manual rerun(s) in launch {result.launch_id}.",
        f"Result IDs: {', '.join(str(result_id) for result_id in result.result_ids)}",
        f"Force manual: {result.force_manual}",
    ]
    if result.assignees:
        lines.append(f"Assignees: {', '.join(result.assignees)}")
    return "\n".join(lines)


def _format_manual_test_session_result(result: ManualTestSessionResult) -> str:
    lines = [
        f"Manual test session started successfully. Test session ID: {result.test_session_id}",
    ]
    if result.launch_id is not None:
        lines.append(f"Launch ID: {result.launch_id}")
    if result.job_id is not None:
        lines.append(f"Job ID: {result.job_id}")
    if result.job_run_id is not None:
        lines.append(f"Job run ID: {result.job_run_id}")
    if result.environment:
        rendered = ", ".join(f"{item.get('key')}={item.get('value')}" for item in result.environment)
        lines.append(f"Environment: {rendered}")
    return "\n".join(lines)


def _format_manual_test_submission_result(result: ManualTestSubmissionResult) -> str:
    lines = [
        f"Submitted {result.submitted_count} manual result payload(s) for test session {result.test_session_id}.",
    ]
    if result.result_ids:
        lines.append(f"Result IDs: {', '.join(str(result_id) for result_id in result.result_ids)}")
    else:
        lines.append("Result IDs were not returned by the API.")
    return "\n".join(lines)


def _format_attachment_upload_result(result: AttachmentUploadResult) -> str:
    file_names = ", ".join(result.file_names)
    return (
        f"Attachment upload accepted for {result.target_kind} {result.target_id}. "
        f"Files: {file_names}. HTTP status: {result.status_code}."
    )
