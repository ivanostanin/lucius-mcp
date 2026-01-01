import pytest
from starlette.testclient import TestClient


@pytest.fixture
def client(app):
    """
    Returns a Starlette TestClient instance using the refreshed app fixture.
    """
    with TestClient(app) as test_client:
        yield test_client
