"""Resolve Allure auth inputs across runtime args, env, saved CLI auth, and defaults."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

from pydantic import SecretStr

from src.cli.auth_config import AuthConfig, load_auth_config
from src.utils.auth_constants import ALLURE_API_TOKEN_ENV, ALLURE_ENDPOINT_ENV, ALLURE_PROJECT_ID_ENV
from src.utils.config import Settings, get_current_settings


@dataclass(frozen=True)
class ResolvedAuthSettings:
    """Fully resolved auth settings for CLI and tool execution."""

    endpoint: str | None
    api_token: SecretStr | None
    project_id: int | None


def _env_has_value(environ: Mapping[str, str], name: str) -> bool:
    return name in environ


def _load_saved_auth_if_needed(
    *,
    environ: Mapping[str, str],
    explicit_api_token: str | None,
    explicit_project_id: int | None,
    include_endpoint: bool,
    include_api_token: bool,
    include_project_id: bool,
) -> AuthConfig | None:
    needs_saved_endpoint = include_endpoint and not _env_has_value(environ, ALLURE_ENDPOINT_ENV)
    needs_saved_token = (
        include_api_token and explicit_api_token is None and not _env_has_value(environ, ALLURE_API_TOKEN_ENV)
    )
    needs_saved_project = (
        include_project_id and explicit_project_id is None and not _env_has_value(environ, ALLURE_PROJECT_ID_ENV)
    )
    if not any((needs_saved_endpoint, needs_saved_token, needs_saved_project)):
        return None
    return load_auth_config()


def _resolve_endpoint(*, environ: Mapping[str, str], settings: Settings, saved_config: AuthConfig | None) -> str | None:
    if _env_has_value(environ, ALLURE_ENDPOINT_ENV):
        return environ[ALLURE_ENDPOINT_ENV]
    if saved_config is not None:
        return saved_config.allure_endpoint
    return settings.ALLURE_ENDPOINT


def _resolve_api_token(
    *,
    explicit_api_token: str | None,
    environ: Mapping[str, str],
    settings: Settings,
    saved_config: AuthConfig | None,
) -> SecretStr | None:
    if explicit_api_token:
        return SecretStr(explicit_api_token)
    if _env_has_value(environ, ALLURE_API_TOKEN_ENV):
        raw_token = environ[ALLURE_API_TOKEN_ENV]
        return SecretStr(raw_token) if raw_token else None
    if saved_config is not None:
        return SecretStr(saved_config.allure_api_token)
    return settings.ALLURE_API_TOKEN


def _parse_project_id_from_env(raw_value: str) -> int | None:
    stripped = raw_value.strip()
    if not stripped:
        return None
    try:
        project_id = int(stripped)
    except ValueError:
        raise ValueError("ALLURE_PROJECT_ID must be a positive integer") from None
    if project_id <= 0:
        raise ValueError("ALLURE_PROJECT_ID must be a positive integer")
    return project_id


def _resolve_project_id(
    *,
    explicit_project_id: int | None,
    environ: Mapping[str, str],
    settings: Settings,
    saved_config: AuthConfig | None,
) -> int | None:
    if explicit_project_id is not None:
        return explicit_project_id
    if _env_has_value(environ, ALLURE_PROJECT_ID_ENV):
        return _parse_project_id_from_env(environ[ALLURE_PROJECT_ID_ENV])
    if saved_config is not None:
        return saved_config.allure_project_id
    return settings.ALLURE_PROJECT_ID


def resolve_auth_settings(
    *,
    api_token: str | None = None,
    project_id: int | None = None,
    environ: Mapping[str, str] | None = None,
    include_endpoint: bool = True,
    include_api_token: bool = True,
    include_project_id: bool = True,
) -> ResolvedAuthSettings:
    """Resolve auth values with precedence: args > env > saved CLI auth > defaults."""
    resolved_environ = os.environ if environ is None else environ
    current_settings = get_current_settings()
    saved_config = _load_saved_auth_if_needed(
        environ=resolved_environ,
        explicit_api_token=api_token,
        explicit_project_id=project_id,
        include_endpoint=include_endpoint,
        include_api_token=include_api_token,
        include_project_id=include_project_id,
    )
    return ResolvedAuthSettings(
        endpoint=(
            _resolve_endpoint(environ=resolved_environ, settings=current_settings, saved_config=saved_config)
            if include_endpoint
            else None
        ),
        api_token=_resolve_api_token(
            explicit_api_token=api_token,
            environ=resolved_environ,
            settings=current_settings,
            saved_config=saved_config,
        )
        if include_api_token
        else None,
        project_id=_resolve_project_id(
            explicit_project_id=project_id,
            environ=resolved_environ,
            settings=current_settings,
            saved_config=saved_config,
        )
        if include_project_id
        else None,
    )
