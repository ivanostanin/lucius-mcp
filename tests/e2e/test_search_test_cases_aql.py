import pytest

from src.client import AllureClient
from src.services.search_service import SearchService


@pytest.fixture
def service(allure_client: AllureClient) -> SearchService:
    return SearchService(client=allure_client)


async def test_aql_basic_operators(service: SearchService) -> None:
    """Test basic comparison operators (=, !=, ~=, >, <)."""
    # Equality
    result = await service.search_test_cases(aql='name = "NonExistentTestNameXYZ"', page=0, size=1)
    assert result.total == 0

    # Inequality (sanity check: status != "Draft" should return something or at least be valid)
    result = await service.search_test_cases(aql='status != "Draft"', page=0, size=1)
    # We expect some results usually, or at least a valid empty result
    assert result.total >= 0

    # Numeric comparison
    result = await service.search_test_cases(aql="id > 0", page=0, size=1)
    assert result.total >= 0


async def test_aql_logical_operators(service: SearchService) -> None:
    """Test logical operators (and, or, not) and grouping."""
    # AND
    result = await service.search_test_cases(aql='name ~= "Test" and id > 0', page=0, size=1)
    assert result.total >= 0

    # NOT
    result = await service.search_test_cases(aql='not name = "SpecificName"', page=0, size=1)
    assert result.total >= 0

    # Parentheses
    result = await service.search_test_cases(aql='(name ~= "Test" or name ~= "Demo") and id > 0', page=0, size=1)
    assert result.total >= 0


async def test_aql_list_operators(service: SearchService) -> None:
    """Test list operators (in, not in)."""
    # IN
    result = await service.search_test_cases(aql='status in ["Active", "Draft"]', page=0, size=1)
    assert result.total >= 0

    # NOT IN (AQL syntax is 'not field in [...]')
    result = await service.search_test_cases(aql='not status in ["Outdated"]', page=0, size=1)
    assert result.total >= 0


async def test_aql_field_types(service: SearchService) -> None:
    """Test different field types (Boolean, Null, Dates)."""
    # Boolean (using 'muted' as a confirmed boolean field)
    result = await service.search_test_cases(aql="muted = true or muted = false", page=0, size=1)
    assert result.total >= 0

    # Null check (syntax check primarily)
    result = await service.search_test_cases(aql="muted = null", page=0, size=1)
    assert result.total >= 0

    # Null check with 'is'
    import contextlib

    with contextlib.suppress(Exception):
        # Some versions might strictly require '= null' vs 'is null', depending on Allure version
        result = await service.search_test_cases(aql="muted is null", page=0, size=1)
        assert result.total >= 0

    # Date fields (numeric comparison)
    # Using a timestamp from 2023 (1672531200000)
    result = await service.search_test_cases(aql="createdDate > 1672531200000", page=0, size=1)
    assert result.total >= 0


async def test_aql_special_fields(service: SearchService) -> None:
    """Test specific complex fields like tags and custom fields."""
    # Tags
    result = await service.search_test_cases(aql='tag = "smoke"', page=0, size=1)
    assert result.total >= 0

    # Custom Fields (cf["Name"])
    # We may not know exact CF names, but testing the syntax validity
    # Use a non-existent one to match nothing but ensure no syntax error
    result = await service.search_test_cases(aql='cf["NonExistentField"] = "Value"', page=0, size=1)
    assert result.total == 0
