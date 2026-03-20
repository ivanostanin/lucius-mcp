"""Launch management tools."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.launch_service import LaunchDeleteResult, LaunchListResult, LaunchService
from src.tools.output_contract import DEFAULT_OUTPUT_FORMAT, OutputFormat, render_output
from src.utils.auth import get_auth_context
from src.utils.config import settings


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
    output_format: Annotated[OutputFormat, Field(description="Output format: 'plain' (default) or 'json'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> str:
    """Create a new launch in Allure TestOps.

    Args:
        name: Launch name.
        autoclose: Whether the launch auto-closes.
        external: Whether the launch is external.
        issues: Optional list of issue dictionaries.
        links: Optional list of external link dictionaries.
        tags: Optional list of launch tags.
        project_id: Optional override for the default Project ID.
        output_format: Output format: plain (default) or json.

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

    message = f"✅ Launch created successfully! ID: {launch.id}, Name: {launch.name}"
    return render_output(
        plain=message,
        json_payload=_launch_payload(launch),
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
    output_format: Annotated[OutputFormat, Field(description="Output format: 'plain' (default) or 'json'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> str:
    """List launches in a project.

    Args:
        page: Zero-based page index.
        size: Number of results per page (max 100).
        search: Optional name search.
        filter_id: Optional filter ID.
        sort: Optional sort criteria.
        project_id: Optional override for the default Project ID.
        output_format: Output format: plain (default) or json.

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

    items = [_launch_payload(launch) for launch in result.items]
    return render_output(
        plain=_format_launch_list(result),
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
    output_format: Annotated[OutputFormat, Field(description="Output format: 'plain' (default) or 'json'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> str:
    """Retrieve a specific launch and summarize its details.

    Args:
        launch_id: The unique ID of the launch.
        project_id: Optional override for the default Project ID.
        output_format: Output format: plain (default) or json.

    Returns:
        LLM-friendly summary of the launch details.
    """
    async with _launch_client_context(project_id=project_id) as client:
        service = LaunchService(client=client)
        launch = await service.get_launch(launch_id)

    return render_output(
        plain=_format_launch_detail(launch),
        json_payload=_launch_payload(launch),
        output_format=output_format,
    )


async def delete_launch(
    launch_id: Annotated[int, Field(description="Launch ID to delete/archive (required).")],
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    output_format: Annotated[OutputFormat, Field(description="Output format: 'plain' (default) or 'json'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> str:
    """Delete/archive a launch by ID.
    ⚠️ CAUTION: Destructive.

    Args:
        launch_id: The unique ID of the launch to archive.
        project_id: Optional override for the default Project ID.
        output_format: Output format: plain (default) or json.

    Returns:
        Confirmation message with launch ID and idempotent status.
    """
    async with _launch_client_context(project_id=project_id) as client:
        service = LaunchService(client=client)
        result = await service.delete_launch(launch_id)

    return render_output(
        plain=_format_launch_delete(result),
        json_payload={
            "launch_id": result.launch_id,
            "name": result.name,
            "status": result.status,
            "message": result.message,
        },
        output_format=output_format,
    )


async def close_launch(
    launch_id: Annotated[int, Field(description="Launch ID (required).")],
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    api_token: Annotated[str | None, Field(description="Optional runtime API token override.")] = None,
    output_format: Annotated[OutputFormat, Field(description="Output format: 'plain' (default) or 'json'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> str:
    """Close a launch and return updated launch details.

    Args:
        launch_id: The unique ID of the launch.
        project_id: Optional override for the default Project ID.
        api_token: Optional runtime API token override.
        output_format: Output format: plain (default) or json.

    Returns:
        LLM-friendly summary of the closed launch.
    """
    async with _launch_client_context(project_id=project_id, api_token=api_token) as client:
        service = LaunchService(client=client)
        launch = await service.close_launch(launch_id)

    message = f"Launch closed successfully.\n{_format_launch_detail(launch)}"
    payload = _launch_payload(launch)
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
    output_format: Annotated[OutputFormat, Field(description="Output format: 'plain' (default) or 'json'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> str:
    """Reopen a launch and return updated launch details.

    Args:
        launch_id: The unique ID of the launch.
        project_id: Optional override for the default Project ID.
        api_token: Optional runtime API token override.
        output_format: Output format: plain (default) or json.

    Returns:
        LLM-friendly summary of the reopened launch.
    """
    async with _launch_client_context(project_id=project_id, api_token=api_token) as client:
        service = LaunchService(client=client)
        launch = await service.reopen_launch(launch_id)

    message = f"Launch reopened successfully.\n{_format_launch_detail(launch)}"
    payload = _launch_payload(launch)
    payload["operation"] = "reopened"
    return render_output(
        plain=message,
        json_payload=payload,
        output_format=output_format,
    )


def _launch_payload(launch: object) -> dict[str, object]:
    return {
        "id": getattr(launch, "id", None),
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
    }


@asynccontextmanager
async def _launch_client_context(
    *,
    project_id: int | None = None,
    api_token: str | None = None,
) -> AsyncIterator[AllureClient]:
    if api_token is None:
        auth_context = get_auth_context(project_id=project_id)
    else:
        auth_context = get_auth_context(api_token=api_token, project_id=project_id)
    project = auth_context.project_id if auth_context.project_id is not None else settings.ALLURE_PROJECT_ID
    if project is None:
        raise ValueError("Project ID is required for launch operations")

    async with AllureClient(
        base_url=settings.ALLURE_ENDPOINT,
        token=auth_context.api_token,
        project=project,
    ) as client:
        yield client


def _format_launch_list(result: LaunchListResult) -> str:
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

    if result.page < result.total_pages - 1:
        lines.append(f"\nUse page={result.page + 1} to see more results.")

    return "\n".join(lines)


def _format_launch_detail(launch: object) -> str:
    launch_id = getattr(launch, "id", None)
    name = getattr(launch, "name", None) or "(unnamed)"
    closed = getattr(launch, "closed", None)
    status = "closed" if closed else "open"

    lines = ["Launch details:"]
    _append_close_report_line(lines, launch)
    lines.append(f"- ID: {launch_id if launch_id is not None else 'unknown'}")
    lines.append(f"- Name: {name}")
    lines.append(f"- Status: {status}")

    _append_timing_lines(lines, launch)
    _append_metadata_lines(lines, launch)
    _append_statistic_lines(lines, launch)

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
