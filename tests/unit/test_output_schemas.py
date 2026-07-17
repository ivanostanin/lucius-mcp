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
