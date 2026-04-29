# ruff: noqa: S105,S106,S108
"""Tests for the CLI-local auth command and saved-config fallback behavior."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path
from textwrap import dedent
from unittest.mock import AsyncMock, patch

import pytest

from src.cli import cli_entry
from src.cli.auth_command import _map_auth_validation_error, parse_auth_command_options
from src.cli.auth_config import (
    AUTH_ENDPOINT_ENV,
    AUTH_PROJECT_ENV,
    AUTH_TOKEN_ENV,
    apply_saved_auth_environment,
    auth_config_path,
    clear_auth_config,
    load_auth_config,
    save_auth_config,
)
from src.cli.cli_entry import run_cli as run_cli_in_process
from src.cli.models import CLIError
from src.cli.route_matrix import CANONICAL_ROUTE_MATRIX
from src.cli.schema_loader import load_tool_schemas
from src.utils.auth import get_auth_context
from tests.cli.subprocess_helpers import run_cli, run_uv_cli


def _sitecustomize_dir(tmp_path: Path, body: str) -> Path:
    directory = tmp_path / "sitecustomize"
    directory.mkdir()
    (directory / "sitecustomize.py").write_text(dedent(body), encoding="utf-8")
    return directory


def _subprocess_env(tmp_path: Path, *, sitecustomize: Path | None = None) -> dict[str, str]:
    env = os.environ.copy()
    env.pop(AUTH_ENDPOINT_ENV, None)
    env.pop(AUTH_TOKEN_ENV, None)
    env.pop(AUTH_PROJECT_ENV, None)
    env["XDG_CONFIG_HOME"] = str(tmp_path / "xdg-config")
    if sitecustomize is not None:
        existing = env.get("PYTHONPATH")
        env["PYTHONPATH"] = str(sitecustomize) if not existing else os.pathsep.join([str(sitecustomize), existing])
    return env


def _write_saved_config(config_root: Path, *, url: str, token: str, project_id: int) -> Path:
    config_dir = config_root / "lucius"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "auth.json"
    config_path.write_text(
        json.dumps(
            {
                "allure_endpoint": url,
                "allure_api_token": token,
                "allure_project_id": project_id,
                "created_at": "2026-04-29T10:00:00Z",
                "updated_at": "2026-04-29T10:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    return config_path


class TestCLIAuthConfig:
    @pytest.mark.parametrize(
        ("platform_path", "expected"),
        [
            (Path("/tmp/xdg/lucius"), Path("/tmp/xdg/lucius/auth.json")),
            (
                Path("/Users/test/Library/Application Support/lucius"),
                Path("/Users/test/Library/Application Support/lucius/auth.json"),
            ),
            (Path("C:/Users/test/AppData/Local/lucius"), Path("C:/Users/test/AppData/Local/lucius/auth.json")),
        ],
    )
    def test_auth_config_path_uses_platformdirs(
        self,
        monkeypatch: pytest.MonkeyPatch,
        platform_path: Path,
        expected: Path,
    ) -> None:
        monkeypatch.setattr("src.cli.auth_config.platformdirs.user_config_path", lambda *args, **kwargs: platform_path)
        assert auth_config_path() == expected

    def test_save_and_load_auth_config_round_trip(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("src.cli.auth_config.platformdirs.user_config_path", lambda *args, **kwargs: tmp_path)
        saved_path = save_auth_config(
            url="https://example.testops.cloud/",
            token="super-secret-token",
            project_id=123,
            now="2026-04-29T10:00:00Z",
        )
        loaded = load_auth_config(saved_path)
        assert saved_path == tmp_path / "auth.json"
        assert loaded is not None
        assert loaded.allure_endpoint == "https://example.testops.cloud"
        assert loaded.allure_api_token == "super-secret-token"
        assert loaded.allure_project_id == 123
        assert loaded.created_at == "2026-04-29T10:00:00Z"
        assert loaded.updated_at == "2026-04-29T10:00:00Z"

    def test_load_auth_config_rejects_malformed_json(self, tmp_path: Path) -> None:
        config_path = tmp_path / "auth.json"
        config_path.write_text("{not-json", encoding="utf-8")
        with pytest.raises(CLIError) as exc_info:
            load_auth_config(config_path)
        assert "malformed json" in exc_info.value.message.lower()
        assert "lucius auth" in (exc_info.value.hint or "")

    def test_load_auth_config_rejects_missing_fields(self, tmp_path: Path) -> None:
        config_path = tmp_path / "auth.json"
        config_path.write_text(json.dumps({"allure_endpoint": "https://example.testops.cloud"}), encoding="utf-8")
        with pytest.raises(CLIError) as exc_info:
            load_auth_config(config_path)
        assert "missing required fields" in exc_info.value.message.lower()

    def test_save_auth_config_calls_posix_permission_helpers(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        chmod_calls: list[tuple[Path, int]] = []

        def _record_chmod(target: str | os.PathLike[str], mode: int) -> None:
            chmod_calls.append((Path(target), mode))

        monkeypatch.setattr("src.cli.auth_config.platformdirs.user_config_path", lambda *args, **kwargs: tmp_path)
        monkeypatch.setattr("src.cli.auth_config.os.chmod", _record_chmod)
        save_auth_config(
            url="https://example.testops.cloud",
            token="token",
            project_id=7,
            now="2026-04-29T10:00:00Z",
        )
        assert any(mode == 0o700 and path == tmp_path for path, mode in chmod_calls)
        assert any(mode == 0o600 and path.name.endswith(".tmp") for path, mode in chmod_calls)

    def test_save_auth_config_keeps_existing_file_on_replace_failure(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        config_path = tmp_path / "auth.json"
        config_path.write_text(
            json.dumps(
                {
                    "allure_endpoint": "https://old.testops.cloud",
                    "allure_api_token": "old-token",
                    "allure_project_id": 1,
                    "created_at": "2026-04-29T09:00:00Z",
                    "updated_at": "2026-04-29T09:00:00Z",
                }
            ),
            encoding="utf-8",
        )

        original_replace = Path.replace

        def _failing_replace(self: Path, target: Path) -> Path:
            if target == config_path:
                raise OSError("disk full")
            return original_replace(self, target)

        monkeypatch.setattr(Path, "replace", _failing_replace)
        with pytest.raises(CLIError):
            save_auth_config(
                url="https://new.testops.cloud",
                token="new-token",
                project_id=99,
                path=config_path,
                now="2026-04-29T10:00:00Z",
            )

        persisted = json.loads(config_path.read_text(encoding="utf-8"))
        assert persisted["allure_endpoint"] == "https://old.testops.cloud"
        assert persisted["allure_api_token"] == "old-token"
        assert persisted["allure_project_id"] == 1

    def test_apply_saved_auth_environment_only_fills_missing(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        config_path = tmp_path / "auth.json"
        monkeypatch.setattr("src.cli.auth_config.platformdirs.user_config_path", lambda *args, **kwargs: tmp_path)
        save_auth_config(
            url="https://saved.testops.cloud",
            token="saved-token",
            project_id=77,
            path=config_path,
            now="2026-04-29T10:00:00Z",
        )

        import src.utils.config as config_module

        monkeypatch.setattr(config_module.settings, AUTH_ENDPOINT_ENV, "https://demo.testops.cloud", raising=False)
        monkeypatch.setattr(config_module.settings, AUTH_TOKEN_ENV, None, raising=False)
        monkeypatch.setattr(config_module.settings, AUTH_PROJECT_ENV, None, raising=False)

        env = {AUTH_ENDPOINT_ENV: "https://env.testops.cloud"}
        loaded = apply_saved_auth_environment(env)
        assert loaded is not None
        assert env[AUTH_ENDPOINT_ENV] == "https://env.testops.cloud"
        assert env[AUTH_TOKEN_ENV] == "saved-token"
        assert env[AUTH_PROJECT_ENV] == "77"
        assert config_module.settings.ALLURE_ENDPOINT == "https://demo.testops.cloud"
        assert config_module.settings.ALLURE_API_TOKEN is None
        assert config_module.settings.ALLURE_PROJECT_ID is None

    def test_apply_saved_auth_environment_does_not_override_explicit_empty_env(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        config_path = tmp_path / "auth.json"
        monkeypatch.setattr("src.cli.auth_config.platformdirs.user_config_path", lambda *args, **kwargs: tmp_path)
        save_auth_config(
            url="https://saved.testops.cloud",
            token="saved-token",
            project_id=77,
            path=config_path,
            now="2026-04-29T10:00:00Z",
        )

        env = {
            AUTH_ENDPOINT_ENV: "",
            AUTH_TOKEN_ENV: "",
            AUTH_PROJECT_ENV: "",
        }
        apply_saved_auth_environment(env)
        assert env[AUTH_ENDPOINT_ENV] == ""
        assert env[AUTH_TOKEN_ENV] == ""
        assert env[AUTH_PROJECT_ENV] == ""

    def test_clear_auth_config_removes_existing_file(self, tmp_path: Path) -> None:
        config_path = _write_saved_config(
            tmp_path,
            url="https://example.testops.cloud",
            token="clear-token",
            project_id=123,
        )
        assert clear_auth_config(config_path) is True
        assert not config_path.exists()

    def test_clear_auth_config_returns_false_when_missing(self, tmp_path: Path) -> None:
        assert clear_auth_config(tmp_path / "auth.json") is False

    def test_save_auth_config_surfaces_existing_config_errors(self, tmp_path: Path) -> None:
        config_path = tmp_path / "auth.json"
        config_path.write_text("{bad-json", encoding="utf-8")
        with pytest.raises(CLIError, match="malformed JSON"):
            save_auth_config(
                url="https://example.testops.cloud",
                token="super-secret-token",
                project_id=123,
                path=config_path,
                now="2026-04-29T10:00:00Z",
            )


class TestCLIAuthCommandUnit:
    def test_parse_auth_command_options(self) -> None:
        options = parse_auth_command_options(
            ["--url", "https://example.testops.cloud", "--token", "abc", "--project", "7"]
        )
        assert options.mode == "configure"
        assert options.url == "https://example.testops.cloud"
        assert options.token == "abc"
        assert options.project == "7"

        status = parse_auth_command_options(["status"])
        assert status.mode == "status"

        clear = parse_auth_command_options(["clear"])
        assert clear.mode == "clear"

    def test_auth_help_and_status_do_not_import_fastmcp_or_src_main(self, capsys: pytest.CaptureFixture[str]) -> None:
        original_fastmcp = sys.modules.get("fastmcp")
        original_src_main = sys.modules.get("src.main")
        sys.modules.pop("fastmcp", None)
        sys.modules.pop("src.main", None)
        try:
            run_cli_in_process(["auth", "--help"])
            _ = capsys.readouterr()
            run_cli_in_process(["auth", "status"])
            _ = capsys.readouterr()
            assert "fastmcp" not in sys.modules
            assert "src.main" not in sys.modules
        finally:
            if original_fastmcp is not None:
                sys.modules["fastmcp"] = original_fastmcp
            else:
                sys.modules.pop("fastmcp", None)
            if original_src_main is not None:
                sys.modules["src.main"] = original_src_main
            else:
                sys.modules.pop("src.main", None)

    def test_auth_route_stays_out_of_tool_route_matrix_and_schema(self) -> None:
        assert "auth" not in CANONICAL_ROUTE_MATRIX
        schemas = load_tool_schemas(cli_entry.TOOL_SCHEMAS_PATH, Path(cli_entry.__file__))
        assert all(schema.get("entity") != "auth" for schema in schemas.values())
        assert all(schema.get("action") != "auth" for schema in schemas.values())

    def test_partial_non_interactive_auth_prompts_only_for_missing_values(self) -> None:
        with (
            patch("builtins.input", return_value="42") as prompt_input,
            patch("src.cli.auth_command.getpass.getpass", return_value="masked-token") as prompt_secret,
            patch("src.cli.auth_command.validate_auth_credentials", new=AsyncMock()) as mock_validate,
            patch("src.cli.auth_command.save_auth_config", return_value=Path("/tmp/auth.json")) as mock_save,
            patch.object(cli_entry.console_out, "print"),
        ):
            run_cli_in_process(["auth", "--url", "https://example.testops.cloud"])

        prompt_input.assert_called_once_with("Default project ID: ")
        prompt_secret.assert_called_once_with("Allure API token: ")
        mock_validate.assert_awaited_once_with(
            url="https://example.testops.cloud",
            token="masked-token",
            project_id=42,
        )
        mock_save.assert_called_once()

    def test_auth_clear_removes_saved_config_in_process(self) -> None:
        with (
            patch("src.cli.auth_command.clear_auth_config", return_value=True) as mock_clear,
            patch("src.cli.auth_command.auth_config_path", return_value=Path("/tmp/auth.json")),
            patch.object(cli_entry.console_out, "print") as mock_print,
        ):
            run_cli_in_process(["auth", "clear"])

        mock_clear.assert_called_once_with(Path("/tmp/auth.json"))
        printed = " ".join(str(call.args[0]) for call in mock_print.call_args_list)
        assert "Cleared saved CLI auth configuration." in printed

    def test_auth_clear_noop_in_process_when_missing(self) -> None:
        with (
            patch("src.cli.auth_command.clear_auth_config", return_value=False) as mock_clear,
            patch("src.cli.auth_command.auth_config_path", return_value=Path("/tmp/auth.json")),
            patch.object(cli_entry.console_out, "print") as mock_print,
        ):
            run_cli_in_process(["auth", "clear"])

        mock_clear.assert_called_once_with(Path("/tmp/auth.json"))
        printed = " ".join(str(call.args[0]) for call in mock_print.call_args_list)
        assert "CLI auth was already clear." in printed

    def test_blank_non_interactive_values_prompt_for_missing_values(self) -> None:
        with (
            patch("builtins.input", side_effect=["https://example.testops.cloud", "42"]) as prompt_input,
            patch("src.cli.auth_command.getpass.getpass", return_value="masked-token") as prompt_secret,
            patch("src.cli.auth_command.validate_auth_credentials", new=AsyncMock()) as mock_validate,
            patch("src.cli.auth_command.save_auth_config", return_value=Path("/tmp/auth.json")) as mock_save,
            patch.object(cli_entry.console_out, "print"),
        ):
            run_cli_in_process(["auth", "--url", " ", "--token", "", "--project", ""])

        assert prompt_input.call_args_list == [
            (("Allure URL: ",),),
            (("Default project ID: ",),),
        ]
        prompt_secret.assert_called_once_with("Allure API token: ")
        mock_validate.assert_awaited_once_with(
            url="https://example.testops.cloud",
            token="masked-token",
            project_id=42,
        )
        mock_save.assert_called_once()

    def test_validation_error_mapping_redacts_exception_text_with_patch(self) -> None:
        error = _map_auth_validation_error(RuntimeError("secret-token leaked"), project_id=7)
        assert "secret-token" not in error.message
        assert error.message == "Unexpected auth validation error."

    def test_get_auth_context_reads_live_environment_without_settings_mutation(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv(AUTH_TOKEN_ENV, "saved-token")
        monkeypatch.setenv(AUTH_PROJECT_ENV, "77")
        context = get_auth_context()
        assert context.api_token.get_secret_value() == "saved-token"
        assert context.project_id == 77


class TestCLIAuthCommandProcess:
    def test_process_cli_help_mentions_auth(self) -> None:
        result = run_cli(["--help"])
        assert result.returncode == 0
        assert "lucius auth" in result.stdout

    def test_process_auth_noninteractive_writes_config(self, tmp_path: Path) -> None:
        sitecustomize = _sitecustomize_dir(
            tmp_path,
            """
            import src.cli.auth_command as auth_command

            async def _fake_validate(*, url, token, project_id):
                assert url == "https://example.testops.cloud"
                assert token == "super-secret-token"
                assert project_id == 123

            auth_command.validate_auth_credentials = _fake_validate
            """,
        )
        env = _subprocess_env(tmp_path, sitecustomize=sitecustomize)
        result = run_cli(
            [
                "auth",
                "--url",
                "https://example.testops.cloud",
                "--token",
                "super-secret-token",
                "--project",
                "123",
            ],
            env=env,
        )
        assert result.returncode == 0
        assert "super-secret-token" not in result.stdout

        config_path = Path(env["XDG_CONFIG_HOME"]) / "lucius" / "auth.json"
        payload = json.loads(config_path.read_text(encoding="utf-8"))
        assert payload["allure_endpoint"] == "https://example.testops.cloud"
        assert payload["allure_api_token"] == "super-secret-token"
        assert payload["allure_project_id"] == 123

    def test_process_auth_status_never_displays_token(self, tmp_path: Path) -> None:
        env = _subprocess_env(tmp_path)
        _write_saved_config(
            Path(env["XDG_CONFIG_HOME"]),
            url="https://example.testops.cloud",
            token="hidden-token",
            project_id=123,
        )
        result = run_cli(["auth", "status"], env=env)
        assert result.returncode == 0
        assert "hidden-token" not in result.stdout
        assert "API token: configured" in result.stdout

    def test_process_auth_clear_removes_saved_config(self, tmp_path: Path) -> None:
        env = _subprocess_env(tmp_path)
        config_path = _write_saved_config(
            Path(env["XDG_CONFIG_HOME"]),
            url="https://example.testops.cloud",
            token="hidden-token",
            project_id=123,
        )
        result = run_cli(["auth", "clear"], env=env)
        assert result.returncode == 0
        assert "Cleared saved CLI auth configuration." in result.stdout
        assert not config_path.exists()

    def test_process_auth_clear_is_idempotent_when_missing(self, tmp_path: Path) -> None:
        env = _subprocess_env(tmp_path)
        result = run_cli(["auth", "clear"], env=env)
        assert result.returncode == 0
        assert "CLI auth was already clear." in result.stdout

    def test_process_saved_config_fills_missing_env_before_tool_resolution(self, tmp_path: Path) -> None:
        sitecustomize = _sitecustomize_dir(
            tmp_path,
            """
            import json
            import os
            import src.cli.tool_resolver as tool_resolver

            async def _fake_tool(**kwargs):
                return json.dumps(
                    {
                        "endpoint": os.environ.get("ALLURE_ENDPOINT"),
                        "token": os.environ.get("ALLURE_API_TOKEN"),
                        "project": os.environ.get("ALLURE_PROJECT_ID"),
                        "kwargs": kwargs,
                    }
                )

            tool_resolver.resolve_tool_function = lambda _tool_name: _fake_tool
            """,
        )
        env = _subprocess_env(tmp_path, sitecustomize=sitecustomize)
        _write_saved_config(
            Path(env["XDG_CONFIG_HOME"]),
            url="https://saved.testops.cloud",
            token="saved-token",
            project_id=321,
        )
        result = run_cli(["launch", "close", "--args", '{"launch_id": 15}'], env=env)
        assert result.returncode == 0
        payload = json.loads(result.stdout)
        assert payload["endpoint"] == "https://saved.testops.cloud"
        assert payload["token"] == "saved-token"
        assert payload["project"] == "321"

    def test_process_real_env_vars_override_saved_config(self, tmp_path: Path) -> None:
        sitecustomize = _sitecustomize_dir(
            tmp_path,
            """
            import json
            import os
            import src.cli.tool_resolver as tool_resolver

            async def _fake_tool(**kwargs):
                return json.dumps(
                    {
                        "endpoint": os.environ.get("ALLURE_ENDPOINT"),
                        "token": os.environ.get("ALLURE_API_TOKEN"),
                        "project": os.environ.get("ALLURE_PROJECT_ID"),
                    }
                )

            tool_resolver.resolve_tool_function = lambda _tool_name: _fake_tool
            """,
        )
        env = _subprocess_env(tmp_path, sitecustomize=sitecustomize)
        _write_saved_config(
            Path(env["XDG_CONFIG_HOME"]),
            url="https://saved.testops.cloud",
            token="saved-token",
            project_id=321,
        )
        env[AUTH_ENDPOINT_ENV] = "https://env.testops.cloud"
        env[AUTH_TOKEN_ENV] = "env-token"
        env[AUTH_PROJECT_ENV] = "999"
        result = run_cli(["launch", "close", "--args", '{"launch_id": 15}'], env=env)
        assert result.returncode == 0
        payload = json.loads(result.stdout)
        assert payload["endpoint"] == "https://env.testops.cloud"
        assert payload["token"] == "env-token"
        assert payload["project"] == "999"

    def test_process_explicit_empty_env_vars_do_not_fall_back_to_saved_config(self, tmp_path: Path) -> None:
        sitecustomize = _sitecustomize_dir(
            tmp_path,
            """
            import json
            import os
            import src.cli.tool_resolver as tool_resolver

            async def _fake_tool(**kwargs):
                return json.dumps(
                    {
                        "endpoint": os.environ.get("ALLURE_ENDPOINT"),
                        "token": os.environ.get("ALLURE_API_TOKEN"),
                        "project": os.environ.get("ALLURE_PROJECT_ID"),
                    }
                )

            tool_resolver.resolve_tool_function = lambda _tool_name: _fake_tool
            """,
        )
        env = _subprocess_env(tmp_path, sitecustomize=sitecustomize)
        _write_saved_config(
            Path(env["XDG_CONFIG_HOME"]),
            url="https://saved.testops.cloud",
            token="saved-token",
            project_id=321,
        )
        env[AUTH_ENDPOINT_ENV] = ""
        env[AUTH_TOKEN_ENV] = ""
        env[AUTH_PROJECT_ENV] = ""
        result = run_cli(["launch", "close", "--args", '{"launch_id": 15}'], env=env)
        assert result.returncode == 0
        payload = json.loads(result.stdout)
        assert payload["endpoint"] == ""
        assert payload["token"] == ""
        assert payload["project"] == ""

    def test_process_action_args_override_default_auth_context(self, tmp_path: Path) -> None:
        sitecustomize = _sitecustomize_dir(
            tmp_path,
            """
            import json
            import os
            import src.cli.tool_resolver as tool_resolver

            async def _fake_tool(**kwargs):
                from src.utils.auth import get_auth_context

                context = get_auth_context(api_token=kwargs.get("api_token"), project_id=kwargs.get("project_id"))
                return json.dumps(
                    {
                        "endpoint": os.environ.get("ALLURE_ENDPOINT"),
                        "token": context.api_token.get_secret_value(),
                        "project": context.project_id,
                    }
                )

            tool_resolver.resolve_tool_function = lambda _tool_name: _fake_tool
            """,
        )
        env = _subprocess_env(tmp_path, sitecustomize=sitecustomize)
        _write_saved_config(
            Path(env["XDG_CONFIG_HOME"]),
            url="https://saved.testops.cloud",
            token="saved-token",
            project_id=321,
        )
        result = run_cli(
            ["launch", "close", "--args", '{"launch_id": 15, "api_token": "arg-token", "project_id": 77}'],
            env=env,
        )
        assert result.returncode == 0
        payload = json.loads(result.stdout)
        assert payload["endpoint"] == "https://saved.testops.cloud"
        assert payload["token"] == "arg-token"
        assert payload["project"] == 77

    def test_uv_run_auth_and_status(self, tmp_path: Path) -> None:
        sitecustomize = _sitecustomize_dir(
            tmp_path,
            """
            import src.cli.auth_command as auth_command

            async def _fake_validate(*, url, token, project_id):
                assert url == "https://example.testops.cloud"
                assert token == "uv-secret-token"
                assert project_id == 555

            auth_command.validate_auth_credentials = _fake_validate
            """,
        )
        env = _subprocess_env(tmp_path, sitecustomize=sitecustomize)
        setup = run_uv_cli(
            [
                "auth",
                "--url",
                "https://example.testops.cloud",
                "--token",
                "uv-secret-token",
                "--project",
                "555",
            ],
            env=env,
        )
        assert setup.returncode == 0
        assert "uv-secret-token" not in setup.stdout

        status = run_uv_cli(["auth", "status"], env=env)
        assert status.returncode == 0
        assert "CLI auth status: configured" in status.stdout
        assert "uv-secret-token" not in status.stdout

        clear = run_uv_cli(["auth", "clear"], env=env)
        assert clear.returncode == 0
        assert "Cleared saved CLI auth configuration." in clear.stdout

        status_after_clear = run_uv_cli(["auth", "status"], env=env)
        assert status_after_clear.returncode == 0
        assert "CLI auth status: not configured" in status_after_clear.stdout

    def test_uv_run_saved_config_fallback(self, tmp_path: Path) -> None:
        sitecustomize = _sitecustomize_dir(
            tmp_path,
            """
            import json
            import os
            import src.cli.tool_resolver as tool_resolver

            async def _fake_tool(**kwargs):
                return json.dumps(
                    {
                        "endpoint": os.environ.get("ALLURE_ENDPOINT"),
                        "token": os.environ.get("ALLURE_API_TOKEN"),
                        "project": os.environ.get("ALLURE_PROJECT_ID"),
                    }
                )

            tool_resolver.resolve_tool_function = lambda _tool_name: _fake_tool
            """,
        )
        env = _subprocess_env(tmp_path, sitecustomize=sitecustomize)
        _write_saved_config(
            Path(env["XDG_CONFIG_HOME"]),
            url="https://saved.testops.cloud",
            token="saved-token",
            project_id=321,
        )
        result = run_uv_cli(["launch", "close", "--args", '{"launch_id": 15}'], env=env)
        assert result.returncode == 0
        payload = json.loads(result.stdout)
        assert payload["endpoint"] == "https://saved.testops.cloud"
        assert payload["token"] == "saved-token"
        assert payload["project"] == "321"


class TestCLICompletionScripts:
    def test_generated_completion_script_includes_auth_tokens(self) -> None:
        script_path = Path(__file__).resolve().parents[2] / "deployment" / "scripts" / "generate_completions.py"
        spec = importlib.util.spec_from_file_location("generate_completions_test", script_path)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules["generate_completions_test"] = module
        spec.loader.exec_module(module)

        entities, alias_to_canonical, actions_by_entity = module._completion_data()
        bash = module.generate_bash_completion(entities, alias_to_canonical, actions_by_entity)
        zsh = module.generate_zsh_completion(entities, alias_to_canonical, actions_by_entity)
        fish = module.generate_fish_completion(entities, alias_to_canonical, actions_by_entity)
        powershell = module.generate_powershell_completion(entities, alias_to_canonical, actions_by_entity)

        for rendered in (bash, zsh, fish, powershell):
            assert "auth" in rendered
            assert "status" in rendered
            assert "clear" in rendered
        for rendered in (bash, zsh, powershell):
            assert "--url" in rendered
            assert "--token" in rendered
            assert "--project" in rendered
        assert "-l url" in fish
        assert "-l token" in fish
        assert "-l project" in fish
        assert "COMP_WORDS[2]" in bash
        assert '"status"' in bash
        assert "words[3]:l" in zsh
        assert '"status"' in zsh
        assert "not __fish_seen_subcommand_from status" in fish
        assert "$commandAst.CommandElements[2].Value -eq 'status'" in powershell
