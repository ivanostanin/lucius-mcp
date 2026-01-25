import pytest
from pydantic import SecretStr

from src.utils import auth
from src.utils.config import Settings
from src.utils.error import AuthenticationError


def _refresh_auth_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(auth, "settings", Settings())


def test_auth_context_from_environment_reads_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALLURE_API_TOKEN", "env-token")
    monkeypatch.setenv("ALLURE_PROJECT_ID", "42")
    _refresh_auth_settings(monkeypatch)

    context = auth.AuthContext.from_environment()

    assert isinstance(context.api_token, SecretStr)
    assert context.api_token.get_secret_value() == "env-token"
    assert context.project_id == 42


def test_auth_context_from_environment_requires_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ALLURE_API_TOKEN", raising=False)
    monkeypatch.delenv("ALLURE_PROJECT_ID", raising=False)
    _refresh_auth_settings(monkeypatch)

    with pytest.raises(AuthenticationError, match="ALLURE_API_TOKEN"):
        auth.AuthContext.from_environment()


def test_auth_context_with_overrides_returns_new_instance() -> None:
    base = auth.AuthContext(api_token=SecretStr("base"), project_id=100)

    updated = base.with_overrides(api_token="override", project_id=200)  # noqa: S106

    assert base.api_token.get_secret_value() == "base"
    assert base.project_id == 100
    assert updated.api_token.get_secret_value() == "override"
    assert updated.project_id == 200


def test_get_auth_context_prefers_runtime_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALLURE_API_TOKEN", "env-token")
    _refresh_auth_settings(monkeypatch)

    context = auth.get_auth_context(api_token="runtime-token")  # noqa: S106

    assert context.api_token.get_secret_value() == "runtime-token"


def test_get_auth_context_falls_back_to_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALLURE_API_TOKEN", "env-token")
    _refresh_auth_settings(monkeypatch)

    context = auth.get_auth_context()

    assert context.api_token.get_secret_value() == "env-token"


def test_get_auth_context_requires_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ALLURE_API_TOKEN", raising=False)
    _refresh_auth_settings(monkeypatch)

    with pytest.raises(AuthenticationError, match="api_token"):
        auth.get_auth_context()


def test_get_auth_context_is_stateless(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALLURE_API_TOKEN", "env-token")
    _refresh_auth_settings(monkeypatch)

    first = auth.get_auth_context(api_token="override")  # noqa: S106
    second = auth.get_auth_context()

    assert first.api_token.get_secret_value() == "override"
    assert second.api_token.get_secret_value() == "env-token"


def test_auth_context_masks_token_in_repr() -> None:
    context = auth.AuthContext(api_token=SecretStr("secret123"))

    assert "secret123" not in repr(context)
    assert "secret123" not in str(context)


def test_auth_context_token_masked_in_actual_logs(caplog: pytest.LogCaptureFixture) -> None:
    """Integration test: verify token masking in actual log output (AC#6)."""
    import logging

    # Enable logging capture
    caplog.set_level(logging.INFO)

    logger = logging.getLogger("test_logger")
    context = auth.AuthContext(api_token=SecretStr("secret123"))

    # Log the context
    logger.info("Auth context created: %s", context)

    # Verify the actual secret token does NOT appear in logs
    assert "secret123" not in caplog.text
    # SecretStr masks itself in repr/str, so the raw token should never appear
