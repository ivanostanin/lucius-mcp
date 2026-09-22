import pytest
from pydantic import ValidationError

from src.utils.config import Settings


def test_attachment_upload_limit_defaults_to_10_mib(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ATTACHMENT_MAX_FILE_BYTES", raising=False)

    settings = Settings(_env_file=None)

    assert settings.ATTACHMENT_MAX_FILE_BYTES == 10 * 1024 * 1024


def test_attachment_upload_limit_reads_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ATTACHMENT_MAX_FILE_BYTES", "104857600")

    settings = Settings(_env_file=None)

    assert settings.ATTACHMENT_MAX_FILE_BYTES == 100 * 1024 * 1024


def test_launch_attachment_import_root_reads_environment(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setenv("LAUNCH_ATTACHMENT_IMPORT_ROOT", str(tmp_path))

    settings = Settings(_env_file=None)

    assert settings.LAUNCH_ATTACHMENT_IMPORT_ROOT == tmp_path


@pytest.mark.parametrize("value", ["0", "-1", "not-a-number"])
def test_attachment_upload_limit_rejects_invalid_values(value: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ATTACHMENT_MAX_FILE_BYTES", value)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
