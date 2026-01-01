import json
import logging
from collections.abc import Callable, Generator

import pytest

from src.utils.logger import CustomJsonEncoder, CustomJsonFormatter


class ListHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


@pytest.fixture
def capture_structured_logs() -> Generator[Callable[[], list[dict[str, object]]]]:
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
    memory_handler = ListHandler()

    # We still need the formatter to test formatting logic (JSON structure)
    formatter = CustomJsonFormatter(
        "%(timestamp)s %(level)s %(logger)s %(message)s %(context)s %(request_id)s", json_encoder=CustomJsonEncoder
    )
    memory_handler.setFormatter(formatter)

    root.addHandler(memory_handler)

    def get_logs() -> list[dict[str, object]]:
        """Returns a list of parsed JSON log entries."""
        logs: list[dict[str, object]] = []
        for record in memory_handler.records:
            # Format the record to get the JSON string string
            log_str = memory_handler.format(record)
            try:
                # json.loads returns Any, we cast it to Dict[str, object] for strictness if we expect a dict
                parsed = json.loads(log_str)
                if isinstance(parsed, dict):
                    logs.append(parsed)
            except json.JSONDecodeError:
                pass
        return logs

    yield get_logs

    # Cleanup: restore handlers
    root.removeHandler(memory_handler)
    for h in old_handlers:
        root.addHandler(h)
