from starlette.testclient import TestClient

# Import will fail until implemented
from src.main import app

client = TestClient(app)


def test_app_initialization():
    assert app is not None

    with TestClient(app) as client:
        response = client.get("/mcp")
        assert response.status_code != 404
