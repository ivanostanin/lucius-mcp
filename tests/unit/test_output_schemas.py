import pytest

from src.tools import all_tools
from src.tools.output_schemas import OUTPUT_MODELS, output_model_for, output_schema_for, validate_registry_coverage


def test_output_schema_registry_covers_registered_tools_exactly() -> None:
    validate_registry_coverage()

    registered_names = {tool.__name__ for tool in all_tools}
    modeled_names = {tool.__name__ for tool in all_tools if output_model_for(tool.__name__)}
    assert registered_names == modeled_names


def test_registered_tools_own_their_output_field_contracts() -> None:
    for tool in all_tools:
        assert getattr(tool, "__lucius_output_fields__", ()), (
            f"{tool.__name__} must declare output fields at its definition site"
        )


def test_registered_schemas_are_concrete_object_schemas() -> None:
    for tool in all_tools:
        schema = output_schema_for(tool.__name__)

        assert schema["type"] == "object"
        assert schema["properties"]
        assert schema.get("additionalProperties") is False
        assert schema != {"type": "object", "properties": {"result": {"type": "string"}}}


def test_every_registered_model_accepts_its_documented_empty_or_confirmation_branch() -> None:
    for tool_name, model in OUTPUT_MODELS.items():
        fields = model.model_fields
        payload: dict[str, object] = {}

        if "items" in fields:
            payload["items"] = []
            if "total" in fields:
                payload["total"] = 0
        if "requires_confirmation" in fields:
            payload.update({"requires_confirmation": True, "action": tool_name})
        if tool_name == "search_test_cases":
            payload.update({"page": 0, "size": 20, "total_pages": 0, "query": ""})

        validated = model.model_validate(payload)
        assert validated.model_dump(mode="json", by_alias=True, exclude_none=True) == payload


def test_search_schema_validates_nested_serialized_payload() -> None:
    model = output_model_for("search_test_cases")

    payload = model.model_validate(
        {
            "total": 1,
            "page": 0,
            "size": 20,
            "total_pages": 1,
            "query": "login",
            "items": [
                {
                    "id": 1,
                    "name": "Login Flow",
                    "status": "unknown",
                    "tags": ["smoke"],
                    "url": "https://example.com/project/1/test-cases/1",
                }
            ],
        }
    )

    assert payload.model_dump(mode="json", by_alias=True) == {
        "total": 1,
        "page": 0,
        "size": 20,
        "total_pages": 1,
        "query": "login",
        "items": [
            {
                "id": 1,
                "name": "Login Flow",
                "status": "unknown",
                "tags": ["smoke"],
                "url": "https://example.com/project/1/test-cases/1",
            }
        ],
    }


@pytest.mark.parametrize(
    ("tool_name", "payload"),
    [
        (
            "list_launches",
            {
                "total": 1,
                "page": 0,
                "size": 20,
                "total_pages": 1,
                "items": [
                    {
                        "id": 7,
                        "name": "Nightly",
                        "closed": False,
                        "created_date": 1_700_000_000_000,
                        "last_modified_date": 1_700_000_100_000,
                        "project_id": 1,
                        "autoclose": True,
                        "external": False,
                        "known_defects_count": 0,
                        "new_defects_count": 1,
                        "manual_execution_guidance": "Use manual execution tools.",
                        "url": "https://example.test/launch/7",
                    }
                ],
            },
        ),
        (
            "list_test_suites",
            {
                "tree": {"id": 1, "name": "Default"},
                "total": 1,
                "items": [{"id": 2, "name": "Parent", "children": [{"id": 3, "name": "Child", "children": []}]}],
            },
        ),
        (
            "list_defect_matchers",
            {
                "defect_id": 4,
                "total": 1,
                "items": [{"id": 5, "name": "Matcher", "message_regex": "boom", "trace_regex": "trace"}],
            },
        ),
        (
            "get_test_case_details",
            {
                "id": 6,
                "name": "Login",
                "status": "Active",
                "tags": [],
                "custom_fields": [{"name": "Layer", "value": "UI"}],
                "attachments": [],
                "steps": [],
            },
        ),
        (
            "unlink_issue_from_test_case",
            {"test_case_id": 8, "issue_id": "PROJ-123", "status": "unlinked", "already_unlinked": False},
        ),
        (
            "create_launch",
            {"id": 9, "name": "Launch", "created_date": 1_700_000_000_000, "closed": False},
        ),
        (
            "delete_archived_test_cases",
            {"requires_confirmation": True, "action": "delete_archived_test_cases"},
        ),
        (
            "delete_archived_shared_steps",
            {"requires_confirmation": True, "action": "delete_archived_shared_steps"},
        ),
        (
            "delete_unused_custom_fields",
            {"requires_confirmation": True, "action": "delete_unused_custom_fields"},
        ),
    ],
)
def test_specialized_models_accept_documented_normal_payloads(tool_name: str, payload: dict[str, object]) -> None:
    model = output_model_for(tool_name)

    validated = model.model_validate(payload)

    assert validated.model_dump(mode="json", by_alias=True, exclude_unset=True) == payload
