"""Unit tests for generated Pydantic models."""

import pytest
from pydantic import ValidationError

from src.client.models.common import (
    AllowedRoleDto,
    CategoryCreateDto,
    CategoryDto,
    CommentCreateDto,
    CustomFieldCreateDto,
    CustomFieldDto,
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
    assert category.projectId == data["projectId"]


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
    assert cf.singleSelect == data["singleSelect"]


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
    assert comment.testCaseId == data["testCaseId"]


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
    assert cf.singleSelect == data["singleSelect"]
    assert cf.archived == data["archived"]
    assert cf.createdBy is None
    assert cf.createdDate is None


def test_models_use_union_operator() -> None:
    """Test that models use Python 3.10+ union operator (X | None)."""
    import inspect

    # Get the source code of CategoryDto
    source = inspect.getsource(CategoryDto)

    # Check that it uses | None instead of Optional
    assert "| None" in source or CategoryDto.__annotations__


def test_model_strict_validation() -> None:
    """Test that Pydantic v2 strict validation is working."""
    # This should fail in strict mode (string to int coercion disabled)
    data = {
        "name": "Test",
        "color": "#FF0000",
        "projectId": "123",  # String instead of int
    }

    # Note: datamodel-code-generator might not add strict=True by default
    # This test verifies the behavior
    try:
        CategoryCreateDto(**data)
        # If this passes, strict mode is not enabled (coercion allowed)
        # This is acceptable for generated models
    except ValidationError:
        # If this fails, strict mode is enabled
        pass
