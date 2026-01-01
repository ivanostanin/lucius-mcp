import pytest
from faker import Faker

# Shared faker instance
fake = Faker()


@pytest.fixture(scope="session")
def faker():
    return fake
