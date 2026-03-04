"""E2E server entrypoint that routes telemetry to the test collector."""

from __future__ import annotations

import importlib
import os
from dataclasses import replace

from src.utils import config as config_module


def _configure_test_telemetry() -> None:
    base_url = os.getenv("LUCIUS_E2E_UMAMI_BASE_URL")
    if not base_url:
        return
    config_module.telemetry_config = replace(config_module.telemetry_config, umami_base_url=base_url)


_configure_test_telemetry()


if __name__ == "__main__":
    start = importlib.import_module("src.main").start
    start()
