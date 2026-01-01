import json
import logging

import pytest

from src.utils.logger import CustomJsonEncoder, CustomJsonFormatter


@pytest.fixture
def capture_structured_logs():
    """
    Fixture that configures logging to capture records in memory
    and provides a helper to retrieve and parse them.
    """
    # Configure root logger with a clean state
    root = logging.getLogger()
    root.setLevel("DEBUG")

    # Remove existing handlers to avoid interference (e.g. stderr stream from src/utils/logger.py)
    old_handlers = list(root.handlers)
    for h in root.handlers:
        root.removeHandler(h)

    # Create in-memory handler
    class ListHandler(logging.Handler):
        def __init__(self):
            super().__init__()
            self.records = []

        def emit(self, record):
            self.records.append(record)

    memory_handler = ListHandler()

    # We still need the formatter to test formatting logic (JSON structure)
    formatter = CustomJsonFormatter(
        "%(timestamp)s %(level)s %(logger)s %(message)s %(context)s %(request_id)s", json_encoder=CustomJsonEncoder
    )
    memory_handler.setFormatter(formatter)

    root.addHandler(memory_handler)

    def get_logs():
        """Returns a list of parsed JSON log entries."""
        logs = []
        for record in memory_handler.records:
            # Format the record to get the JSON string string
            log_str = memory_handler.format(record)
            try:
                logs.append(json.loads(log_str))
            except json.JSONDecodeError:
                pass
        return logs

    yield get_logs

    # Cleanup: restore handlers
    root.removeHandler(memory_handler)
    for h in old_handlers:
        root.addHandler(h)
