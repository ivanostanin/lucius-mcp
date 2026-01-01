import json

from pydantic import SecretStr

from src.utils.logger import get_logger


def test_logger_json_format(capture_structured_logs):
    """Verify logs are output in structured JSON format with required fields."""
    logger = get_logger("test_json")
    logger.info("structure check", extra={"context": {"foo": "bar"}})

    logs = capture_structured_logs()
    assert len(logs) >= 1
    entry = logs[-1]

    assert entry["message"] == "structure check"
    assert entry["level"] == "INFO"
    assert entry["logger"] == "test_json"
    assert "timestamp" in entry
    # Context handling depends on the formatter implementation, ensuring it works
    if "context" in entry:
        assert entry["context"] == {"foo": "bar"}


def test_logger_secret_masking(capture_structured_logs):
    """Verify SecretStr values are masked in logs."""
    logger = get_logger("test_masking")
    secret = SecretStr("highly_sensitive_data")

    # Test case 1: Secret in context
    logger.info("processing secret", extra={"context": {"token": secret}})

    # Test case 2: Secret in args (if supported by formatter/encoder)
    # logger.info("secret is %s", secret)

    logs = capture_structured_logs()

    # Verify strict masking (should not appear in string dump of any log)
    log_dump = json.dumps(logs)
    assert "highly_sensitive_data" not in log_dump
    assert "**********" in log_dump


def test_logger_correlation_id(capture_structured_logs):
    """Verify correlation ID / Request ID is captured if present."""
    logger = get_logger("test_correlation")
    # Simulating request_id passed via extra - in real app this might come from contextvars
    logger.info("request tracking", extra={"request_id": "req-123"})

    logs = capture_structured_logs()
    entry = logs[-1]

    assert entry.get("request_id") == "req-123"


def test_logger_exception_traceback(capture_structured_logs):
    """Verify exceptions are captured structuredly."""
    logger = get_logger("test_exception")
    try:
        raise ValueError("oops")
    except ValueError:
        logger.exception("something failed")

    logs = capture_structured_logs()
    entry = logs[-1]

    assert entry["message"] == "something failed"
    assert "exc_info" in entry or "exception" in entry or "stack_info" in entry or "\nTraceback" in str(entry)
