from collections.abc import Generator

import pytest
from starlette.applications import Starlette
from starlette.testclient import TestClient


@pytest.fixture
def client(app: Starlette) -> Generator[TestClient]:
    """
    Returns a Starlette TestClient instance using the refreshed app fixture.
    """
    with TestClient(app) as test_client:
        yield test_client
