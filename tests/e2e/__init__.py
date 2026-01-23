# todo clean up trash
# use unique test cases names
import os

import pytest

# Skip all tests if sandbox environment is not configured
pytestmark = pytest.mark.skipif(
    not (os.getenv("ALLURE_ENDPOINT") and os.getenv("ALLURE_API_TOKEN")),
    reason="Sandbox credentials not configured (ALLURE_ENDPOINT/TOKEN)",
)
