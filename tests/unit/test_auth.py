import pytest
from pydantic import SecretStr

from src.utils.error import AuthenticationError


def test_auth_context_from_environment_reads_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALLURE_API_TOKEN", "env-token")
    monkeypatch.setenv("ALLURE_PROJECT_ID", "42")

    from src.utils.auth import AuthContext

    context = AuthContext.from_environment()

    assert isinstance(context.api_token, SecretStr)
    assert context.api_token.get_secret_value() == "env-token"
    assert context.project_id == 42


def test_auth_context_from_environment_requires_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ALLURE_API_TOKEN", raising=False)
    monkeypatch.delenv("ALLURE_PROJECT_ID", raising=False)

    from src.utils.auth import AuthContext

    with pytest.raises(AuthenticationError, match="ALLURE_API_TOKEN"):
        AuthContext.from_environment()


def test_auth_context_with_overrides_returns_new_instance() -> None:
    from src.utils.auth import AuthContext

    base = AuthContext(api_token=SecretStr("base"), project_id=100)

    updated = base.with_overrides(api_token="override", project_id=200)  # noqa: S106

    assert base.api_token.get_secret_value() == "base"
    assert base.project_id == 100
    assert updated.api_token.get_secret_value() == "override"
    assert updated.project_id == 200


def test_get_auth_context_prefers_runtime_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALLURE_API_TOKEN", "env-token")

    from src.utils.auth import get_auth_context

    context = get_auth_context(api_token="runtime-token")  # noqa: S106

    assert context.api_token.get_secret_value() == "runtime-token"


def test_get_auth_context_falls_back_to_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALLURE_API_TOKEN", "env-token")

    from src.utils.auth import get_auth_context

    context = get_auth_context()

    assert context.api_token.get_secret_value() == "env-token"


def test_get_auth_context_requires_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ALLURE_API_TOKEN", raising=False)

    from src.utils.auth import get_auth_context

    with pytest.raises(AuthenticationError, match="api_token"):
        get_auth_context()


def test_get_auth_context_is_stateless(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALLURE_API_TOKEN", "env-token")

    from src.utils.auth import get_auth_context

    first = get_auth_context(api_token="override")  # noqa: S106
    second = get_auth_context()

    assert first.api_token.get_secret_value() == "override"
    assert second.api_token.get_secret_value() == "env-token"


def test_auth_context_masks_token_in_repr() -> None:
    from src.utils.auth import AuthContext

    context = AuthContext(api_token=SecretStr("secret123"))

    assert "secret123" not in repr(context)
    assert "secret123" not in str(context)
