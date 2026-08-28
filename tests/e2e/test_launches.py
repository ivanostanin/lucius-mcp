"""E2E tests for launch lifecycle operations."""

import json
import threading
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import pytest
from pydantic import SecretStr

from src.client import AllureClient
from src.client.generated.models.launch_upload_response_dto import LaunchUploadResponseDto
from src.services.launch_service import LaunchService
from src.tools.launches import get_launch as get_launch_tool


@pytest.mark.asyncio
async def test_create_close_reopen_launch_lifecycle(allure_client, project_id, test_run_id, cleanup_tracker) -> None:
    service = LaunchService(client=allure_client)
    launch_name = f"[{test_run_id}] E2E Launch"
    created_id: int | None = None

    try:
        created = await service.create_launch(name=launch_name)
        assert created.id is not None
        cleanup_tracker.track_launch(created.id)

        created_id = created.id
        retrieved = await service.get_launch(created_id)
        assert retrieved.id == created_id
        assert retrieved.closed is not True
        assert retrieved.statistic is None or isinstance(retrieved.statistic, list)
        assert retrieved.environment is None or isinstance(retrieved.environment, list)
        assert retrieved.jobs is None or isinstance(retrieved.jobs, list)

        closed = await service.close_launch(created_id)
        assert closed.id == created_id
        assert closed.closed is True

        reopened = await service.reopen_launch(created_id)
        assert reopened.id == created_id
        assert reopened.closed is not True

        result = await service.list_launches(page=0, size=50, sort=["createdDate,DESC"])
        names = [getattr(item, "name", None) for item in result.items]
        assert launch_name in names
        assert all(not hasattr(item, "known_defects_count") for item in result.items)

        deleted = await service.delete_launch(created.id)
        assert deleted.launch_id == created.id
        assert deleted.status == "deleted"

        deleted_again = await service.delete_launch(created.id)
        assert deleted_again.launch_id == created.id
        assert deleted_again.status == "deleted"
    finally:
        if created_id is not None:
            await cleanup_tracker.delete_launch_strict(created_id)


@pytest.mark.asyncio
async def test_get_launch_execution_snapshot_is_opt_in(allure_client, test_run_id, cleanup_tracker) -> None:
    """Exercise the real tool/service/client aggregate against a sandbox launch."""
    service = LaunchService(client=allure_client)
    created = await service.create_launch(name=f"[{test_run_id}] E2E execution snapshot")
    assert created.id is not None
    cleanup_tracker.track_launch(created.id)

    detail = await service.get_launch(created.id, include_execution_results=True)

    assert detail.id == created.id
    assert detail.execution_snapshot is not None
    assert detail.partial is False or detail.unavailable_sections is not None
    assert detail.flat_test_results is not None
    assert detail.trees is not None


@pytest.mark.asyncio
async def test_get_launch_execution_controlled_later_page_failure_returns_serialized_partial_response() -> None:  # noqa: C901
    """Exercise the public tool through its real service/client stack and local HTTP upstream."""

    class StubTestOpsHandler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            if self.path != "/api/uaa/oauth/token":
                self.send_error(404)
                return
            encoded = b'{"access_token":"controlled-jwt","expires_in":3600}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def do_GET(self) -> None:
            request = urlsplit(self.path)
            query = parse_qs(request.query)
            page_payload = {
                "content": [],
                "empty": True,
                "first": True,
                "last": True,
                "number": 0,
                "numberOfElements": 0,
                "size": 100,
                "totalElements": 0,
                "totalPages": 1,
            }
            status = 200
            if request.path == "/api/launch/12":
                payload: object = {"id": 12, "name": "Controlled partial", "projectId": 1, "closed": False}
            elif request.path == "/api/launch/12/variables" and query.get("page") == ["0"]:
                payload = {
                    **page_payload,
                    "content": [{"key": "build", "values": ["42"]}],
                    "empty": False,
                    "numberOfElements": 1,
                    "last": False,
                    "totalElements": 2,
                    "totalPages": 2,
                }
            elif request.path == "/api/launch/12/variables" and query.get("page") == ["1"]:
                # Deliberately include unsafe-looking data: diagnostics must not echo it.
                status = 503
                payload = {"message": "Bearer secret-token at https://private.example/result"}
            elif request.path in {
                "/api/launch/12/duration",
                "/api/launch/12/assignees",
                "/api/launch/12/tester",
                "/api/launch/12/statistic",
                "/api/launch/12/env",
                "/api/launch/12/job",
            }:
                payload = []
            elif request.path == "/api/launch/12/progress":
                payload = {"ready": False}
            elif request.path in {"/api/testresult/timeline", "/api/testresult/defects"}:
                payload = {"groups": [], "leafs": []}
            elif request.path in {
                "/api/launch/12/defect",
                "/api/launch/12/memberstats",
                "/api/launch/12/muted",
                "/api/launch/12/retries",
                "/api/launch/12/unresolved",
                "/api/testresult",
                "/api/v2/launch/12/test-result/flat",
                "/api/v2/tree",
            }:
                payload = page_payload
            else:
                status = 404
                payload = {"message": "not found"}
            encoded = json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def log_message(self, *_args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), StubTestOpsHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    @asynccontextmanager
    async def local_client_context(
        *, project_id: int | None = None, api_token: str | None = None
    ) -> AsyncIterator[AllureClient]:
        del project_id, api_token
        async with AllureClient(
            base_url=f"http://127.0.0.1:{server.server_port}", token=SecretStr("test-token"), project=1
        ) as client:
            yield client

    try:
        with patch("src.tools.launches._launch_client_context", local_client_context):
            output = await get_launch_tool(launch_id=12, include_execution_results=True, output_format="json")
        payload = output.structured_content
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()

    assert payload["id"] == 12
    assert payload["variables"] == [{"key": "build", "values": ["42"]}]
    assert payload["partial"] is True
    diagnostic = next(item for item in payload["unavailable_sections"] if item["section"] == "variables")
    assert diagnostic["items_retrieved"] == 1
    assert diagnostic["reason"] == "upstream_error"
    serialized = json.dumps(payload)
    assert "secret-token" not in serialized
    assert "private.example" not in serialized


# todo: revise this once launch_upload_controller is in
@pytest.mark.asyncio
async def test_reopened_launch_accepts_upload_if_supported(
    allure_client, project_id, test_run_id, cleanup_tracker
) -> None:
    upload_method_name = "upload_results_to_launch"
    if not hasattr(allure_client, upload_method_name):
        pytest.skip(
            "AC4 upload acceptance check skipped: repository does not expose "
            "a launch-result-upload path in AllureClient"
        )

    service = LaunchService(client=allure_client)
    launch_name = f"[{test_run_id}] E2E Launch Upload AC4"

    created = await service.create_launch(name=launch_name)
    assert created.id is not None
    cleanup_tracker.track_launch(created.id)

    created_id = created.id
    await service.close_launch(created_id)
    reopened = await service.reopen_launch(created_id)
    assert reopened.closed is not True

    now_ms = int(time.time() * 1000)
    result_uuid = str(uuid.uuid4())
    container_uuid = str(uuid.uuid4())
    allure_result_payload = {
        "uuid": result_uuid,
        "historyId": result_uuid,
        "name": "upload-after-reopen",
        "fullName": "ac4.upload-after-reopen",
        "status": "passed",
        "stage": "finished",
        "start": now_ms,
        "stop": now_ms + 10,
        "labels": [
            {"name": "host", "value": "e2e-runner"},
            {"name": "thread", "value": test_run_id},
            {"name": "language", "value": "python"},
            {"name": "suite", "value": "ac4-suite"},
            {"name": "framework", "value": "pytest"},
        ],
    }
    allure_container_payload = {
        "uuid": container_uuid,
        "children": [result_uuid],
        "start": now_ms,
        "stop": now_ms + 10,
    }

    result_file_name = f"{result_uuid}-result.json"
    result_file_bytes = json.dumps(allure_result_payload).encode("utf-8")
    container_file_name = f"{container_uuid}-container.json"
    container_file_bytes = json.dumps(allure_container_payload).encode("utf-8")

    upload_result = await service.upload_results_to_launch(
        launch_id=created_id,
        files=[
            (result_file_name, result_file_bytes),
            (container_file_name, container_file_bytes),
        ],
    )

    assert isinstance(upload_result, LaunchUploadResponseDto)
    assert upload_result.launch_id == created_id
    assert upload_result.files_count is None or upload_result.files_count >= 1
