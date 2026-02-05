"""Launch management tools."""

from typing import Annotated

from pydantic import Field

from src.client import AllureClient
from src.services.launch_service import LaunchListResult, LaunchService
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

    return f"✅ Launch created successfully! ID: {launch.id}, Name: {launch.name}"


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
) -> str:
    """List launches in a project.

    Args:
        page: Zero-based page index.
        size: Number of results per page (max 100).
        search: Optional name search.
        filter_id: Optional filter ID.
        sort: Optional sort criteria.
        project_id: Optional override for the default Project ID.

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

    return _format_launch_list(result)


async def get_launch(
    launch_id: Annotated[int, Field(description="Launch ID (required).")],
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
) -> str:
    """Retrieve a specific launch and summarize its details.

    Args:
        launch_id: The unique ID of the launch.
        project_id: Optional override for the default Project ID.

    Returns:
        LLM-friendly summary of the launch details.
    """
    auth_context = get_auth_context(project_id=project_id)
    project = auth_context.project_id or settings.ALLURE_PROJECT_ID
    if project is None:
        raise ValueError("Project ID is required to retrieve launch details")

    async with AllureClient(
        base_url=settings.ALLURE_ENDPOINT,
        token=auth_context.api_token,
        project=project,
    ) as client:
        service = LaunchService(client=client)
        launch = await service.get_launch(launch_id)

    return _format_launch_detail(launch)


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
    lines.append(f"- ID: {launch_id if launch_id is not None else 'unknown'}")
    lines.append(f"- Name: {name}")
    lines.append(f"- Status: {status}")

    started_at = getattr(launch, "created_date", None) or getattr(launch, "createdDate", None)
    ended_at = getattr(launch, "last_modified_date", None) or getattr(launch, "lastModifiedDate", None)

    if started_at is not None:
        lines.append(f"- Started: {started_at}")
    if ended_at is not None:
        lines.append(f"- Ended: {ended_at}")

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
        if value is None:
            continue
        if label in seen_labels:
            continue
        lines.append(f"- {label}: {value}")
        seen_labels.add(label)

    statistic = getattr(launch, "statistic", None)
    if statistic:
        summary_parts: list[str] = []
        for item in statistic:
            status_label = getattr(item, "status", None)
            count = getattr(item, "count", None)
            if status_label is None or count is None:
                continue
            summary_parts.append(f"{status_label!s}={count}")
        if summary_parts:
            lines.append(f"- Summary: {', '.join(summary_parts)}")

    return "\n".join(lines)
