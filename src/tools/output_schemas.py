"""Pydantic response models published as Lucius MCP output schemas.

These models intentionally describe Lucius's agent-facing response envelopes,
rather than the generated Allure API client DTOs.  Each registered tool owns a
concrete object-root model so the MCP manifest remains stable as upstream API
models evolve.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar, cast

from pydantic import BaseModel, ConfigDict, Field, create_model

ToolFnT = TypeVar("ToolFnT", bound=Callable[..., Any])
ToolFn = Callable[..., Any]
_OUTPUT_FIELDS_ATTRIBUTE = "__lucius_output_fields__"
_OUTPUT_MODEL_ATTRIBUTE = "__lucius_output_model__"


def output_fields(
    *field_names: str,
    model: type[BaseModel] | None = None,
) -> Callable[[ToolFnT], ToolFnT]:
    """Attach an MCP output contract to a tool at its definition site.

    This module deliberately does not import ``src.tools``: leaf tool modules
    import this decorator while ``src.tools`` is still initializing.
    """

    def decorate(tool: ToolFnT) -> ToolFnT:
        setattr(tool, _OUTPUT_FIELDS_ATTRIBUTE, field_names)
        if model is not None:
            setattr(tool, _OUTPUT_MODEL_ATTRIBUTE, model)
        return tool

    return decorate


class TestCaseSummary(BaseModel):
    """A compact test-case entry returned by search and list tools."""

    model_config = ConfigDict(extra="forbid", strict=True)

    id: int | None = Field(description="Test case identifier.")
    name: str | None = Field(description="Test case name.")
    status: str = Field(description="Test case status label.")
    tags: list[str] = Field(description="Test case tags.")
    url: str | None = Field(default=None, description="Canonical TestOps URL.")


class Link(BaseModel):
    """A named external link in an agent-facing response."""

    model_config = ConfigDict(extra="forbid", strict=True)

    name: str | None = Field(default=None, description="Link label.")
    url: str = Field(description="Absolute link URL.")
    type: str | None = Field(default=None, description="Link type when supplied by TestOps.")


class Attachment(BaseModel):
    """A lightweight attachment reference."""

    model_config = ConfigDict(extra="forbid", strict=True)

    name: str = Field(description="Attachment filename or display name.")
    id: str | None = Field(default=None, description="Attachment identifier.")


class Step(BaseModel):
    """A serialized scenario step, including recursive shared-step children."""

    model_config = ConfigDict(extra="forbid", strict=True)

    index: int = Field(ge=1, description="One-based step index.")
    type: str | None = Field(default=None, description="Step kind, such as shared_step.")
    action: str | None = Field(default=None, description="Inline step action.")
    expected: str | None = Field(default=None, description="Expected result for an inline step.")
    shared_step_id: int | None = Field(default=None, description="Referenced shared-step identifier.")
    shared_step_url: str | None = Field(default=None, description="Referenced shared-step URL.")
    steps: list[Step] | None = Field(default=None, description="Nested shared-step children.")


class EntitySummary(BaseModel):
    """Closed common vocabulary for collection entries across Lucius tools."""

    model_config = ConfigDict(extra="forbid", strict=True)

    id: int | None = Field(default=None)
    name: str | None = Field(default=None)
    key: str | None = Field(default=None)
    status: str | None = Field(default=None)
    url: str | None = Field(default=None)
    type: str | None = Field(default=None)
    closed: bool | None = Field(default=None)
    tags: list[str] | None = Field(default=None)
    project_id: int | None = Field(default=None)
    test_case_id: int | None = Field(default=None)
    test_layer_id: int | None = Field(default=None)
    test_layer_name: str | None = Field(default=None)
    steps_count: int | None = Field(default=None, ge=0)
    test_cases_count: int | None = Field(default=None, ge=0)
    required: bool | None = Field(default=None)
    values: list[str] | None = Field(default=None)
    manual: bool | None = Field(default=None)
    assignee: str | None = Field(default=None)
    tested_by: str | None = Field(default=None)
    result_id: int | None = Field(default=None)


class Failure(BaseModel):
    """A rejected bulk-operation entry."""

    model_config = ConfigDict(extra="forbid", strict=True)

    index: int = Field(ge=0, description="Zero-based input item index.")
    message: str = Field(description="Reason the item was rejected.")


class KeyValue(BaseModel):
    """A string key/value pair, for example a manual-session environment entry."""

    model_config = ConfigDict(extra="forbid", strict=True)

    key: str = Field(description="Variable name.")
    value: str = Field(description="Variable value.")


class SearchTestCasesOutput(BaseModel):
    """Paginated output for ``search_test_cases``."""

    model_config = ConfigDict(extra="forbid", strict=True)

    total: int = Field(ge=0, description="Total matching test cases.")
    page: int = Field(ge=0, description="Zero-based result page.")
    size: int = Field(ge=0, description="Requested page size.")
    total_pages: int = Field(ge=0, description="Number of result pages.")
    query: str = Field(description="Query that produced these results.")
    items: list[TestCaseSummary] = Field(description="Matching test cases.")


class ToolOutputModel(BaseModel):
    """Shared, closed vocabulary used by concrete per-tool response models.

    The tools have intentionally small JSON envelopes but several operations
    return alternative confirmation, success, or idempotency branches.  The
    fields below enumerate that documented vocabulary; ``extra='forbid'`` is
    deliberate so an unmodelled runtime key fails at the contract boundary.
    Nested ``items`` and ``steps`` remain JSON values because their exact shape
    differs by entity, while their enclosing payload is always explicit.
    """

    model_config = ConfigDict(extra="forbid", strict=True)

    action: str | None = Field(default=None, description="Requested operation name.")
    add_test_case_ids: list[int] | None = Field(default=None)
    add_test_case_urls: list[str] | None = Field(default=None)
    already_linked: bool | None = Field(default=None)
    already_unlinked: bool | None = Field(default=None)
    aql_filter: str | None = Field(default=None)
    assigned_count: int | None = Field(default=None, ge=0)
    assignees: list[str] | None = Field(default=None)
    attachments: list[Attachment] | None = Field(default=None)
    autoclose: bool | None = Field(default=None)
    cfv_id: int | None = Field(default=None)
    changed: bool | None = Field(default=None)
    changes: list[str] | None = Field(default=None)
    closed: bool | None = Field(default=None)
    created_date: str | None = Field(default=None)
    custom_field_id: int | None = Field(default=None)
    custom_field_name: str | None = Field(default=None)
    custom_fields: list[EntitySummary] | dict[str, str | int | float | bool | list[str] | None] | None = Field(
        default=None, description="Custom-field values as named entries or a value map."
    )
    defect_id: int | None = Field(default=None)
    defect_url: str | None = Field(default=None)
    deleted_count: int | None = Field(default=None, ge=0)
    description: str | None = Field(default=None)
    environment: list[KeyValue] | None = Field(default=None)
    error: str | None = Field(default=None)
    external: bool | None = Field(default=None)
    failed_only: bool | None = Field(default=None)
    failures: list[Failure] | None = Field(default=None)
    file_names: list[str] | None = Field(default=None)
    filter_name: str | None = Field(default=None)
    force_manual: bool | None = Field(default=None)
    id: int | None = Field(default=None)
    integration_id: int | None = Field(default=None)
    issue_id: int | None = Field(default=None)
    issue_key: str | None = Field(default=None)
    items: list[EntitySummary] | None = Field(default=None, description="Entity-specific collection entries.")
    job_id: int | None = Field(default=None)
    job_run_id: int | None = Field(default=None)
    key: str | None = Field(default=None)
    known_defects_count: int | None = Field(default=None, ge=0)
    last_modified_date: str | None = Field(default=None)
    launch_id: int | None = Field(default=None)
    layer_id: int | None = Field(default=None)
    manual_execution_guidance: str | None = Field(default=None)
    manual_only: bool | None = Field(default=None)
    matcher_id: int | None = Field(default=None)
    message: str | None = Field(default=None)
    message_regex: str | None = Field(default=None)
    name: str | None = Field(default=None)
    new_defects_count: int | None = Field(default=None, ge=0)
    operation: str | None = Field(default=None)
    page: int | None = Field(default=None, ge=0)
    parent_suite_id: int | None = Field(default=None)
    plan_id: int | None = Field(default=None)
    precondition: str | None = Field(default=None)
    project_id: int | None = Field(default=None)
    query: str | None = Field(default=None)
    remove_test_case_ids: list[int] | None = Field(default=None)
    remove_test_case_urls: list[str] | None = Field(default=None)
    requested_count: int | None = Field(default=None, ge=0)
    requires_confirmation: bool | None = Field(default=None)
    result_ids: list[int] | None = Field(default=None)
    scheduled_count: int | None = Field(default=None, ge=0)
    schema_id: int | None = Field(default=None)
    shared_step_id: int | None = Field(default=None)
    shared_step_url: str | None = Field(default=None)
    size: int | None = Field(default=None, ge=0)
    status: str | None = Field(default=None)
    status_code: int | None = Field(default=None)
    step_id: int | None = Field(default=None)
    steps: list[Step] | None = Field(default=None, description="Serialized scenario steps.")
    submitted_count: int | None = Field(default=None, ge=0)
    suite_id: int | None = Field(default=None)
    summary: str | None = Field(default=None)
    tags: list[str] | None = Field(default=None)
    target_id: int | None = Field(default=None)
    target_kind: str | None = Field(default=None)
    test_case_id: int | None = Field(default=None)
    test_case_ids: list[int] | None = Field(default=None)
    test_case_url: str | None = Field(default=None)
    test_case_urls: list[str] | None = Field(default=None)
    test_layer_id: int | None = Field(default=None)
    test_layer_name: str | None = Field(default=None)
    test_session_id: int | None = Field(default=None)
    total: int | None = Field(default=None, ge=0)
    total_pages: int | None = Field(default=None, ge=0)
    trace_regex: str | None = Field(default=None)
    tree: EntitySummary | None = Field(default=None)
    tree_id: int | None = Field(default=None)
    type: str | None = Field(default=None)
    updated_fields: list[str] | None = Field(default=None)
    uploaded_count: int | None = Field(default=None, ge=0)
    url: str | None = Field(default=None)
    values: list[str] | None = Field(default=None)
    issues: list[str] | None = Field(default=None)
    required: bool | None = Field(default=None)
    test_cases_count: int | None = Field(default=None, ge=0)
    steps_count: int | None = Field(default=None, ge=0)
    assignee: str | None = Field(default=None)
    manual: bool | None = Field(default=None)
    result_id: int | None = Field(default=None)
    tested_by: str | None = Field(default=None)


def _model_name(tool_name: str) -> str:
    return "".join(part.capitalize() for part in tool_name.split("_")) + "Output"


_COLLECTION_FIELDS = ("items", "total", "page", "size", "total_pages")
_LAUNCH_FIELDS = (
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
_TEST_CASE_LIST_FIELDS = ("total", "page", "size", "total_pages", "items")

# Each tool explicitly selects the fields its documented branches can produce.
# Values are optional at the object level because confirmation and idempotent
# responses intentionally have different envelopes for the same operation.
_TOOL_FIELDS: dict[str, tuple[str, ...]] = {
    "add_test_result_attachment": ("target_kind", "target_id", "file_names", "status_code"),
    "add_test_step_attachment": ("target_kind", "target_id", "file_names", "status_code"),
    "assign_test_cases_to_suite": ("tree_id", "suite_id", "test_case_ids", "assigned_count"),
    "close_launch": _LAUNCH_FIELDS,
    "create_custom_field_value": ("id", "name", "custom_field_id", "custom_field_name"),
    "create_defect": ("id", "name", "description", "url"),
    "create_defect_matcher": ("id", "defect_id", "name", "message_regex", "trace_regex"),
    "create_launch": _LAUNCH_FIELDS,
    "create_shared_step": ("id", "name", "project_id", "url"),
    "create_test_case": ("id", "name", "issues", "url"),
    "create_test_layer": ("id", "name"),
    "create_test_layer_schema": ("id", "key", "test_layer_id", "test_layer_name"),
    "create_test_plan": ("id", "name", "aql_filter", "test_case_ids", "test_case_urls", "url"),
    "create_test_suite": ("id", "name", "tree_id", "parent_suite_id"),
    "delete_archived_shared_steps": ("deleted_count",),
    "delete_archived_test_cases": ("deleted_count",),
    "delete_custom_field_value": ("requires_confirmation", "action", "cfv_id", "id", "status"),
    "delete_defect": ("defect_id", "id", "status", "url"),
    "delete_defect_matcher": ("matcher_id", "id", "status"),
    "delete_launch": ("launch_id", "status", "message"),
    "delete_shared_step": ("requires_confirmation", "action", "step_id", "id", "status", "url"),
    "delete_test_case": ("requires_confirmation", "action", "test_case_id", "name", "status", "error", "url"),
    "delete_test_layer": ("requires_confirmation", "action", "layer_id", "id", "status"),
    "delete_test_layer_schema": ("requires_confirmation", "action", "schema_id", "id", "status"),
    "delete_test_plan": ("requires_confirmation", "action", "plan_id", "status", "url"),
    "delete_test_suite": ("requires_confirmation", "action", "suite_id", "status"),
    "delete_unused_custom_fields": ("deleted_count",),
    "get_custom_fields": ("items", "total", "filter_name"),
    "get_defect": ("id", "name", "description", "status", "closed", "url"),
    "get_launch": _LAUNCH_FIELDS,
    "get_test_case_custom_fields": ("test_case_id", "custom_fields"),
    "get_test_case_details": (
        "id",
        "name",
        "status",
        "description",
        "precondition",
        "tags",
        "custom_fields",
        "attachments",
        "steps",
        "url",
    ),
    "link_defect_to_test_case": (
        "defect_id",
        "defect_url",
        "test_case_id",
        "test_case_url",
        "integration_id",
        "issue_key",
        "already_linked",
    ),
    "link_shared_step": (
        "requires_confirmation",
        "action",
        "test_case_id",
        "test_case_url",
        "shared_step_id",
        "shared_step_url",
        "steps",
        "status",
        "error",
    ),
    "list_custom_field_values": _COLLECTION_FIELDS,
    "list_defect_matchers": ("defect_id", *_COLLECTION_FIELDS),
    "list_defect_test_cases": ("defect_id", "defect_url", *_COLLECTION_FIELDS),
    "list_defects": _COLLECTION_FIELDS,
    "list_integrations": ("items", "total"),
    "list_launch_test_results": ("launch_id", "manual_only", "failed_only", *_COLLECTION_FIELDS),
    "list_launches": _COLLECTION_FIELDS,
    "list_shared_steps": _COLLECTION_FIELDS,
    "list_test_cases": _TEST_CASE_LIST_FIELDS,
    "list_test_layer_schemas": _COLLECTION_FIELDS,
    "list_test_layers": _COLLECTION_FIELDS,
    "list_test_plans": _COLLECTION_FIELDS,
    "list_test_suites": ("tree", "items", "total"),
    "manage_test_plan_content": (
        "plan_id",
        "add_test_case_ids",
        "remove_test_case_ids",
        "aql_filter",
        "add_test_case_urls",
        "remove_test_case_urls",
        "url",
    ),
    "reopen_launch": _LAUNCH_FIELDS,
    "rerun_test_results_manually": ("launch_id", "result_ids", "scheduled_count", "assignees", "force_manual"),
    "search_test_cases": (*_TEST_CASE_LIST_FIELDS, "query"),
    "start_manual_test_session": ("test_session_id", "launch_id", "job_id", "job_run_id", "project_id", "environment"),
    "submit_manual_test_results": ("test_session_id", "result_ids", "submitted_count"),
    "unlink_issue_from_test_case": ("test_case_id", "issue_id", "status", "already_unlinked"),
    "unlink_shared_step": (
        "requires_confirmation",
        "action",
        "test_case_id",
        "test_case_url",
        "shared_step_id",
        "shared_step_url",
        "steps",
        "status",
        "error",
    ),
    "update_custom_field_value": (
        "requires_confirmation",
        "action",
        "cfv_id",
        "id",
        "name",
        "custom_field_id",
        "custom_field_name",
    ),
    "update_defect": ("id", "name", "description", "status", "closed", "url"),
    "update_defect_matcher": ("id", "name", "message_regex", "trace_regex"),
    "update_shared_step": (
        "requires_confirmation",
        "action",
        "step_id",
        "id",
        "name",
        "changed",
        "updated_fields",
        "url",
    ),
    "update_test_case": ("requires_confirmation", "action", "test_case_id", "id", "name", "summary", "changes", "url"),
    "update_test_layer": ("requires_confirmation", "action", "layer_id", "id", "name", "changed"),
    "update_test_layer_schema": (
        "requires_confirmation",
        "action",
        "schema_id",
        "id",
        "key",
        "test_layer_name",
        "changed",
    ),
    "update_test_plan": ("id", "name", "url"),
    "upload_test_results": ("launch_id", "requested_count", "uploaded_count", "result_ids", "failures"),
}


def _create_tool_output_model(tool: ToolFn) -> type[BaseModel]:
    fields: dict[str, Any] = {
        field_name: (
            ToolOutputModel.model_fields[field_name].annotation,
            Field(default=None, description=ToolOutputModel.model_fields[field_name].description),
        )
        for field_name in _output_fields_for(tool)
    }
    return cast(
        type[BaseModel],
        create_model(_model_name(tool.__name__), __config__=ConfigDict(extra="forbid", strict=True), **fields),
    )


OUTPUT_MODELS: dict[str, type[BaseModel]] = {}


def _output_fields_for(tool: ToolFn) -> tuple[str, ...]:
    fields = getattr(tool, _OUTPUT_FIELDS_ATTRIBUTE, None)
    if isinstance(fields, tuple) and all(isinstance(field, str) for field in fields):
        return fields
    from src.tools import output_fields_for

    return output_fields_for(tool)


def _ensure_output_models() -> None:
    if OUTPUT_MODELS:
        return
    from src.tools import all_tools, search_test_cases

    OUTPUT_MODELS.update({tool.__name__: _create_tool_output_model(tool) for tool in all_tools})
    OUTPUT_MODELS[search_test_cases.__name__] = SearchTestCasesOutput


def output_model_for(tool_name: str) -> type[BaseModel]:
    """Return the concrete Pydantic output model for a registered tool."""
    _ensure_output_models()
    try:
        return OUTPUT_MODELS[tool_name]
    except KeyError as exc:
        raise ValueError(f"No output model registered for tool '{tool_name}'") from exc


def output_schema_for(tool_name: str) -> dict[str, Any]:
    """Build the FastMCP-compatible serialization schema for ``tool_name``."""
    return output_model_for(tool_name).model_json_schema(mode="serialization", by_alias=True)


def validate_registry_coverage() -> None:
    """Fail fast when tools and their output-contract registrations drift."""
    _ensure_output_models()
    from src.tools import all_tools, validate_output_field_coverage

    validate_output_field_coverage()

    registered = {tool.__name__ for tool in all_tools}
    schemas = set(OUTPUT_MODELS)
    if registered != schemas:
        missing = sorted(registered - schemas)
        stale = sorted(schemas - registered)
        raise RuntimeError(f"Output schema registry coverage mismatch; missing={missing}, stale={stale}")
