"""Pydantic response models published as Lucius MCP output schemas.

These models intentionally describe Lucius's agent-facing response envelopes,
rather than the generated Allure API client DTOs.  Each registered tool owns a
concrete object-root model so the MCP manifest remains stable as upstream API
models evolve.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal, TypeVar, cast

from pydantic import BaseModel, ConfigDict, Field, create_model, model_validator

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


class SuiteNodeOutput(BaseModel):
    """A recursive hierarchy-suite node."""

    model_config = ConfigDict(extra="forbid", strict=True)

    id: int | None = Field(default=None)
    name: str | None = Field(default=None)
    children: list[SuiteNodeOutput] = Field(default_factory=list)


class LaunchMutationSummary(BaseModel):
    """Stable compact launch fields emitted by create and lifecycle tools."""

    model_config = ConfigDict(extra="forbid", strict=True)

    id: int | None = Field(default=None)
    name: str | None = Field(default=None)
    closed: bool | None = Field(default=None)
    created_date: int | None = Field(default=None)
    last_modified_date: int | None = Field(default=None)
    project_id: int | None = Field(default=None)
    autoclose: bool | None = Field(default=None)
    external: bool | None = Field(default=None)
    known_defects_count: int | None = Field(default=None, ge=0)
    new_defects_count: int | None = Field(default=None, ge=0)
    manual_execution_guidance: str | None = Field(default=None)
    url: str | None = Field(default=None)
    operation: str | None = Field(default=None)


class LaunchListItem(BaseModel):
    """Compact launch fields emitted only for collection discovery."""

    model_config = ConfigDict(extra="forbid", strict=True)

    id: int | None = Field(default=None)
    name: str | None = Field(default=None)
    closed: bool | None = Field(default=None)
    created_date: int | None = Field(default=None)
    last_modified_date: int | None = Field(default=None)
    project_id: int | None = Field(default=None)
    autoclose: bool | None = Field(default=None)
    external: bool | None = Field(default=None)
    url: str | None = Field(default=None)


class LaunchStatisticItem(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    status: str | None = Field(default=None)
    count: int | None = Field(default=None, ge=0)


class LaunchEnvironmentVariable(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    id: int | None = Field(default=None)
    name: str | None = Field(default=None)


class LaunchEnvironmentValue(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    id: int | None = Field(default=None)
    name: str | None = Field(default=None)
    variable: LaunchEnvironmentVariable | None = Field(default=None)


class LaunchJob(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    id: int | None = Field(default=None)
    name: str | None = Field(default=None)
    type: str | None = Field(default=None)
    url: str | None = Field(default=None)


class LaunchJobRun(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    id: int | None = Field(default=None)
    name: str | None = Field(default=None)
    status: str | None = Field(default=None)
    stage: str | None = Field(default=None)
    url: str | None = Field(default=None)
    error_message: str | None = Field(default=None)
    external_id: str | None = Field(default=None)
    job: LaunchJob | None = Field(default=None)


class LaunchTag(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    id: int | None = Field(default=None)
    name: str | None = Field(default=None)


class LaunchIssue(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    id: int | None = Field(default=None)
    name: str | None = Field(default=None)
    display_name: str | None = Field(default=None)
    status: str | None = Field(default=None)
    summary: str | None = Field(default=None)
    url: str | None = Field(default=None)
    closed: bool | None = Field(default=None)


class LaunchLink(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    name: str | None = Field(default=None)
    type: str | None = Field(default=None)
    url: str | None = Field(default=None)


class LaunchExecutionSnapshotOutput(BaseModel):
    """Point-in-time state for the opt-in execution aggregate."""

    model_config = ConfigDict(extra="forbid", strict=True)

    captured_at: str
    closed: bool | None = Field(default=None)
    mutable: bool
    message: str


class LaunchUnavailableSectionOutput(BaseModel):
    """Sanitized optional-read completeness diagnostic."""

    model_config = ConfigDict(extra="forbid", strict=True)

    section: str
    reason: str
    status_code: int | None = Field(default=None)
    message: str
    items_retrieved: int | None = Field(default=None, ge=0)


class LaunchDetailOutput(BaseModel):
    """Rich exact-ID launch fields, with explicit stable nested projections."""

    model_config = ConfigDict(extra="forbid", strict=True)

    id: int | None = Field(default=None)
    name: str | None = Field(default=None)
    closed: bool | None = Field(default=None)
    created_date: int | None = Field(default=None)
    last_modified_date: int | None = Field(default=None)
    project_id: int | None = Field(default=None)
    autoclose: bool | None = Field(default=None)
    external: bool | None = Field(default=None)
    created_by: str | None = Field(default=None)
    last_modified_by: str | None = Field(default=None)
    statistic: list[LaunchStatisticItem] | None = Field(default=None)
    known_defects_count: int | None = Field(default=None, ge=0)
    new_defects_count: int | None = Field(default=None, ge=0)
    environment: list[LaunchEnvironmentValue] | None = Field(default=None)
    jobs: list[LaunchJobRun] | None = Field(default=None)
    tags: list[LaunchTag] | None = Field(default=None)
    issues: list[LaunchIssue] | None = Field(default=None)
    links: list[LaunchLink] | None = Field(default=None)
    manual_execution_guidance: str | None = Field(default=None)
    url: str | None = Field(default=None)
    duration: list[object] | None = Field(default=None)
    progress: object | None = Field(default=None)
    assignees: list[object] | None = Field(default=None)
    testers: list[object] | None = Field(default=None)
    variables: list[object] | None = Field(default=None)
    defects: list[object] | None = Field(default=None)
    member_stats: list[object] | None = Field(default=None)
    muted_results: list[object] | None = Field(default=None)
    retries: list[object] | None = Field(default=None)
    unresolved_results: list[object] | None = Field(default=None)
    flat_test_results: list[object] | None = Field(
        default=None, description="Compact rows; each row id is the Test Result ID for get_test_result."
    )
    core_test_result_index: list[object] | None = Field(default=None)
    result_timeline: object | None = Field(default=None)
    result_defect_tree: object | None = Field(default=None)
    trees: list[object] | None = Field(default=None)
    execution_snapshot: LaunchExecutionSnapshotOutput | None = Field(default=None)
    partial: bool | None = Field(default=None)
    unavailable_sections: list[LaunchUnavailableSectionOutput] | None = Field(default=None)


class TestResultAttachmentOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    attachment_id: int | None = Field(default=None, ge=1, description="Attachment identifier for preparation.")
    attachment_kind: Literal["test_result", "fixture_result", "test_case"] | None = Field(
        default=None, description="Verified attachment owner kind for prepare_attachment_download."
    )
    test_result_id: int | None = Field(
        default=None, ge=1, description="Required owner context for result or fixture attachments."
    )
    test_case_id: int | None = Field(
        default=None, ge=1, description="Required owner context for test-case attachments."
    )
    name: str | None = None
    entity: str | None = None
    content_type: str | None = None
    content_length: int | None = None
    missed: bool | None = None
    from_test_case: bool | None = None

    @model_validator(mode="after")
    def _validate_preparation_reference(self) -> TestResultAttachmentOutput:
        if self.attachment_id is None:
            return self
        if self.attachment_kind in {"test_result", "fixture_result"}:
            if self.test_result_id is None or self.test_case_id is not None:
                raise ValueError("result and fixture attachments require only test_result_id")
        elif self.attachment_kind == "test_case":
            if self.test_case_id is None or self.test_result_id is not None:
                raise ValueError("test-case attachments require only test_case_id")
        else:
            raise ValueError("attachment references require a supported attachment_kind")
        return self


class TestCaseAttachmentOutput(BaseModel):
    """A test-case attachment reference safe to pass to the preparation tool."""

    model_config = ConfigDict(extra="forbid", strict=True)

    attachment_id: int | None = Field(default=None, ge=1, description="Attachment identifier for preparation.")
    attachment_kind: Literal["test_case"] = Field(
        default="test_case", description="Verified attachment owner kind for prepare_attachment_download."
    )
    test_case_id: int | None = Field(default=None, ge=1, description="Required owner context for preparation.")
    name: str = Field(description="Attachment filename or display name.")
    content_type: str | None = Field(default=None, description="Attachment MIME type when available.")
    content_length: int | None = Field(default=None, ge=0, description="Attachment byte length when available.")

    @model_validator(mode="after")
    def _validate_preparation_reference(self) -> TestCaseAttachmentOutput:
        if self.attachment_id is not None and self.test_case_id is None:
            raise ValueError("test-case attachment references require test_case_id")
        return self


class PreparedAttachmentDownloadOutput(BaseModel):
    """Opaque one-time attachment delivery metadata returned by the public preparation tool."""

    model_config = ConfigDict(extra="forbid", strict=True)

    attachment_id: int = Field(gt=0, description="Verified attachment identifier.")
    attachment_kind: Literal["test_result", "fixture_result", "test_case"] = Field(
        description="Verified attachment owner kind."
    )
    test_result_id: int | None = Field(
        default=None, gt=0, description="Owner context for result or fixture attachments."
    )
    test_case_id: int | None = Field(default=None, gt=0, description="Owner context for test-case attachments.")
    download_url: str = Field(
        description="Opaque Lucius URL to HTTP GET before expires_at; no Allure bearer token is needed."
    )
    expires_at: str = Field(description="UTC expiry timestamp for the one-time download URL.")
    name: str = Field(description="Sanitized attachment filename.")
    content_type: str = Field(description="Attachment MIME type.")
    content_length: int = Field(ge=0, description="Prepared attachment byte length.")

    @model_validator(mode="after")
    def _validate_owner_context(self) -> PreparedAttachmentDownloadOutput:
        if self.attachment_kind in {"test_result", "fixture_result"}:
            if self.test_result_id is None or self.test_case_id is not None:
                raise ValueError("result and fixture attachments require only test_result_id")
        elif self.test_case_id is None or self.test_result_id is not None:
            raise ValueError("test-case attachments require only test_case_id")
        return self


class TestResultStepOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    id: int | None = None
    type: str | None = None
    name: str | None = None
    action: str | None = None
    body: str | None = None
    body_json: object | None = None
    expected_result: str | None = None
    keyword: str | None = None
    status: str | None = None
    start: int | None = None
    stop: int | None = None
    duration: int | None = None
    message: str | None = None
    trace: str | None = None
    parameters: list[dict[str, object]] = Field(default_factory=list)
    attachments: list[TestResultAttachmentOutput] = Field(default_factory=list)
    steps: list[TestResultStepOutput] = Field(default_factory=list)


class TestResultFixtureOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    id: int | None = None
    name: str | None = None
    type: str | None = None
    status: str | None = None
    start: int | None = None
    stop: int | None = None
    duration: int | None = None
    message: str | None = None
    trace: str | None = None
    steps: list[TestResultStepOutput] = Field(default_factory=list)
    attachments: list[TestResultAttachmentOutput] = Field(default_factory=list)


class RelatedTestResultOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    relation: str
    test_result_id: int | None = None
    launch_id: int | None = None
    name: str | None = None
    status: str | None = None
    url: str | None = None


class UnavailableSectionOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    section: str
    reason: str
    status_code: int | None = None
    message: str | None = None
    items_retrieved: int = Field(ge=0)


class TestResultNamedOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    id: int | None = None
    name: str | None = None


class TestResultReferenceOutput(TestResultNamedOutput):
    url: str | None = None


class TestResultParameterOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    name: str | None = None
    value: str | None = None
    excluded: bool | None = None
    hidden: bool | None = None


class TestResultLinkOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    name: str | None = None
    type: str | None = None
    url: str | None = None


class TestResultJobOutput(TestResultReferenceOutput):
    type: str | None = None


class TestResultJobRunOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    id: int | None = None
    name: str | None = None
    status: str | None = None
    stage: str | None = None
    url: str | None = None
    error_message: str | None = None
    external_id: str | None = None
    job: TestResultJobOutput | None = None


class TestResultCoreOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    name: str | None = None
    full_name: str | None = None
    status: str | None = None
    manual: bool | None = None
    external: bool | None = None
    hidden: bool | None = None
    flaky: bool | None = None
    muted: bool | None = None
    known: bool | None = None
    start: int | None = None
    stop: int | None = None
    duration: int | None = None
    created_date: int | None = None
    last_modified_date: int | None = None
    created_by: str | None = None
    last_modified_by: str | None = None
    assignee: str | None = None
    tested_by: str | None = None
    host_id: str | None = None
    thread_id: str | None = None
    scenario_key: str | None = None
    history_key: str | None = None
    description: str | None = None
    description_html: str | None = None
    precondition: str | None = None
    precondition_html: str | None = None
    expected_result: str | None = None
    expected_result_html: str | None = None
    message: str | None = None
    trace: str | None = None
    category: TestResultNamedOutput | None = None
    layer: TestResultNamedOutput | None = None
    parameters: list[TestResultParameterOutput] = Field(default_factory=list)
    tags: list[TestResultNamedOutput] = Field(default_factory=list)
    links: list[TestResultLinkOutput] = Field(default_factory=list)
    job_run: TestResultJobRunOutput | None = None


class TestResultCustomFieldOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    id: int | None = None
    name: str | None = None
    required: bool | None = None
    single_select: bool | None = None
    locked: bool | None = None
    archived: bool | None = None
    default_custom_field_value_id: int | None = None


class TestResultCustomFieldValuesOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    custom_field: TestResultCustomFieldOutput | None = None
    values: list[TestResultNamedOutput] = Field(default_factory=list)


class TestResultEnvironmentOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    id: int | None = None
    name: str | None = None
    variable: TestResultNamedOutput | None = None


class TestResultMemberOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    id: int | None = None
    name: str | None = None
    role: TestResultNamedOutput | None = None


class TestResultKeyOutput(TestResultReferenceOutput):
    integration_id: int | None = None


class TestResultIssueOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    id: int | None = None
    integration_id: int | None = None
    integration_type: str | None = None
    name: str | None = None
    display_name: str | None = None
    status: str | None = None
    summary: str | None = None
    url: str | None = None
    closed: bool | None = None


class TestResultDefectOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    id: int | None = None
    name: str | None = None
    closed: bool | None = None
    issue: TestResultIssueOutput | None = None


class TestResultDetailOutput(BaseModel):
    """Stable object-root output for one exact enriched TestOps result."""

    model_config = ConfigDict(extra="forbid", strict=True)

    actual_launch_id: int | None = None
    test_result_id: int | None = None
    project_id: int | None = None
    result_url: str | None = None
    launch_url: str | None = None
    test_case: TestResultReferenceOutput | None = None
    core: TestResultCoreOutput | None = None
    custom_fields: list[TestResultCustomFieldValuesOutput] | None = None
    environment: list[TestResultEnvironmentOutput] | None = None
    members: list[TestResultMemberOutput] | None = None
    test_keys: list[TestResultKeyOutput] | None = None
    issues: list[TestResultIssueOutput] | None = None
    defects: list[TestResultDefectOutput] | None = None
    execution_steps: list[TestResultStepOutput] | None = None
    fixtures: list[TestResultFixtureOutput] | None = None
    result_attachments: list[TestResultAttachmentOutput] | None = None
    related_results: list[RelatedTestResultOutput] | None = None
    partial: bool | None = None
    unavailable_sections: list[UnavailableSectionOutput] | None = None


class ListLaunchesOutput(BaseModel):
    """Paginated compact launches."""

    model_config = ConfigDict(extra="forbid", strict=True)

    total: int | None = Field(default=None, ge=0)
    page: int | None = Field(default=None, ge=0)
    size: int | None = Field(default=None, ge=0)
    total_pages: int | None = Field(default=None, ge=0)
    items: list[LaunchListItem] | None = Field(default=None)


class ListTestSuitesOutput(BaseModel):
    """Hierarchy tree and its recursive suite nodes."""

    model_config = ConfigDict(extra="forbid", strict=True)

    tree: EntitySummary | None = Field(default=None)
    items: list[SuiteNodeOutput] | None = Field(default=None)
    total: int | None = Field(default=None, ge=0)


class DefectMatcherSummary(BaseModel):
    """A matcher entry returned when listing a defect's automation rules."""

    model_config = ConfigDict(extra="forbid", strict=True)

    id: int | None = Field(default=None)
    name: str | None = Field(default=None)
    message_regex: str | None = Field(default=None)
    trace_regex: str | None = Field(default=None)


class ListDefectMatchersOutput(BaseModel):
    """Matcher list for a defect."""

    model_config = ConfigDict(extra="forbid", strict=True)

    defect_id: int | None = Field(default=None)
    items: list[DefectMatcherSummary] | None = Field(default=None)
    total: int | None = Field(default=None, ge=0)
    page: int | None = Field(default=None, ge=0)
    size: int | None = Field(default=None, ge=0)
    total_pages: int | None = Field(default=None, ge=0)


class CustomFieldEntry(BaseModel):
    """A named custom-field value exposed by test-case details."""

    model_config = ConfigDict(extra="forbid", strict=True)

    name: str = Field(description="Custom field name.")
    value: str = Field(description="Rendered custom field value.")


class TestCaseDetailsOutput(BaseModel):
    """Structured details for one test case."""

    model_config = ConfigDict(extra="forbid", strict=True)

    id: int | None = Field(default=None)
    name: str | None = Field(default=None)
    status: str | None = Field(default=None)
    description: str | None = Field(default=None)
    precondition: str | None = Field(default=None)
    tags: list[str] | None = Field(default=None)
    custom_fields: list[CustomFieldEntry] | None = Field(default=None)
    attachments: list[TestCaseAttachmentOutput] | None = Field(default=None)
    steps: list[Step] | None = Field(default=None)
    url: str | None = Field(default=None)


class UnlinkIssueFromTestCaseOutput(BaseModel):
    """Confirmation for unlinking an issue by numeric ID or issue key."""

    model_config = ConfigDict(extra="forbid", strict=True)

    test_case_id: int | None = Field(default=None)
    issue_id: int | str | None = Field(default=None)
    status: str | None = Field(default=None)
    already_unlinked: bool | None = Field(default=None)


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
    abbr: str | None = Field(default=None, description="Project abbreviation.")
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
    code: str | None = Field(default=None, description="Generated source-code snippet.")
    created_date: int | None = Field(default=None)
    custom_field_id: int | None = Field(default=None)
    custom_field_name: str | None = Field(default=None)
    custom_fields: list[CustomFieldEntry] | dict[str, str | int | float | bool | list[str] | None] | None = Field(
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
    framework: str | None = Field(default=None, description="Requested target testing framework.")
    force_manual: bool | None = Field(default=None)
    id: int | None = Field(default=None)
    integration_id: int | None = Field(default=None)
    is_public: bool | None = Field(default=None, description="Whether the project is publicly visible.")
    issue_id: int | str | None = Field(default=None)
    issue_key: str | None = Field(default=None)
    items: list[EntitySummary] | None = Field(default=None, description="Entity-specific collection entries.")
    job_id: int | None = Field(default=None)
    job_run_id: int | None = Field(default=None)
    key: str | None = Field(default=None)
    known_defects_count: int | None = Field(default=None, ge=0)
    language: str | None = Field(default=None, description="Requested target programming language.")
    last_modified_date: int | None = Field(default=None)
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
    metadata: list[str] | None = Field(
        default=None,
        description="Canonical test-case metadata selections included in generated code.",
    )
    result_id: int | None = Field(default=None)
    tested_by: str | None = Field(default=None)


def _model_name(tool_name: str) -> str:
    return "".join(part.capitalize() for part in tool_name.split("_")) + "Output"


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
    raise ValueError(f"No output fields declared for tool '{tool.__name__}'")


def _output_model_for_tool(tool: ToolFn) -> type[BaseModel]:
    declared_model = getattr(tool, _OUTPUT_MODEL_ATTRIBUTE, None)
    if declared_model is None:
        return _create_tool_output_model(tool)
    if isinstance(declared_model, type) and issubclass(declared_model, BaseModel):
        return declared_model
    raise TypeError(f"Invalid output model declared for tool '{tool.__name__}'")


def _ensure_output_models() -> None:
    if OUTPUT_MODELS:
        return
    from src.tools import all_tools

    OUTPUT_MODELS.update({tool.__name__: _output_model_for_tool(tool) for tool in all_tools})


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
    from src.tools import all_tools

    registered = {tool.__name__ for tool in all_tools}
    schemas = set(OUTPUT_MODELS)
    if registered != schemas:
        missing = sorted(registered - schemas)
        stale = sorted(schemas - registered)
        raise RuntimeError(f"Output schema registry coverage mismatch; missing={missing}, stale={stale}")
