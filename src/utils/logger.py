import datetime
import logging
import sys

from pydantic import SecretStr
from pythonjsonlogger import json


# Custom JSON encoder to handle SecretStr and other types
class CustomJsonEncoder(json.JsonEncoder):
    def default(self, obj: object) -> object:
        if isinstance(obj, SecretStr):
            return "**********"
        return super().default(obj)


class CustomJsonFormatter(json.JsonFormatter):
    def add_fields(
        self, log_record: dict[str, object], record: logging.LogRecord, message_dict: dict[str, object]
    ) -> None:
        super().add_fields(log_record, record, message_dict)

        # Ensure consistent timestamp format
        if not log_record.get("timestamp"):
            now = datetime.datetime.fromtimestamp(record.created, datetime.UTC)
            log_record["timestamp"] = now.isoformat()

        log_record["level"] = record.levelname
        log_record["logger"] = record.name

        # Move extra fields to 'context' if not already present
        # This implementation depends on how fields are passed.
        # python-json-logger usually merges extra into log_record.
        # We want structured 'context' if possible.

        # Masking logic handles by the Encoder during dump,
        # but if we want to manipulate structure, we do it here.


def configure_logging(log_level: str = "INFO") -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplication during tests/reloads
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stderr)  # Log to stderr by default

    # Define the fields we want to capture explicitly
    formatter = CustomJsonFormatter(
        "%(timestamp)s %(level)s %(logger)s %(message)s %(context)s %(request_id)s", json_encoder=CustomJsonEncoder
    )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
