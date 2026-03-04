"""Telemetry collection service with privacy-preserving payload shaping."""

from __future__ import annotations

import asyncio
import datetime as dt
import hashlib
import os
import platform
import sys
import uuid
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

import httpx
import umami  # type: ignore[import-untyped]
from pydantic import ValidationError

from src.utils.config import settings, telemetry_config
from src.utils.logger import get_logger
from src.version import __version__

logger = get_logger(__name__)

type TelemetryOutcome = Literal["success", "error"]
type TelemetryErrorCategory = Literal["validation", "auth", "api", "unexpected"]
type DeploymentMethod = Literal["docker", "mcpb", "uvx+pypi", "cli", "plain-code-checkout"]
type MpcMode = Literal["stdio", "http"]


class TelemetryService:
    """Collect and send best-effort telemetry events."""

    def __init__(
        self,
        *,
        enabled: bool | None = None,
        umami_base_url: str | None = None,
        umami_website_id: str | None = None,
        umami_hostname: str | None = None,
        hash_salt: str | None = None,
        mcp_mode: MpcMode | None = None,
        lucius_version: str = __version__,
    ) -> None:
        self._enabled = self._resolve_enabled(enabled)
        self._umami_base_url = self._resolve_umami_base_url(
            telemetry_config.umami_base_url if umami_base_url is None else umami_base_url
        )
        self._website_id = self._resolve_umami_website_id(umami_website_id)
        self._hostname = self._resolve_umami_hostname(umami_hostname)
        self._hash_salt = telemetry_config.hash_salt if hash_salt is None else hash_salt
        self._mcp_mode = settings.MCP_MODE if mcp_mode is None else mcp_mode
        self._lucius_version = lucius_version
        self._session_id = uuid.uuid4().hex
        self._started_at = dt.datetime.now(dt.UTC).isoformat()
        self._pending_tasks: set[asyncio.Task[None]] = set()
        self._missing_website_warned = False
        self._umami_ready = self._configure_umami_client()

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def log_status(self) -> None:
        status = "enabled" if self._enabled else "disabled"
        logger.info("Telemetry status: %s", status)

    def emit_startup_event(self) -> None:
        if not self._enabled:
            return
        payload = self._runtime_context()
        session_id_hash = self._hash_identifier(self._session_id) or "unknown"
        payload.update(
            {
                "session_id_hash": session_id_hash,
                "process_started_at": self._started_at,
                "installation_id_hash": self._installation_id_hash(),
            }
        )
        self._schedule_event("lucius_startup", payload)

    def emit_tool_usage_event(
        self,
        *,
        tool_name: str,
        outcome: TelemetryOutcome,
        duration_ms: float,
        error: Exception | None = None,
    ) -> None:
        if not self._enabled:
            return
        payload = self._runtime_context()
        payload.update(
            {
                "tool_name": tool_name,
                "outcome": outcome,
                "duration_bucket": self._duration_bucket(duration_ms),
                "installation_id_hash": self._installation_id_hash(),
            }
        )
        if error is not None:
            payload["error_category"] = self._classify_error(error)
        self._schedule_event("lucius_tool_use", payload)

    async def drain(self) -> None:
        """Test helper: wait for scheduled telemetry tasks to finish."""
        if not self._pending_tasks:
            return
        await asyncio.gather(*tuple(self._pending_tasks), return_exceptions=True)

    def _runtime_context(self) -> dict[str, str]:
        endpoint_host_hash = self._hash_identifier(self._endpoint_host())
        project_hash = self._hash_identifier(str(settings.ALLURE_PROJECT_ID)) if settings.ALLURE_PROJECT_ID else None
        return {
            "lucius_version": self._lucius_version,
            "python_version": platform.python_version(),
            "platform": f"{platform.system().lower()}-{platform.machine().lower()}",
            "mcp_mode": self._mcp_mode,
            "deployment_method": self._detect_deployment_method(),
            "project_id_hash": project_hash or "unknown",
            "endpoint_host_hash": endpoint_host_hash or "unknown",
        }

    def _installation_id_hash(self) -> str:
        endpoint_host = self._endpoint_host() or "unknown-host"
        project_id = str(settings.ALLURE_PROJECT_ID) if settings.ALLURE_PROJECT_ID else "unknown-project"
        return self._hash_identifier(f"{endpoint_host}:{project_id}") or "unknown"

    def _endpoint_host(self) -> str | None:
        parsed = urlparse(settings.ALLURE_ENDPOINT)
        return parsed.hostname

    @staticmethod
    def _resolve_umami_base_url(base_url: str) -> str:
        cleaned = base_url.strip().rstrip("/")
        if cleaned.endswith("/api/send"):
            return cleaned[: -len("/api/send")]
        if cleaned.endswith("/api"):
            return cleaned[: -len("/api")]
        return cleaned

    def _configure_umami_client(self) -> bool:
        try:
            umami.set_url_base(self._umami_base_url)
            umami.set_hostname(self._hostname)
            if self._website_id:
                umami.set_website_id(self._website_id)
            return True
        except Exception as exc:
            logger.warning(
                "Telemetry disabled due to invalid Umami configuration",
                extra={"context": {"error": exc.__class__.__name__}},
            )
            return False

    @staticmethod
    def _resolve_enabled(explicit_enabled: bool | None) -> bool:
        if explicit_enabled is not None:
            return explicit_enabled
        if settings.TELEMETRY_ENABLED is not None:
            return settings.TELEMETRY_ENABLED
        return telemetry_config.enabled

    @staticmethod
    def _resolve_umami_website_id(explicit_website_id: str | None) -> str | None:
        if explicit_website_id is not None:
            return explicit_website_id
        if settings.TELEMETRY_UMAMI_WEBSITE_ID is not None:
            return settings.TELEMETRY_UMAMI_WEBSITE_ID
        return telemetry_config.umami_website_id

    @staticmethod
    def _resolve_umami_hostname(explicit_hostname: str | None) -> str:
        if explicit_hostname is not None:
            resolved = explicit_hostname
        elif settings.TELEMETRY_UMAMI_HOSTNAME is not None:
            resolved = settings.TELEMETRY_UMAMI_HOSTNAME
        else:
            resolved = telemetry_config.umami_hostname
        return resolved or "lucius-mcp.local"

    def _schedule_event(self, event_name: str, payload: dict[str, str]) -> None:
        if not self._umami_ready:
            logger.debug("Telemetry client is not configured; skipping event", extra={"context": {"event": event_name}})
            return

        if not self._website_id:
            if not self._missing_website_warned:
                logger.warning(
                    "Telemetry is enabled but telemetry_config.umami_website_id is missing; skipping event",
                    extra={"context": {"event": event_name}},
                )
                self._missing_website_warned = True
            else:
                logger.debug(
                    "Telemetry event skipped due to missing telemetry_config.umami_website_id",
                    extra={"context": {"event": event_name}},
                )
            return

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            logger.debug("No running event loop; telemetry event skipped", extra={"context": {"event": event_name}})
            return

        # Intentionally fire-and-forget: telemetry must never block tool execution or startup.
        task = loop.create_task(self._send_event(event_name=event_name, payload=payload))
        self._pending_tasks.add(task)
        task.add_done_callback(self._pending_tasks.discard)

    async def _send_event(self, *, event_name: str, payload: dict[str, str]) -> None:
        if not self._website_id:
            return

        try:
            await umami.new_event_async(
                event_name=event_name,
                hostname=self._hostname,
                url="/",
                website_id=self._website_id,
                title=event_name,
                custom_data=payload,
            )
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "Telemetry emission failed",
                extra={
                    "context": {
                        "event": event_name,
                        "error": exc.__class__.__name__,
                        "status_code": str(exc.response.status_code),
                    }
                },
            )
        except httpx.HTTPError as exc:
            logger.warning(
                "Telemetry emission failed",
                extra={"context": {"event": event_name, "error": exc.__class__.__name__}},
            )
        except Exception as exc:
            logger.warning(
                "Telemetry emission failed",
                extra={"context": {"event": event_name, "error": exc.__class__.__name__}},
            )

    def _detect_deployment_method(self) -> DeploymentMethod:
        """Infer deployment method using process/runtime heuristics.

        Detection order is intentionally strict:
        1. `docker`: container markers (`/.dockerenv`, Kubernetes env hint)
        2. `mcpb`: bundled runtime markers in argv/executable/env
        3. `uvx+pypi`: uvx runtime markers in argv/env
        4. `cli`: installed script entrypoint names
        5. fallback: `plain-code-checkout`
        """
        if Path("/.dockerenv").exists() or os.getenv("KUBERNETES_SERVICE_HOST"):
            return "docker"

        argv_joined = " ".join(sys.argv).lower()
        executable = str(Path(sys.executable)).lower()
        if "mcpb" in argv_joined or "mcpb" in executable or os.getenv("MCPB_BUNDLE_PATH"):
            return "mcpb"

        if "uvx" in argv_joined:
            return "uvx+pypi"

        executable_name = Path(sys.argv[0]).name.lower()
        if executable_name in {"start", "lucius-mcp", "lucius_mcp"}:
            return "cli"

        return "plain-code-checkout"

    def _hash_identifier(self, value: str | None) -> str | None:
        if not value:
            return None
        salted = f"{self._hash_salt}:{value}" if self._hash_salt else value
        return hashlib.sha256(salted.encode("utf-8")).hexdigest()

    @staticmethod
    def _duration_bucket(duration_ms: float) -> str:
        if duration_ms < 100:
            return "<100ms"
        if duration_ms < 500:
            return "100-500ms"
        if duration_ms < 2000:
            return "500ms-2s"
        return ">2s"

    @staticmethod
    def _classify_error(error: Exception) -> TelemetryErrorCategory:
        error_name = error.__class__.__name__.lower()
        if isinstance(error, (ValidationError, ValueError, TypeError)) or "validation" in error_name:
            return "validation"
        if "auth" in error_name or "permission" in error_name or "token" in error_name or "unauthorized" in error_name:
            return "auth"
        if "api" in error_name or "http" in error_name or "request" in error_name or "timeout" in error_name:
            return "api"
        return "unexpected"
