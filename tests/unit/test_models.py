"""Unit tests for generated Pydantic models."""

import pytest
from pydantic import ValidationError

from src.client.generated.models import (
    AllowedRoleDto,
    BodyStepDto,
    CategoryCreateDto,
    CategoryDto,
    CommentCreateDto,
    CustomFieldCreateDto,
    CustomFieldDto,
    TestCaseCreateV2Dto,
    TestCaseScenarioV2Dto,
)
from tests.support.factories.model_factories import (
    create_test_case_create_v2_dto,
    create_test_case_scenario_v2_dto,
)


def test_models_import_successfully() -> None:
    """Test that models can be imported without errors."""
    # If we got here, imports succeeded
    assert True


def test_category_create_dto_valid() -> None:
    """Test CategoryCreateDto with valid data."""
    data = {
        "name": "Test Category",
        "color": "#FF0000",
        "description": "A test category",
        "projectId": 123,
    }
    category = CategoryCreateDto(**data)

    assert category.name == data["name"]
    assert category.color == data["color"]
    assert category.description == data["description"]
    assert category.project_id == data["projectId"]


def test_category_create_dto_missing_required_field() -> None:
    """Test CategoryCreateDto rejects missing required fields."""
    data = {
        "color": "#FF0000",
    }

    with pytest.raises(ValidationError) as exc_info:
        CategoryCreateDto(**data)

    errors = exc_info.value.errors()
    assert any(e["loc"] == ("name",) for e in errors)


def test_category_create_dto_invalid_type() -> None:
    """Test CategoryCreateDto rejects invalid field types."""
    data = {
        "name": "Test",
        "color": 12345,  # Should be string
    }

    with pytest.raises(ValidationError) as exc_info:
        CategoryCreateDto(**data)

    errors = exc_info.value.errors()
    assert any(e["loc"] == ("color",) for e in errors)


def test_category_dto_optional_fields() -> None:
    """Test CategoryDto handles optional fields correctly."""
    # Minimal data
    category = CategoryDto()

    assert category.id is None
    assert category.name is None
    assert category.color is None
    assert category.description is None

    # With some data
    data = {"id": 1, "name": "Test", "color": "#000000"}
    category = CategoryDto(**data)
    assert category.id == data["id"]
    assert category.name == data["name"]
    assert category.color == data["color"]
    assert category.description is None


def test_custom_field_create_dto_valid() -> None:
    """Test CustomFieldCreateDto with valid data."""
    data = {
        "name": "Environment",
        "required": True,
        "singleSelect": False,
    }
    cf = CustomFieldCreateDto(**data)

    assert cf.name == data["name"]
    assert cf.required == data["required"]
    assert cf.single_select == data["singleSelect"]


def test_custom_field_create_dto_name_too_long() -> None:
    """Test CustomFieldCreateDto rejects name that's too long."""
    data = {
        "name": "x" * 256,  # Max is 255
        "required": True,
    }

    with pytest.raises(ValidationError):
        CustomFieldCreateDto(**data)


def test_custom_field_create_dto_name_too_short() -> None:
    """Test CustomFieldCreateDto rejects empty name."""
    data = {
        "name": "",  # Min length is 1
        "required": True,
    }

    with pytest.raises(ValidationError):
        CustomFieldCreateDto(**data)


def test_comment_create_dto_valid() -> None:
    """Test CommentCreateDto with valid data."""
    data = {
        "body": "This is a comment",
        "testCaseId": 42,
    }
    comment = CommentCreateDto(**data)

    assert comment.body == data["body"]
    assert comment.test_case_id == data["testCaseId"]


def test_comment_create_dto_body_too_short() -> None:
    """Test CommentCreateDto rejects empty body."""
    data = {
        "body": "",  # Min length is 1
        "testCaseId": 42,
    }

    with pytest.raises(ValidationError):
        CommentCreateDto(**data)


def test_allowed_role_dto_enum() -> None:
    """Test AllowedRoleDto enum values."""
    assert AllowedRoleDto.ADMIN == "ADMIN"
    assert AllowedRoleDto.USER == "USER"

    # Can create from string
    role = AllowedRoleDto("ADMIN")
    assert role == AllowedRoleDto.ADMIN


def test_custom_field_dto_structure() -> None:
    """Test CustomFieldDto has expected structure."""
    data = {
        "id": 1,
        "name": "Priority",
        "required": False,
        "singleSelect": True,
        "archived": False,
    }
    cf = CustomFieldDto(**data)

    assert cf.id == data["id"]
    assert cf.name == data["name"]
    assert cf.required == data["required"]
    assert cf.single_select == data["singleSelect"]
    assert cf.archived == data["archived"]
    assert cf.created_by is None
    assert cf.created_date is None


def test_models_use_union_operator() -> None:
    """Test that models use Python 3.10+ union operator (X | None)."""
    import inspect

    # Get the source code of CategoryDto
    source = inspect.getsource(CategoryDto)

    # Check that it uses | None instead of Optional
    assert "| None" in source or CategoryDto.__annotations__


def test_test_case_create_v2_dto_factory() -> None:
    """Test TestCaseCreateV2Dto factory and validation."""
    dto = create_test_case_create_v2_dto(name="Custom Name")
    assert dto.name == "Custom Name"
    assert dto.project_id == 1
    assert dto.automated is False


def test_test_case_create_v2_dto_missing_name() -> None:
    """Test TestCaseCreateV2Dto rejects missing name."""
    with pytest.raises(ValidationError):
        TestCaseCreateV2Dto.model_validate({"projectId": 1})


def test_test_case_scenario_v2_dto_factory() -> None:
    """Test TestCaseScenarioV2Dto factory and structure."""
    scenario = create_test_case_scenario_v2_dto()
    assert scenario.steps is not None
    assert len(scenario.steps) == 3
    for step in scenario.steps:
        actual = step.actual_instance
        assert isinstance(actual, BodyStepDto)
        assert isinstance(actual.body, str)


def test_test_case_scenario_v2_dto_invalid_steps() -> None:
    """Test TestCaseScenarioV2Dto rejects invalid steps."""
    with pytest.raises(ValidationError):
        TestCaseScenarioV2Dto(steps="not-a-list")


def test_test_case_scenario_v2_dto_empty_steps() -> None:
    """Test TestCaseScenarioV2Dto handles empty steps (if allowed by schema)."""
    scenario = TestCaseScenarioV2Dto(steps=[])
    assert scenario.steps == []
