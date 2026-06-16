"""Output schema models for MCP tools.

These Pydantic models define the structured content (json_payload) that each tool returns.
They are used to generate the outputSchema for MCP tool registration.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# Base response models
class BaseResponse(BaseModel):
    """Base model for all tool responses."""

    pass


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    status: str = "error"


class SuccessResponse(BaseModel):
    """Standard success response."""

    status: str = "success"


# Test Case related schemas
class TestCaseCreatedResponse(BaseModel):
    """Response from create_test_case."""

    id: int
    name: str
    issues: list[str] = Field(default_factory=list)
    url: str


class TestCaseDetailsResponse(BaseModel):
    """Response from get_test_case_details."""

    id: int | None
    name: str | None
    status: str
    description: str | None
    precondition: str | None
    tags: list[str]
    custom_fields: list[dict[str, str]]
    attachments: list[dict[str, str]]
    steps: list[dict[str, Any]]
    url: str | None = None


class TestCaseListResponse(BaseModel):
    """Response from list_test_cases."""

    total: int
    page: int
    size: int
    total_pages: int
    items: list[dict[str, Any]]


class TestCaseSearchResponse(BaseModel):
    """Response from search_test_cases."""

    total: int
    page: int
    size: int
    total_pages: int
    items: list[dict[str, Any]]
    query: str


class CustomFieldsResponse(BaseModel):
    """Response from get_custom_fields."""

    items: list[dict[str, Any]]
    total: int


class CustomFieldValueResponse(BaseModel):
    """Response from get_test_case_custom_fields_values."""

    # Dynamic based on custom fields
    pass


class TestCaseCustomFieldsResponse(BaseModel):
    """Response from get_test_case_custom_fields."""

    items: list[dict[str, str]]
    total: int


class TestCaseUpdatedResponse(BaseModel):
    """Response from update_test_case."""

    id: int
    name: str
    status: str
    url: str


class TestCaseDeletedResponse(BaseModel):
    """Response from delete_test_case."""

    test_case_id: int
    name: str | None
    status: str
    url: str


class DeletedCountResponse(BaseModel):
    """Response from delete_archived_* operations."""

    deleted_count: int


# Custom Field Value schemas
class CustomFieldValueCreatedResponse(BaseModel):
    """Response from create_custom_field_value."""

    id: int
    name: str
    value: str | list[str]
    custom_field_id: int


class CustomFieldValueUpdatedResponse(BaseModel):
    """Response from update_custom_field_value."""

    id: int
    name: str
    value: str | list[str]
    custom_field_id: int


class CustomFieldValueDeletedResponse(BaseModel):
    """Response from delete_custom_field_value."""

    id: int
    status: str


# Integration schemas
class IntegrationItem(BaseModel):
    """Integration item."""

    id: int | None
    name: str
    type: str | None


class IntegrationsResponse(BaseModel):
    """Response from list_integrations."""

    items: list[IntegrationItem]
    total: int


# Launch schemas
class LaunchPayload(BaseModel):
    """Launch payload."""

    id: int | None
    name: str | None
    closed: bool | None
    created_date: int | None
    last_modified_date: int | None
    project_id: int | None
    autoclose: bool | None
    external: bool | None
    known_defects_count: int | None
    new_defects_count: int | None
    url: str | None = None


class LaunchListResponse(BaseModel):
    """Response from list_launches."""

    total: int
    page: int
    size: int
    total_pages: int
    items: list[LaunchPayload]


class LaunchDetailResponse(BaseModel):
    """Response from get_launch."""

    id: int | None
    name: str | None
    closed: bool | None
    created_date: int | None
    last_modified_date: int | None
    project_id: int | None
    autoclose: bool | None
    external: bool | None
    known_defects_count: int | None
    new_defects_count: int | None
    url: str | None = None
    operation: str | None = None


class LaunchDeleteResponse(BaseModel):
    """Response from delete_launch."""

    launch_id: int
    name: str | None
    status: str
    message: str
    url: str


# Shared Step schemas
class SharedStepItem(BaseModel):
    """Shared step item."""

    id: int | None
    name: str | None
    steps_count: int | None
    url: str | None = None


class SharedStepsResponse(BaseModel):
    """Response from list_shared_steps."""

    items: list[SharedStepItem]
    total: int
    page: int
    size: int


class SharedStepCreatedResponse(BaseModel):
    """Response from create_shared_step."""

    id: int
    name: str
    project_id: int
    url: str


class SharedStepUpdatedResponse(BaseModel):
    """Response from update_shared_step."""

    id: int
    name: str
    changed: bool
    updated_fields: list[str]
    url: str


class SharedStepDeletedResponse(BaseModel):
    """Response from delete_shared_step."""

    id: int
    status: str
    url: str


# Test Layer schemas
class TestLayerItem(BaseModel):
    """Test layer item."""

    id: int
    name: str


class TestLayersResponse(BaseModel):
    """Response from list_test_layers."""

    items: list[TestLayerItem]
    total: int
    page: int
    size: int


class TestLayerCreatedResponse(BaseModel):
    """Response from create_test_layer."""

    id: int
    name: str


class TestLayerDeletedResponse(BaseModel):
    """Response from delete_test_layer."""

    id: int
    status: str


# Test Suite schemas
class TestSuiteCreatedResponse(BaseModel):
    """Response from create_test_suite."""

    id: int
    name: str
    project_id: int


class TestSuiteListResponse(BaseModel):
    """Response from list_test_suites."""

    items: list[dict[str, Any]]
    total: int
    page: int
    size: int


class TestSuiteDeletedResponse(BaseModel):
    """Response from delete_test_suite."""

    id: int
    status: str


# Test Plan schemas
class TestPlanCreatedResponse(BaseModel):
    """Response from create_test_plan."""

    id: int
    name: str
    project_id: int


class TestPlanListResponse(BaseModel):
    """Response from list_test_plans."""

    items: list[dict[str, Any]]
    total: int
    page: int
    size: int


class TestPlanDeletedResponse(BaseModel):
    """Response from delete_test_plan."""

    id: int
    status: str


# Defect schemas
class DefectPayload(BaseModel):
    """Defect payload."""

    id: int
    name: str
    closed: bool
    status: str
    description: str | None
    url: str


class DefectCreatedResponse(BaseModel):
    """Response from create_defect."""

    id: int
    name: str
    description: str | None
    url: str


class DefectDetailResponse(BaseModel):
    """Response from get_defect."""

    id: int
    name: str
    closed: bool
    status: str
    description: str | None
    url: str


class DefectUpdatedResponse(BaseModel):
    """Response from update_defect."""

    id: int
    name: str
    closed: bool
    status: str
    description: str | None
    url: str


class DefectDeletedResponse(BaseModel):
    """Response from delete_defect."""

    id: int
    status: str
    url: str


class DefectListResponse(BaseModel):
    """Response from list_defects."""

    items: list[DefectPayload]


class DefectLinkResponse(BaseModel):
    """Response from link_defect_to_test_case."""

    defect_id: int
    defect_url: str
    test_case_id: int
    test_case_url: str
    issue_key: str | None
    integration_id: int
    already_linked: bool


class DefectTestCasesResponse(BaseModel):
    """Response from list_defect_test_cases."""

    total: int
    page: int
    size: int
    total_pages: int
    items: list[dict[str, Any]]
    defect_id: int
    defect_url: str


# Defect Matcher schemas
class DefectMatcherPayload(BaseModel):
    """Defect matcher payload."""

    id: int
    name: str
    message_regex: str | None
    trace_regex: str | None


class DefectMatcherCreatedResponse(BaseModel):
    """Response from create_defect_matcher."""

    id: int
    name: str
    defect_id: int
    message_regex: str | None
    trace_regex: str | None


class DefectMatcherUpdatedResponse(BaseModel):
    """Response from update_defect_matcher."""

    id: int
    name: str
    message_regex: str | None
    trace_regex: str | None


class DefectMatcherDeletedResponse(BaseModel):
    """Response from delete_defect_matcher."""

    id: int
    status: str


class DefectMatchersResponse(BaseModel):
    """Response from list_defect_matchers."""

    items: list[DefectMatcherPayload]
    defect_id: int


# Schema registry mapping tool name -> output schema model
TOOL_OUTPUT_SCHEMAS: dict[str, type[BaseModel]] = {
    "create_test_case": TestCaseCreatedResponse,
    "get_test_case_details": TestCaseDetailsResponse,
    "list_test_cases": TestCaseListResponse,
    "search_test_cases": TestCaseSearchResponse,
    "get_custom_fields": CustomFieldsResponse,
    "get_test_case_custom_fields": TestCaseCustomFieldsResponse,
    "update_test_case": TestCaseUpdatedResponse,
    "delete_test_case": TestCaseDeletedResponse,
    "delete_archived_test_cases": DeletedCountResponse,
    "delete_unused_custom_fields": DeletedCountResponse,
    "list_custom_field_values": CustomFieldsResponse,
    "create_custom_field_value": CustomFieldValueCreatedResponse,
    "update_custom_field_value": CustomFieldValueUpdatedResponse,
    "delete_custom_field_value": CustomFieldValueDeletedResponse,
    "list_integrations": IntegrationsResponse,
    "create_launch": LaunchDetailResponse,
    "get_launch": LaunchDetailResponse,
    "list_launches": LaunchListResponse,
    "delete_launch": LaunchDeleteResponse,
    "close_launch": LaunchDetailResponse,
    "reopen_launch": LaunchDetailResponse,
    "create_shared_step": SharedStepCreatedResponse,
    "list_shared_steps": SharedStepsResponse,
    "update_shared_step": SharedStepUpdatedResponse,
    "delete_shared_step": SharedStepDeletedResponse,
    "delete_archived_shared_steps": DeletedCountResponse,
    "link_shared_step": SuccessResponse,
    "unlink_shared_step": SuccessResponse,
    "list_test_layers": TestLayersResponse,
    "create_test_layer": TestLayerCreatedResponse,
    "update_test_layer": TestLayerCreatedResponse,
    "delete_test_layer": TestLayerDeletedResponse,
    "list_test_layer_schemas": TestLayersResponse,
    "create_test_layer_schema": TestLayerCreatedResponse,
    "update_test_layer_schema": TestLayerCreatedResponse,
    "delete_test_layer_schema": TestLayerDeletedResponse,
    "create_test_suite": TestSuiteCreatedResponse,
    "list_test_suites": TestSuiteListResponse,
    "assign_test_cases_to_suite": SuccessResponse,
    "delete_test_suite": TestSuiteDeletedResponse,
    "create_test_plan": TestPlanCreatedResponse,
    "update_test_plan": TestPlanCreatedResponse,
    "manage_test_plan_content": SuccessResponse,
    "list_test_plans": TestPlanListResponse,
    "delete_test_plan": TestPlanDeletedResponse,
    "create_defect": DefectCreatedResponse,
    "get_defect": DefectDetailResponse,
    "link_defect_to_test_case": DefectLinkResponse,
    "list_defect_test_cases": DefectTestCasesResponse,
    "update_defect": DefectUpdatedResponse,
    "delete_defect": DefectDeletedResponse,
    "list_defects": DefectListResponse,
    "create_defect_matcher": DefectMatcherCreatedResponse,
    "update_defect_matcher": DefectMatcherUpdatedResponse,
    "delete_defect_matcher": DefectMatcherDeletedResponse,
    "list_defect_matchers": DefectMatchersResponse,
}


def get_output_schema_model(tool_name: str) -> type[BaseModel] | None:
    """Get the output schema model for a tool."""
    return TOOL_OUTPUT_SCHEMAS.get(tool_name)


def get_all_output_schemas() -> dict[str, type[BaseModel]]:
    """Get all output schema models."""
    return TOOL_OUTPUT_SCHEMAS.copy()
