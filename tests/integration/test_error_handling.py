import pytest
from pydantic import BaseModel, ValidationError
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from src.utils.error import ResourceNotFoundError, agent_hint_handler


# Define a Dummy Model for validation testing
class TestModel(BaseModel):
    id: int
    name: str
    category: str  # Mandatory


# Define a Dummy Endpoint that simulates logic
async def mock_endpoint(request: Request, body: TestModel = None):
    try:
        data = await request.json()
        # Simulate Pydantic validation manually if not using a framework that does it auto
        # In FastMCP/FastAPI, this happens automatically, raising ValidationError
        TestModel(**data)

        # Simulate Business Logic Error
        if data.get("id") == 999:
            raise ResourceNotFoundError(message="Item 999 not found", suggestions=["Try ID 1"])

    except ValidationError as e:
        raise e  # Allow bubbling to Exception Handler

    return JSONResponse({"status": "ok"})


@pytest.fixture
def client():
    app = Starlette(
        routes=[Route("/test", mock_endpoint, methods=["POST"])], exception_handlers={Exception: agent_hint_handler}
    )
    return TestClient(app, raise_server_exceptions=False)


def test_pydantic_validation_error_missing_field(client):
    """Test that missing fields return a structured hint."""
    # Missing 'name' and 'category'
    response = client.post("/test", json={"id": 123})

    assert response.status_code == 400
    text = response.text
    assert "❌ Validation Error: Invalid Input" in text
    assert "Field 'name': Field required" in text
    assert "Field 'category': Field required" in text
    assert "Hint: Please correct the fields listed above" in text
    assert "Schema Hint (Expected Format):" in text  # AC #2 requirements


def test_pydantic_validation_error_wrong_type(client):
    """Test that wrong types return a structured hint."""
    # 'id' should be int, passed string
    response = client.post("/test", json={"id": "invalid", "name": "test", "category": "A"})

    assert response.status_code == 400
    text = response.text
    assert "Field 'id': Input should be a valid integer" in text


def test_resource_not_found_error(client):
    """Test that AllureAPIError (ResourceNotFound) is handled correctly."""
    response = client.post("/test", json={"id": 999, "name": "missing", "category": "A"})

    assert response.status_code == 404
    text = response.text
    assert "❌ Error: Item 999 not found" in text
    assert "Suggestions:" in text
    assert "- Try ID 1" in text


def test_malformed_json(client):
    """Test what happens with malformed JSON (Starlette might handle this before us)."""
    # If using TestClient, it encodes dict to json using 'json=' arg.
    # To send bad json, we use 'content='.
    response = client.post("/test", content="{bad_json", headers={"content-type": "application/json"})

    # Starlette usually returns 400 Bad Request for malformed JSON in request.json()
    # It raises JSONDecodeError wrapped possibly.
    # Our handler catches Exception, so it might catch it.

    assert response.status_code in [400, 500]
    # We asserted generic Exception handling in current implementation returns 500 or formatted msg


def test_real_model_validation(client):
    """Test validation with a complex, real-world model (TestCaseCreateV2Dto)."""
    # Import locally to avoid module scope issues if files are moving
    try:
        from src.client.generated.models.test_case_create_v2_dto import TestCaseCreateV2Dto
    except ImportError:
        pytest.skip("Generated models not found")

    # Define a route that uses the real model
    async def real_model_endpoint(request: Request, body: TestCaseCreateV2Dto = None):
        try:
            data = await request.json()
            TestCaseCreateV2Dto(**data)
        except ValidationError as e:
            raise e
        return JSONResponse({"status": "ok"})

    # Determine app from client fixture.
    # Since client fixture creates a new app instance, we need to modify IT or create a new one.
    # We can create a new app for this test.
    app = Starlette(
        routes=[Route("/real_test", real_model_endpoint, methods=["POST"])],
        exception_handlers={Exception: agent_hint_handler},
    )
    c = TestClient(app, raise_server_exceptions=False)

    # 1. Missing required fields (projectId, name)
    # Sending empty JSON
    resp = c.post("/real_test", json={})
    assert resp.status_code == 400
    text = resp.text

    # Check for Pydantic errors
    assert "Field 'projectId': Field required" in text
    assert "Field 'name': Field required" in text

    # Check for Schema Hint (AC #2)
    assert "Schema Hint (Expected Format):" in text
    # Check specific fields exist in hint
    assert "- projectId: int (required)" in text or "- projectId: StrictInt (required)" in text
    assert "- name: str (required)" in text or "- name: StrictStr (required)" in text
    assert "- automated: bool (optional)" in text or "- automated: StrictBool (optional)" in text

    # 2. Strict type check (Str for Int)
    resp = c.post("/real_test", json={"projectId": "not-an-int", "name": "Valid Name"})
    assert resp.status_code == 400
    text = resp.text
    assert "Field 'projectId': Input should be a valid integer" in text


def test_update_nested_validation_error(client):
    """Test Case 4: update_test_case with invalid nested field."""
    # We simulate this using a model that has nested fields, like TestCaseCreateV2Dto or a custom one
    # since TestCasePatchV2Dto typically has optional fields, validation errors come from wrong types.

    class Step(BaseModel):
        name: str
        action: str

    class NestedModel(BaseModel):
        id: int
        steps: list[Step]

    async def nested_endpoint(request: Request):
        try:
            data = await request.json()
            NestedModel(**data)
        except ValidationError as e:
            raise e
        return JSONResponse({"status": "ok"})

    app = Starlette(
        routes=[Route("/nested", nested_endpoint, methods=["POST"])],
        exception_handlers={Exception: agent_hint_handler},
    )
    c = TestClient(app, raise_server_exceptions=False)

    # Missing field in nested object
    response = c.post("/nested", json={"id": 1, "steps": [{"action": "do it"}]})  # 'name' missing
    assert response.status_code == 400
    text = response.text
    # Pydantic v2 loc: steps -> 0 -> name
    assert "Field 'steps -> 0 -> name'" in text
    assert "Field required" in text


def test_hallucinated_extra_fields(client):
    """Test Case 5: create_test_case with hallucinated extra fields (using Extra.forbid)."""
    from pydantic import ConfigDict

    from src.utils.error import ValidationError as MyValidationError
    from src.utils.schema_hint import generate_schema_hint

    # Use AllureValidationError from client.exceptions if available, or simulate the behavior
    # simpler to just raise the base AllureAPIError-like exception structure that handler uses.
    # The handler uses src.utils.error.AllureAPIError subclasses.

    class StrictModel(BaseModel):
        name: str
        model_config = ConfigDict(extra="forbid")

    async def strict_endpoint(request: Request):
        try:
            data = await request.json()
            StrictModel(**data)
        except ValidationError as e:
            # Simulate TestCaseService behavior: catch, hint, wrap
            hint = generate_schema_hint(StrictModel)
            # Use MyValidationError (which inherits AllureAPIError) as wrapper
            raise MyValidationError(f"Invalid data: {e}", suggestions=[hint]) from e
        return JSONResponse({"status": "ok"})

    app = Starlette(
        routes=[Route("/strict", strict_endpoint, methods=["POST"])],
        exception_handlers={Exception: agent_hint_handler},
    )
    c = TestClient(app, raise_server_exceptions=False)

    # Send extra field
    response = c.post("/strict", json={"name": "test", "hallucinated_field": "oops"})
    assert response.status_code == 400
    text = response.text
    # The wrapper message format (Pydantic stringifies the error)
    assert "Invalid data" in text
    assert "hallucinated_field" in text
    assert "Extra inputs are not permitted" in text
    # The hint in suggestions
    assert "Suggestions:" in text
    assert "Schema Hint" in text
    assert "- name: str (required)" in text
    assert "Schema Hint" in text
    assert "- name: str (required)" in text
