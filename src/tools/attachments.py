"""Safe evidence-download preparation tools."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from functools import partial
from typing import Annotated, Literal

from pydantic import Field

from src.client import AllureClient
from src.services import attachment_download_runtime
from src.services.attachment_download_service import (
    AttachmentDownloadService,
    AttachmentKind,
    AttachmentPreparationRequest,
)
from src.tools.output_contract import DEFAULT_OUTPUT_FORMAT, OutputFormat, ToolOutput, render_output
from src.tools.output_schemas import PreparedAttachmentDownloadOutput, output_fields
from src.utils.auth_resolution import resolve_auth_settings

AttachmentKindInput = Literal["test_result", "fixture_result", "test_case"]


@output_fields(
    "attachment_id",
    "attachment_kind",
    "test_result_id",
    "test_case_id",
    "download_url",
    "expires_at",
    "name",
    "content_type",
    "content_length",
    model=PreparedAttachmentDownloadOutput,
)
async def prepare_attachment_download(
    attachment_id: Annotated[
        int,
        Field(gt=0, description="Attachment ID discovered from a readable result or test case."),
    ],
    attachment_kind: Annotated[
        AttachmentKindInput,
        Field(description="Verified attachment kind: test_result, fixture_result, or test_case."),
    ],
    test_result_id: Annotated[
        int | None,
        Field(gt=0, description="Required owner ID for test_result or fixture_result attachments."),
    ] = None,
    test_case_id: Annotated[
        int | None,
        Field(gt=0, description="Required owner ID for test_case attachments."),
    ] = None,
    project_id: Annotated[int | None, Field(gt=0, description="Optional override for the default Project ID.")] = None,
    output_format: Annotated[OutputFormat | None, Field(description="Output format: 'json' (default) or 'plain'.")] = (
        DEFAULT_OUTPUT_FORMAT
    ),
) -> ToolOutput:
    """Prepare one verified attachment download, then HTTP GET its returned Lucius URL.

    Call this after get_test_result or get_test_case_details provides an attachment ID, kind, and owner context.
    The returned download URL is one-time and short-lived: HTTP GET it before expires_at without an Allure bearer token.
    Prepare again if the URL expires or was already retrieved.

    Args:
        attachment_id: Attachment ID discovered from a readable result or test case.
        attachment_kind: Verified attachment kind: test_result, fixture_result, or test_case.
        test_result_id: Required owner ID for test_result or fixture_result attachments.
        test_case_id: Required owner ID for test_case attachments.
        project_id: Optional override for the default Project ID.
        output_format: Output format: 'json' (default) or 'plain'.

    Returns:
        Attachment metadata and an opaque Lucius download_url. HTTP GET it before expires_at without an Allure bearer
        token.
    """
    request = AttachmentPreparationRequest(
        attachment_id=attachment_id,
        kind=AttachmentKind(attachment_kind),
        test_result_id=test_result_id,
        test_case_id=test_case_id,
    )
    request.validate()

    async with _attachment_client_context(project_id=project_id) as client:
        prepared = await AttachmentDownloadService(
            client, holder=attachment_download_runtime.attachment_download_runtime_holder
        ).prepare(
            request,
            public_base_url=partial(attachment_download_runtime.get_attachment_download_public_base_url),
        )

    payload = {
        "attachment_id": attachment_id,
        "attachment_kind": attachment_kind,
        "test_result_id": test_result_id,
        "test_case_id": test_case_id,
        "download_url": prepared.download_url,
        "expires_at": prepared.expires_at.isoformat().replace("+00:00", "Z"),
        "name": prepared.filename,
        "content_type": prepared.content_type,
        "content_length": prepared.byte_size,
    }
    plain = (
        f"Attachment prepared: {prepared.filename} ({prepared.content_type}, {prepared.byte_size} bytes).\n"
        "HTTP GET the returned one-time download_url before expires_at; do not send an Allure bearer token. "
        "Prepare again if the URL expires or has already been retrieved."
    )
    return render_output(plain=plain, json_payload=payload, output_format=output_format)


@asynccontextmanager
async def _attachment_client_context(*, project_id: int | None = None) -> AsyncIterator[AllureClient]:
    """Resolve the standard authenticated client context without importing MCP runtime state."""
    resolved = resolve_auth_settings(project_id=project_id)
    if not resolved.endpoint:
        raise ValueError("ALLURE_ENDPOINT is required for attachment download preparation")
    if resolved.api_token is None:
        raise ValueError("ALLURE_API_TOKEN is required for attachment download preparation")
    if resolved.project_id is None:
        raise ValueError("Project ID is required for attachment download preparation")

    async with AllureClient(
        base_url=resolved.endpoint,
        token=resolved.api_token,
        project=resolved.project_id,
    ) as client:
        yield client
