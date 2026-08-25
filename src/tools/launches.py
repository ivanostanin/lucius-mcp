"""Launch management tools."""

import json
from collections.abc import AsyncIterator, Mapping, Sequence
from contextlib import asynccontextmanager
from dataclasses import asdict
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
from src.services.test_result_service import TestResultService
from src.tools.output_contract import DEFAULT_OUTPUT_FORMAT, OutputFormat, ToolOutput, render_output
from src.tools.output_schemas import (
    LaunchDetailOutput,
    LaunchMutationSummary,
    ListLaunchesOutput,
    TestResultDetailOutput,
    output_fields,
)
from src.utils.auth_resolution import resolve_auth_settings
from src.utils.links import launch_url

_COLLECTION_OUTPUT_FIELDS = ("items", "total", "page", "size", "total_pages")
_LAUNCH_OUTPUT_FIELDS = (
    "id",
    "name",
    "closed",
    "created_date",
    "last_modified_date",
    "project_id",
    "autoclose",
    "external",
    "known_defects_count",
    "new_defects_count",
    "manual_execution_guidance",
    "url",
    "operation",
)
_LAUNCH_DETAIL_OUTPUT_FIELDS = (
    "id",
    "name",
    "closed",
    "created_date",
    "last_modified_date",
    "project_id",
    "autoclose",
    "external",
    "created_by",
    "last_modified_by",
    "statistic",
    "known_defects_count",
    "new_defects_count",
    "environment",
    "jobs",
    "tags",
    "issues",
    "links",
    "manual_execution_guidance",
    "url",
)
_TEST_RUN_RESULT_OUTPUT_FIELDS = (
    "actual_launch_id",
    "test_result_id",
    "project_id",
    "result_url",
    "launch_url",
    "test_case",
    "core",
    "custom_fields",
    "environment",
    "members",
    "test_keys",
    "issues",
    "defects",
    "execution_steps",
    "fixtures",
    "result_attachments",
    "related_results",
    "partial",
    "unavailable_sections",
)


@output_fields(*_LAUNCH_OUTPUT_FIELDS, model=LaunchMutationSummary)
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
        json_payload=_launch_mutation_payload(launch, base_url=base_url, project_id=resolved_project_id),
        output_format=output_format,
    )


@output_fields("launch_id", "requested_count", "uploaded_count", "result_ids", "failures")
async def upload_test_results(
    launch_id: Annotated[int, Field(description="Launch ID to receive the results (required).")],
    results: Annotated[
        list[dict[str, object]],
        Field(
            description=(
                "Result objects to append to the launch. Every item requires test_case_id (int) and status "
                "(passed, failed, broken, skipped, or unknown). Optional fields: start, stop, duration, message, "
                "name, and full_name. A maximum of 1000 results is accepted per call."
            )
        ),
    ],
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """Upload external test results to an existing launch.

    Args:
        launch_id: Launch ID that receives all submitted results.
        results: Objects with required `test_case_id` and `status`; timestamps, duration, and a message are optional.
        project_id: Optional override for the default Project ID.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        A concise upload summary, including any rejected result indexes.
    """
    async with _launch_client_context(project_id=project_id) as client:
        service = LaunchService(client=client)
        result = await service.add_results(launch_id, results)

    plain = f"Successfully uploaded {result.uploaded_count} results to launch {result.launch_id}"
    if result.failures:
        rejected_indexes = ", ".join(str(failure.index) for failure in result.failures)
        plain = (
            f"Partially uploaded {result.uploaded_count} of {result.requested_count} results to launch "
            f"{result.launch_id}; rejected result indexes: {rejected_indexes}"
        )

    return render_output(
        plain=plain,
        json_payload={
            "launch_id": result.launch_id,
            "requested_count": result.requested_count,
            "uploaded_count": result.uploaded_count,
            "result_ids": result.result_ids,
            "failures": [{"index": failure.index, "message": failure.message} for failure in result.failures],
        },
        output_format=output_format,
    )


@output_fields(*_COLLECTION_OUTPUT_FIELDS, model=ListLaunchesOutput)
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

    items = [
        _compact_launch_payload(launch, base_url=base_url, project_id=resolved_project_id) for launch in result.items
    ]
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


@output_fields(*_LAUNCH_DETAIL_OUTPUT_FIELDS, model=LaunchDetailOutput)
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
        json_payload=_launch_detail_payload(launch, base_url=base_url, project_id=resolved_project_id),
        output_format=output_format,
    )


@output_fields("launch_id", "manual_only", "failed_only", *_COLLECTION_OUTPUT_FIELDS)
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


@output_fields(*_TEST_RUN_RESULT_OUTPUT_FIELDS, model=TestResultDetailOutput)
async def get_test_result(
    test_result_id: Annotated[
        int,
        Field(description="Exact Test Result ID from the /tree/{test_result_id} URL path; ignore treeId query state."),
    ],
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    output_format: Annotated[
        OutputFormat | None, Field(description="Output format: 'json' (default) or plain agent-readable detail.")
    ] = DEFAULT_OUTPUT_FORMAT,
) -> ToolOutput:
    """Retrieve one complete TestOps result without recursively reading related results.

    Args:
        test_result_id: Exact TestOps result ID matching ``/api/testresult/{id}``.
            Ignore a ``treeId`` URL query parameter.
        project_id: Optional project override.
        output_format: Structured JSON (default) or plain agent-readable detail.

    Returns:
        Curated result detail, authenticated attachment download paths, and explicit partial-data diagnostics.
    """
    async with _launch_client_context(project_id=project_id) as client:
        result = await TestResultService(client).get_test_result(test_result_id)

    payload = _normalize_result_payload(asdict(result))
    return render_output(
        plain=_format_test_result(payload),
        json_payload=payload,
        output_format=output_format,
    )


@output_fields("launch_id", "result_ids", "scheduled_count", "assignees", "force_manual")
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
        Confirmation that manual reruns were scheduled. Refresh launch results after rerun,
        because TestOps creates a new active placeholder result for the next execution phase.
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


@output_fields("test_session_id", "launch_id", "job_id", "job_run_id", "project_id", "environment")
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
        The manual test session ID retained for launch-manual workflow compatibility.
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


@output_fields("test_session_id", "result_ids", "submitted_count")
async def submit_manual_test_results(
    test_session_id: Annotated[int, Field(description="Manual test session ID (required).")],
    results: Annotated[
        list[dict[str, object]],
        Field(
            description=(
                "Manual result payloads. When an item includes result_id from list_launch_test_results, the service "
                "resolves that existing launch result in place through TestOps' test-result run controller. After "
                "rerun_test_results_manually, re-list launch results and submit against the newly visible active "
                "result for that test case. The returned result_ids are the resolved result IDs to use for follow-up "
                "attachments and reads. As a lower-level fallback, you may still provide launch_id + test_case_id + "
                "name/full_name explicitly to create a standalone manual result. Optional fields include "
                "status/start/stop/duration/message/trace/description/precondition/expected_result/steps."
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
        results: Manual result payloads. Prefer `result_id` from `list_launch_test_results` for launch-managed flows.
            The service resolves those existing results in place and returns their IDs for follow-up actions.
        project_id: Optional override for the default Project ID.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        Resolved or created test result IDs for follow-up actions such as attachment upload.
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


@output_fields("target_kind", "target_id", "file_names", "status_code")
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
        test_result_id: Manual test result ID. In rerun workflows, use the resolved result ID
            returned by the latest submit_manual_test_results call.
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


@output_fields("target_kind", "target_id", "file_names", "status_code")
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
        test_result_id: Parent test result ID. In rerun workflows, use the completed result ID
            returned by the latest submit_manual_test_results call.
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


@output_fields("launch_id", "status", "message")
async def delete_launch(
    launch_id: Annotated[int, Field(description="Launch ID to delete (required).")],
    project_id: Annotated[int | None, Field(description="Optional override for the default Project ID.")] = None,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """Delete a launch by ID.
    ⚠️ CAUTION: Destructive.

    Args:
        launch_id: The unique ID of the launch to delete.
        project_id: Optional override for the default Project ID.
        output_format: Output format: 'json' (default) or 'plain'.

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
            "status": result.status,
            "message": result.message,
        },
        output_format=output_format,
    )


@output_fields(*_LAUNCH_OUTPUT_FIELDS, model=LaunchMutationSummary)
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
    payload = _launch_mutation_payload(launch, base_url=base_url, project_id=resolved_project_id)
    payload["operation"] = "closed"
    return render_output(
        plain=message,
        json_payload=payload,
        output_format=output_format,
    )


@output_fields(*_LAUNCH_OUTPUT_FIELDS, model=LaunchMutationSummary)
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
    payload = _launch_mutation_payload(launch, base_url=base_url, project_id=resolved_project_id)
    payload["operation"] = "reopened"
    return render_output(
        plain=message,
        json_payload=payload,
        output_format=output_format,
    )


_MANUAL_EXECUTION_GUIDANCE = (
    "Use list_launch_test_results for result-level manual execution work, "
    "then submit_manual_test_results with result_id to resolve the existing launch result in place. "
    "After rerun_test_results_manually, refresh result discovery and use the resolved result IDs for attachments."
)


def _value(launch: object, snake_case: str, camel_case: str | None = None) -> object | None:
    """Read a value without treating valid zero or false values as missing."""
    value = getattr(launch, snake_case, None)
    if value is not None or camel_case is None:
        return value
    return getattr(launch, camel_case, None)


def _compact_launch_payload(launch: object, *, base_url: str, project_id: int) -> dict[str, object]:
    launch_id = getattr(launch, "id", None)
    payload: dict[str, object] = {
        "id": launch_id,
        "name": getattr(launch, "name", None),
        "closed": getattr(launch, "closed", None),
        "created_date": _value(launch, "created_date", "createdDate"),
        "last_modified_date": _value(launch, "last_modified_date", "lastModifiedDate"),
        "project_id": _value(launch, "project_id", "projectId"),
        "autoclose": getattr(launch, "autoclose", None),
        "external": getattr(launch, "external", None),
    }
    if isinstance(launch_id, int):
        payload["url"] = launch_url(base_url, project_id, launch_id)
    return payload


def _launch_mutation_payload(launch: object, *, base_url: str, project_id: int) -> dict[str, object]:
    """Keep create/close/reopen output stable while list and detail contracts diverge."""
    payload = _compact_launch_payload(launch, base_url=base_url, project_id=project_id)
    payload["known_defects_count"] = _value(launch, "known_defects_count", "knownDefectsCount")
    payload["new_defects_count"] = _value(launch, "new_defects_count", "newDefectsCount")
    payload["manual_execution_guidance"] = _MANUAL_EXECUTION_GUIDANCE
    return payload


def _launch_detail_payload(launch: object, *, base_url: str, project_id: int) -> dict[str, object]:
    payload = _compact_launch_payload(launch, base_url=base_url, project_id=project_id)
    payload.update(
        {
            "created_by": _value(launch, "created_by", "createdBy"),
            "last_modified_by": _value(launch, "last_modified_by", "lastModifiedBy"),
            "statistic": _statistic_payload(getattr(launch, "statistic", None)),
            "known_defects_count": _value(launch, "known_defects_count", "knownDefectsCount"),
            "new_defects_count": _value(launch, "new_defects_count", "newDefectsCount"),
            "environment": _environment_payload(getattr(launch, "environment", None)),
            "jobs": _jobs_payload(getattr(launch, "jobs", None)),
            "tags": _tags_payload(getattr(launch, "tags", None)),
            "issues": _issues_payload(getattr(launch, "issues", None)),
            "links": _links_payload(getattr(launch, "links", None)),
            "manual_execution_guidance": _MANUAL_EXECUTION_GUIDANCE,
        }
    )
    return payload


def _as_text(value: object | None) -> str | None:
    if value is None:
        return None
    raw_value = getattr(value, "value", value)
    return raw_value if isinstance(raw_value, str) else str(raw_value)


def _statistic_payload(items: Sequence[object] | None) -> list[dict[str, object]] | None:
    if items is None:
        return None
    return [
        {"status": _as_text(getattr(item, "status", None)), "count": getattr(item, "count", None)} for item in items
    ]


def _environment_payload(items: Sequence[object] | None) -> list[dict[str, object]] | None:
    if items is None:
        return None
    return [
        {
            "id": getattr(item, "id", None),
            "name": getattr(item, "name", None),
            "variable": (
                {"id": getattr(variable, "id", None), "name": getattr(variable, "name", None)}
                if (variable := getattr(item, "variable", None)) is not None
                else None
            ),
        }
        for item in items
    ]


def _jobs_payload(items: Sequence[object] | None) -> list[dict[str, object]] | None:
    if items is None:
        return None
    return [
        {
            "id": getattr(item, "id", None),
            "name": getattr(item, "name", None),
            "status": _as_text(getattr(item, "status", None)),
            "stage": _as_text(getattr(item, "stage", None)),
            "url": getattr(item, "url", None),
            "error_message": _value(item, "error_message", "errorMessage"),
            "external_id": _value(item, "external_id", "externalId"),
            "job": (
                {
                    "id": getattr(job, "id", None),
                    "name": getattr(job, "name", None),
                    "type": _as_text(getattr(job, "type", None)),
                    "url": getattr(job, "url", None),
                }
                if (job := getattr(item, "job", None)) is not None
                else None
            ),
        }
        for item in items
    ]


def _tags_payload(items: Sequence[object] | None) -> list[dict[str, object]] | None:
    return (
        None
        if items is None
        else [{"id": getattr(item, "id", None), "name": getattr(item, "name", None)} for item in items]
    )


def _issues_payload(items: Sequence[object] | None) -> list[dict[str, object]] | None:
    if items is None:
        return None
    return [
        {
            "id": getattr(item, "id", None),
            "name": getattr(item, "name", None),
            "display_name": _value(item, "display_name", "displayName"),
            "status": getattr(item, "status", None),
            "summary": getattr(item, "summary", None),
            "url": getattr(item, "url", None),
            "closed": getattr(item, "closed", None),
        }
        for item in items
    ]


def _links_payload(items: Sequence[object] | None) -> list[dict[str, object]] | None:
    if items is None:
        return None
    return [
        {"name": getattr(item, "name", None), "type": getattr(item, "type", None), "url": getattr(item, "url", None)}
        for item in items
    ]


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
        created_date = _value(launch, "created_date", "createdDate")
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
    _append_rich_detail_lines(lines, launch)
    lines.append(
        "- Manual execution: use list_launch_test_results for result discovery, "
        "then submit_manual_test_results with result_id to resolve the existing launch result in place. "
        "After rerun_test_results_manually, refresh result discovery and attach evidence to the "
        "resolved result IDs returned by the latest submission."
    )

    return "\n".join(lines)


def _format_test_result(payload: dict[str, object]) -> str:
    """Render every published field so plain and structured output stay equivalent."""
    return "Test result:\n" + json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)


def _normalize_result_payload(value: object) -> dict[str, object]:
    """Convert immutable service collections to JSON-shaped lists before strict output validation."""
    normalized = _normalize_payload_value(value)
    if not isinstance(normalized, dict):  # pragma: no cover - detail output is always an object root
        raise TypeError("Test-result output must be an object")
    return normalized


def _normalize_payload_value(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _normalize_payload_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize_payload_value(item) for item in value]
    return value


def _count_payload_items(value: object) -> int:
    return len(value) if isinstance(value, (list, tuple)) else 0


def _append_close_report_line(lines: list[str], launch: object) -> None:
    close_report_generation = getattr(launch, "close_report_generation", None)
    if close_report_generation is not None:
        lines.append(f"- Close report generation: {close_report_generation}")


def _append_timing_lines(lines: list[str], launch: object) -> None:
    started_at = _value(launch, "created_date", "createdDate")
    ended_at = _value(launch, "last_modified_date", "lastModifiedDate")

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
    if statistic is None:
        return
    if not statistic:
        lines.append("- Summary: []")
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


def _append_rich_detail_lines(lines: list[str], launch: object) -> None:
    """Render every rich detail projection in plain mode as well as JSON mode."""
    payload = _launch_detail_payload(launch, base_url="", project_id=0)
    labels = {
        "created_by": "Created by",
        "last_modified_by": "Last modified by",
        "environment": "Environment",
        "jobs": "Jobs",
        "tags": "Tags",
        "issues": "Issues",
        "links": "Links",
    }
    for field, label in labels.items():
        value = payload[field]
        if value is not None:
            lines.append(f"- {label}: {json.dumps(value, sort_keys=True)}")


def _format_launch_delete(result: LaunchDeleteResult) -> str:
    if result.status == "already_deleted":
        return f"ℹ️ Launch {result.launch_id} was already deleted or doesn't exist."  # noqa: RUF001

    return f"✅ Deleted Launch {result.launch_id}"


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
