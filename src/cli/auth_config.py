"""Persistent CLI auth configuration helpers."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from collections.abc import MutableMapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import platformdirs
from pydantic import SecretStr

from src.cli.models import CLIError

AUTH_CONFIG_FILENAME = "auth.json"
AUTH_ENDPOINT_ENV = "ALLURE_ENDPOINT"
AUTH_TOKEN_ENV = "ALLURE_API_TOKEN"  # noqa: S105
AUTH_PROJECT_ENV = "ALLURE_PROJECT_ID"


@dataclass(frozen=True)
class AuthConfig:
    """Saved CLI auth configuration."""

    allure_endpoint: str
    allure_api_token: str
    allure_project_id: int
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, object]:
        return {
            "allure_endpoint": self.allure_endpoint,
            "allure_api_token": self.allure_api_token,
            "allure_project_id": self.allure_project_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


def auth_config_path() -> Path:
    """Return the native per-user CLI auth config path."""
    config_dir = Path(platformdirs.user_config_path("lucius", appauthor=False, ensure_exists=True))
    return config_dir / AUTH_CONFIG_FILENAME


def current_timestamp() -> str:
    """Return an ISO-8601 UTC timestamp for config metadata."""
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _repair_hint(path: Path) -> str:
    return f"Repair or remove {path} and run 'lucius auth' again."


def _is_missing_env_var(name: str, environ: MutableMapping[str, str]) -> bool:
    value = environ.get(name)
    return value is None or value == ""


def _parse_project_id(raw_value: object, *, path: Path) -> int:
    if isinstance(raw_value, bool) or not isinstance(raw_value, int) or raw_value <= 0:
        raise CLIError(
            "Saved CLI auth config has an invalid project ID.",
            hint=_repair_hint(path),
            exit_code=1,
        )
    return raw_value


def _validate_config_value(raw_value: object, *, field_name: str, path: Path) -> str:
    if not isinstance(raw_value, str) or not raw_value.strip():
        raise CLIError(
            f"Saved CLI auth config has an invalid '{field_name}' value.",
            hint=_repair_hint(path),
            exit_code=1,
        )
    return raw_value.strip()


def load_auth_config(path: Path | None = None) -> AuthConfig | None:
    """Load and validate the saved CLI auth config."""
    resolved_path = path or auth_config_path()
    if not resolved_path.exists():
        return None

    try:
        raw_data = json.loads(resolved_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        raise CLIError(
            "Saved CLI auth config is malformed JSON.",
            hint=_repair_hint(resolved_path),
            exit_code=1,
        ) from None
    except OSError as error:
        raise CLIError(
            f"Failed to read saved CLI auth config: {error}",
            hint=f"Check read permissions for {resolved_path}.",
            exit_code=1,
        ) from None

    if not isinstance(raw_data, dict):
        raise CLIError(
            "Saved CLI auth config must contain a JSON object.",
            hint=_repair_hint(resolved_path),
            exit_code=1,
        )

    required_fields = {
        "allure_endpoint",
        "allure_api_token",
        "allure_project_id",
        "created_at",
        "updated_at",
    }
    missing_fields = sorted(field for field in required_fields if field not in raw_data)
    if missing_fields:
        missing = ", ".join(missing_fields)
        raise CLIError(
            f"Saved CLI auth config is missing required fields: {missing}.",
            hint=_repair_hint(resolved_path),
            exit_code=1,
        )

    endpoint = _validate_config_value(raw_data["allure_endpoint"], field_name="allure_endpoint", path=resolved_path)
    token = _validate_config_value(raw_data["allure_api_token"], field_name="allure_api_token", path=resolved_path)
    created_at = _validate_config_value(raw_data["created_at"], field_name="created_at", path=resolved_path)
    updated_at = _validate_config_value(raw_data["updated_at"], field_name="updated_at", path=resolved_path)
    project_id = _parse_project_id(raw_data["allure_project_id"], path=resolved_path)

    return AuthConfig(
        allure_endpoint=endpoint.rstrip("/"),
        allure_api_token=token,
        allure_project_id=project_id,
        created_at=created_at,
        updated_at=updated_at,
    )


def _ensure_directory_permissions(directory: Path) -> None:
    if os.name == "nt":
        return
    try:
        os.chmod(directory, 0o700)
    except OSError:
        # Best effort only; some filesystems ignore directory chmod semantics.
        return


def _set_file_permissions(path: Path) -> None:
    if os.name == "nt":
        return
    try:
        os.chmod(path, 0o600)
    except OSError as error:
        raise CLIError(
            f"Failed to secure saved CLI auth config permissions: {error}",
            hint=f"Check write permissions for {path.parent}.",
            exit_code=1,
        ) from None


def save_auth_config(
    *,
    url: str,
    token: str,
    project_id: int,
    path: Path | None = None,
    now: str | None = None,
) -> Path:
    """Persist CLI auth config with atomic replacement semantics."""
    resolved_path = path or auth_config_path()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    _ensure_directory_permissions(resolved_path.parent)

    existing = None
    try:
        existing = load_auth_config(resolved_path)
    except CLIError:
        existing = None

    timestamp = now or current_timestamp()
    config = AuthConfig(
        allure_endpoint=url.rstrip("/"),
        allure_api_token=token,
        allure_project_id=project_id,
        created_at=existing.created_at if existing else timestamp,
        updated_at=timestamp,
    )
    payload = json.dumps(config.to_dict(), indent=2, sort_keys=True) + "\n"

    temp_path: Path | None = None
    try:
        fd, raw_temp_path = tempfile.mkstemp(prefix=".auth.", suffix=".tmp", dir=str(resolved_path.parent))
        temp_path = Path(raw_temp_path)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        _set_file_permissions(temp_path)
        temp_path.replace(resolved_path)
    except OSError as error:
        raise CLIError(
            f"Failed to write saved CLI auth config: {error}",
            hint=f"Check write permissions for {resolved_path.parent}.",
            exit_code=1,
        ) from None
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()

    return resolved_path


def apply_saved_auth_environment(environ: MutableMapping[str, str] | None = None) -> AuthConfig | None:
    """Load saved auth config and inject it into missing environment variables."""
    resolved_environ = os.environ if environ is None else environ
    config = load_auth_config()
    if config is None:
        return None

    update_endpoint = _is_missing_env_var(AUTH_ENDPOINT_ENV, resolved_environ)
    update_token = _is_missing_env_var(AUTH_TOKEN_ENV, resolved_environ)
    update_project = _is_missing_env_var(AUTH_PROJECT_ENV, resolved_environ)

    if update_endpoint:
        resolved_environ[AUTH_ENDPOINT_ENV] = config.allure_endpoint
    if update_token:
        resolved_environ[AUTH_TOKEN_ENV] = config.allure_api_token
    if update_project:
        resolved_environ[AUTH_PROJECT_ENV] = str(config.allure_project_id)

    config_module = sys.modules.get("src.utils.config")
    if config_module is not None:
        settings = getattr(config_module, "settings", None)
        if settings is not None:
            if update_endpoint:
                setattr(settings, AUTH_ENDPOINT_ENV, config.allure_endpoint)
            if update_token:
                setattr(settings, AUTH_TOKEN_ENV, SecretStr(config.allure_api_token))
            if update_project:
                setattr(settings, AUTH_PROJECT_ENV, config.allure_project_id)

    return config
