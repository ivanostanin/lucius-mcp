import json
import logging
import pytest
from pydantic import SecretStr

# Import will fail until implemented
from src.utils.logger import configure_logging, get_logger


def test_logger_json_format(capsys):
    configure_logging()
    logger = get_logger("test_logger")
    logger.info("test message", extra={"context": {"key": "value"}})

    # Force flush
    for handler in logger.handlers:
        handler.flush()

    captured = capsys.readouterr()
    # Depending on configuration, it might go to stderr or stdout
    output = captured.err if captured.err else captured.out

    assert output, "No log output captured"
    log_entry = json.loads(output.strip())

    assert log_entry["message"] == "test message"
    assert log_entry["level"] == "INFO"
    assert log_entry["logger"] == "test_logger"
    assert "timestamp" in log_entry
    assert log_entry["context"] == {"key": "value"}


def test_logger_secret_masking(capsys):
    configure_logging()
    logger = get_logger("test_logger")
    secret = SecretStr("super_secret_token")

    # Log directly as argument or in context
    logger.info("Processing", extra={"context": {"token": secret}})

    captured = capsys.readouterr()
    output = captured.err if captured.err else captured.out
    log_entry = json.loads(output.strip())

    log_str = json.dumps(log_entry)
    assert "super_secret_token" not in log_str
    assert "**********" in log_str or "******" in log_str
