"""Curated exact test-result reads with bounded best-effort enrichment."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import TypeVar

from src.client import AllureClient
from src.client.exceptions import AllureAPIError, AllureValidationError
from src.utils.links import (
    fixture_result_attachment_download_url,
    launch_url,
    result_attachment_download_url,
    test_case_attachment_download_url,
    test_case_url,
    test_result_url,
)

T = TypeVar("T")
MAX_PAGES = 100
PAGE_SIZE = 100


@dataclass(frozen=True)
class UnavailableSection:
    section: str
    reason: str
    status_code: int | None = None
    message: str | None = None
    items_retrieved: int = 0


@dataclass(frozen=True)
class AttachmentDetail:
    id: int | None
    name: str | None
    entity: str | None
    content_type: str | None
    content_length: int | None
    missed: bool | None
    from_test_case: bool | None
    storage_key: str | None
    download_url: str | None


@dataclass(frozen=True)
class StepDetail:
    id: int | None
    type: str | None
    name: str | None
    action: str | None
    body: str | None
    body_json: object | None
    expected_result: str | None
    keyword: str | None
    status: str | None
    start: int | None
    stop: int | None
    duration: int | None
    message: str | None
    trace: str | None
    parameters: tuple[dict[str, object], ...]
    attachments: tuple[AttachmentDetail, ...]
    steps: tuple[StepDetail, ...]


@dataclass(frozen=True)
class FixtureDetail:
    id: int | None
    name: str | None
    type: str | None
    status: str | None
    start: int | None
    stop: int | None
    duration: int | None
    message: str | None
    trace: str | None
    steps: tuple[StepDetail, ...]
    attachments: tuple[AttachmentDetail, ...]


@dataclass(frozen=True)
class RelatedResult:
    relation: str
    test_result_id: int | None
    launch_id: int | None
    name: str | None
    status: str | None
    url: str | None


@dataclass(frozen=True)
class TestRunResultDetail:
    requested_launch_id: int
    actual_launch_id: int | None
    test_result_id: int
    project_id: int | None
    result_url: str | None
    launch_url: str | None
    test_case: dict[str, object] | None
    core: dict[str, object]
    custom_fields: tuple[dict[str, object], ...]
    environment: tuple[dict[str, object], ...]
    members: tuple[dict[str, object], ...]
    test_keys: tuple[dict[str, object], ...]
    issues: tuple[dict[str, object], ...]
    defects: tuple[dict[str, object], ...]
    execution_steps: tuple[StepDetail, ...]
    fixtures: tuple[FixtureDetail, ...]
    result_attachments: tuple[AttachmentDetail, ...]
    related_results: tuple[RelatedResult, ...]
    partial: bool
    unavailable_sections: tuple[UnavailableSection, ...]


@dataclass(frozen=True)
class _Outcome:
    value: object | None
    unavailable: UnavailableSection | None = None


class TestResultService:
    """Compose one exact result without recursively reading related results."""

    def __init__(self, client: AllureClient) -> None:
        self._client = client
        self._base_url = client.get_base_url()
        self._project_id = client.get_project()

    async def get_test_run_result(self, launch_id: int, test_result_id: int) -> TestRunResultDetail:
        """Return a stable exact-result view; base lookup failures remain fatal."""
        self._validate_positive(launch_id, "Launch ID")
        self._validate_positive(test_result_id, "Test Result ID")
        result = await self._client.get_test_result(test_result_id)
        actual_launch_id = _int_value(result, "launch_id")
        project_id = _int_value(result, "project_id") or self._project_id

        jobs = await asyncio.gather(
            self._optional("execution", self._client.get_test_result_execution_raw(test_result_id, v2=True)),
            self._optional("fixtures", self._client.get_test_result_fixtures(test_result_id)),
            self._optional("result_attachments", self._collect_result_attachments(test_result_id)),
            self._optional("fixture_attachments", self._collect_fixture_attachments(test_result_id)),
            self._optional("custom_fields", self._client.get_test_result_custom_fields(test_result_id)),
            self._optional("environment", self._client.get_test_result_environment(test_result_id)),
            self._optional("members", self._client.get_test_result_members(test_result_id)),
            self._optional("test_keys", self._client.get_test_result_test_keys(test_result_id)),
            self._optional("issues", self._client.get_test_result_issues(test_result_id)),
            self._optional("defects", self._collect_defects(test_result_id)),
            self._optional("history", self._collect_history(test_result_id, retries=False)),
            self._optional("retries", self._collect_history(test_result_id, retries=True)),
        )
        outcomes = dict(
            zip(
                (
                    "execution",
                    "fixtures",
                    "result_attachments",
                    "fixture_attachments",
                    "custom_fields",
                    "environment",
                    "members",
                    "test_keys",
                    "issues",
                    "defects",
                    "history",
                    "retries",
                ),
                jobs,
                strict=True,
            )
        )
        unavailable = [outcome.unavailable for outcome in outcomes.values() if outcome.unavailable is not None]

        if actual_launch_id is None:
            unavailable.append(
                UnavailableSection(
                    "result_url", "unverified_context", message="The upstream result did not provide a launch ID"
                )
            )
        result_url = test_result_url(self._base_url, actual_launch_id, test_result_id) if actual_launch_id else None
        verified_launch_url = (
            launch_url(self._base_url, project_id or 0, actual_launch_id) if actual_launch_id else None
        )

        execution_steps = self._map_steps(_mapping_value(outcomes["execution"].value, "steps"), fixture=False)
        fixtures, fixture_diagnostic = self._map_fixtures(
            _sequence(outcomes["fixtures"].value),
            _sequence(outcomes["fixture_attachments"].value),
        )
        if fixture_diagnostic is not None:
            unavailable.append(fixture_diagnostic)
        related = self._map_related(
            _sequence(outcomes["history"].value), _sequence(outcomes["retries"].value), actual_launch_id
        )
        retried_by = _value(result, "retried_by")
        if retried_by is not None:
            related = (*related, self._related_reference(retried_by, "retried_by", actual_launch_id))

        return TestRunResultDetail(
            requested_launch_id=launch_id,
            actual_launch_id=actual_launch_id,
            test_result_id=test_result_id,
            project_id=project_id,
            result_url=result_url,
            launch_url=verified_launch_url,
            test_case=self._test_case_reference(result, project_id),
            core=self._core(result),
            custom_fields=tuple(_project_custom_field(item) for item in _sequence(outcomes["custom_fields"].value)),
            environment=tuple(_project_environment(item) for item in _sequence(outcomes["environment"].value)),
            members=tuple(_project_member(item) for item in _sequence(outcomes["members"].value)),
            test_keys=tuple(_project_test_key(item) for item in _sequence(outcomes["test_keys"].value)),
            issues=tuple(_project_issue(item) for item in _sequence(outcomes["issues"].value)),
            defects=tuple(_project_defect(item) for item in _sequence(outcomes["defects"].value)),
            execution_steps=execution_steps,
            fixtures=fixtures,
            result_attachments=tuple(
                self._attachment(item, fixture=False) for item in _sequence(outcomes["result_attachments"].value)
            ),
            related_results=related,
            partial=bool(unavailable),
            unavailable_sections=tuple(unavailable),
        )

    async def _optional(self, section: str, awaitable: Awaitable[T]) -> _Outcome:
        try:
            return _Outcome(await awaitable)
        except AllureAPIError as exc:
            return _Outcome(None, _unavailable(section, exc))
        except Exception:
            return _Outcome(
                None,
                UnavailableSection(
                    section, "upstream_error", message=f"{section.replace('_', ' ').title()} are unavailable"
                ),
            )

    async def _collect_result_attachments(self, test_result_id: int) -> list[object]:
        return await self._collect_pages(
            lambda page: self._client.list_test_result_attachments(test_result_id, page=page, size=PAGE_SIZE)
        )

    async def _collect_fixture_attachments(self, test_result_id: int) -> list[object]:
        return await self._collect_pages(
            lambda page: self._client.get_test_result_fixture_attachments(test_result_id, page=page, size=PAGE_SIZE)
        )

    async def _collect_defects(self, test_result_id: int) -> list[object]:
        return await self._collect_pages(
            lambda page: self._client.get_test_result_defects(test_result_id, page=page, size=PAGE_SIZE)
        )

    async def _collect_history(self, test_result_id: int, *, retries: bool) -> list[object]:
        fetch = self._client.get_test_result_retries if retries else self._client.get_test_result_history
        return await self._collect_pages(lambda page: fetch(test_result_id, page=page, size=PAGE_SIZE))

    async def _collect_pages(self, fetch: Callable[[int], Awaitable[object]]) -> list[object]:
        collected: list[object] = []
        seen_pages: set[int] = set()
        for requested_page in range(MAX_PAGES):
            page = await fetch(requested_page)
            page_number = _int_value(page, "number")
            if page_number is not None and page_number in seen_pages:
                raise AllureAPIError("Pagination did not advance")
            if page_number is not None:
                seen_pages.add(page_number)
            content = _sequence(_value(page, "content"))
            collected.extend(content)
            if _value(page, "last") is True:
                return collected
            total_pages = _int_value(page, "total_pages")
            if total_pages is not None and requested_page + 1 >= total_pages:
                return collected
            if not content and total_pages is None:
                raise AllureAPIError("Pagination response did not establish completion")
        raise AllureAPIError("Pagination safety bound reached")

    def _core(self, result: object) -> dict[str, object]:
        keys = (
            "name",
            "full_name",
            "status",
            "manual",
            "external",
            "hidden",
            "flaky",
            "muted",
            "known",
            "start",
            "stop",
            "duration",
            "created_date",
            "last_modified_date",
            "created_by",
            "last_modified_by",
            "assignee",
            "tested_by",
            "host_id",
            "thread_id",
            "scenario_key",
            "history_key",
            "description",
            "description_html",
            "precondition",
            "precondition_html",
            "expected_result",
            "expected_result_html",
            "message",
            "trace",
            "category",
            "layer",
            "parameters",
            "tags",
            "links",
            "job_run",
        )
        return {key: _json_value(_value(result, key)) for key in keys}

    def _test_case_reference(self, result: object, project_id: int | None) -> dict[str, object] | None:
        test_case_id = _int_value(result, "test_case_id")
        if test_case_id is None:
            return None
        return {
            "id": test_case_id,
            "name": _value(result, "name"),
            "url": test_case_url(self._base_url, project_id, test_case_id) if project_id else None,
        }

    def _attachment(self, value: object, *, fixture: bool) -> AttachmentDetail:
        entity = _str_value(value, "entity")
        attachment_id = _int_value(value, "id")
        from_test_case = _bool_value(value, "from_test_case")
        download_url: str | None = None
        if attachment_id is not None:
            if from_test_case is True or (entity and "testcase" in entity.lower().replace("_", "")):
                download_url = test_case_attachment_download_url(self._base_url, attachment_id)
            elif fixture:
                download_url = fixture_result_attachment_download_url(self._base_url, attachment_id)
            else:
                download_url = result_attachment_download_url(self._base_url, attachment_id)
        return AttachmentDetail(
            attachment_id,
            _str_value(value, "name"),
            entity,
            _str_value(value, "content_type"),
            _int_value(value, "content_length"),
            _bool_value(value, "missed"),
            from_test_case,
            _str_value(value, "storage_key"),
            download_url,
        )

    def _map_steps(self, values: object, *, fixture: bool) -> tuple[StepDetail, ...]:
        mapped: list[StepDetail] = []
        for value in _sequence(values):
            attachment = _value(value, "attachment")
            nested = self._map_steps(_value(value, "steps"), fixture=fixture)
            attachments = (self._attachment(attachment, fixture=fixture),) if attachment is not None else ()
            mapped.append(
                StepDetail(
                    _int_value(value, "id"),
                    _str_value(value, "type"),
                    _str_value(value, "name"),
                    _str_value(value, "action"),
                    _str_value(value, "body"),
                    _json_value(_value(value, "body_json")),
                    _str_value(value, "expected_result"),
                    _str_value(value, "keyword"),
                    _enum_value(_value(value, "status")),
                    _int_value(value, "start"),
                    _int_value(value, "stop"),
                    _int_value(value, "duration"),
                    _str_value(value, "message"),
                    _str_value(value, "trace"),
                    _parameter_dicts(_sequence(_value(value, "parameters"))),
                    attachments,
                    nested,
                )
            )
        return tuple(mapped)

    def _map_fixtures(
        self, values: Sequence[object], aggregate_attachments: Sequence[object]
    ) -> tuple[tuple[FixtureDetail, ...], UnavailableSection | None]:
        aggregate_by_id = {
            attachment_id: item
            for item in aggregate_attachments
            if (attachment_id := _int_value(item, "id")) is not None
        }
        owned_ids: set[int] = set()
        fixtures: list[FixtureDetail] = []
        for value in values:
            steps = self._map_steps(_value(_value(value, "scenario"), "steps"), fixture=True)
            step_attachments = _attachments_from_steps(steps)
            for attachment in step_attachments:
                if attachment.id is not None:
                    owned_ids.add(attachment.id)
            fixtures.append(
                FixtureDetail(
                    _int_value(value, "id"),
                    _str_value(value, "name"),
                    _enum_value(_value(value, "type")),
                    _enum_value(_value(value, "status")),
                    _int_value(value, "start"),
                    _int_value(value, "stop"),
                    _int_value(value, "duration"),
                    _str_value(value, "message"),
                    _str_value(value, "trace"),
                    steps,
                    step_attachments,
                )
            )
        orphan_ids = set(aggregate_by_id) - owned_ids
        diagnostic = None
        if orphan_ids:
            diagnostic = UnavailableSection(
                "fixture_attachments",
                "unverified_ownership",
                message="Some fixture attachment ownership could not be verified",
                items_retrieved=len(owned_ids),
            )
        return tuple(fixtures), diagnostic

    def _map_related(
        self, history: Sequence[object], retries: Sequence[object], actual_launch_id: int | None
    ) -> tuple[RelatedResult, ...]:
        references = [self._related_reference(item, "history", actual_launch_id) for item in history]
        references.extend(self._related_reference(item, "retry", actual_launch_id) for item in retries)
        return tuple(references)

    def _related_reference(self, value: object, relation: str, actual_launch_id: int | None) -> RelatedResult:
        launch = _value(value, "launch")
        launch_id = _int_value(launch, "id") or actual_launch_id
        result_id = _int_value(value, "id")
        url = test_result_url(self._base_url, launch_id, result_id) if launch_id and result_id else None
        return RelatedResult(
            relation,
            result_id,
            launch_id,
            _str_value(value, "name") or _str_value(launch, "name"),
            _enum_value(_value(value, "status")),
            url,
        )

    @staticmethod
    def _validate_positive(value: int, label: str) -> None:
        if not isinstance(value, int) or value <= 0:
            raise AllureValidationError(f"{label} must be a positive integer")


def _unavailable(section: str, error: AllureAPIError) -> UnavailableSection:
    status_code = error.status_code if isinstance(error.status_code, int) else None
    reason = "upstream_error"
    if status_code == 403:
        reason = "forbidden"
    elif status_code == 404:
        reason = "unsupported"
    return UnavailableSection(
        section, reason, status_code=status_code, message=f"{section.replace('_', ' ').title()} are unavailable"
    )


def _value(value: object | None, name: str) -> object | None:
    if isinstance(value, Mapping):
        return value.get(name) if name in value else value.get(_camel(name))
    return getattr(value, name, None) if value is not None else None


def _mapping_value(value: object | None, name: str) -> object | None:
    return _value(value, name)


def _sequence(value: object | None) -> Sequence[object]:
    return value if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) else ()


def _int_value(value: object | None, name: str) -> int | None:
    item = _value(value, name)
    return item if isinstance(item, int) and not isinstance(item, bool) else None


def _str_value(value: object | None, name: str) -> str | None:
    item = _value(value, name)
    return item if isinstance(item, str) else None


def _bool_value(value: object | None, name: str) -> bool | None:
    item = _value(value, name)
    return item if isinstance(item, bool) else None


def _enum_value(value: object | None) -> str | None:
    if isinstance(value, Enum):
        return str(value.value)
    return value if isinstance(value, str) else None


def _camel(value: str) -> str:
    head, *tail = value.split("_")
    return head + "".join(part.title() for part in tail)


def _json_value(value: object | None) -> object:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_json_value(item) for item in value]
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        return _json_value(to_dict())
    return str(value)


def _attachments_from_steps(steps: Sequence[StepDetail]) -> tuple[AttachmentDetail, ...]:
    attachments: list[AttachmentDetail] = []
    for step in steps:
        attachments.extend(step.attachments)
        attachments.extend(_attachments_from_steps(step.steps))
    return tuple(attachments)


def _parameter_dicts(values: Sequence[object]) -> tuple[dict[str, object], ...]:
    projected: list[dict[str, object]] = []
    for value in values:
        item = _json_value(value)
        if isinstance(item, dict):
            projected.append({str(key): value for key, value in item.items()})
    return tuple(projected)


def _project_custom_field(value: object) -> dict[str, object]:
    return {"custom_field": _json_value(_value(value, "custom_field")), "values": _json_value(_value(value, "values"))}


def _project_environment(value: object) -> dict[str, object]:
    return {
        "id": _int_value(value, "id"),
        "name": _str_value(value, "name"),
        "variable": _json_value(_value(value, "variable")),
    }


def _project_member(value: object) -> dict[str, object]:
    return {
        "id": _int_value(value, "id"),
        "name": _str_value(value, "name"),
        "role": _json_value(_value(value, "role")),
    }


def _project_test_key(value: object) -> dict[str, object]:
    return {
        "id": _int_value(value, "id"),
        "integration_id": _int_value(value, "integration_id"),
        "name": _str_value(value, "name"),
        "url": _str_value(value, "url"),
    }


def _project_issue(value: object) -> dict[str, object]:
    return {
        key: _json_value(_value(value, key))
        for key in (
            "id",
            "integration_id",
            "integration_type",
            "name",
            "display_name",
            "status",
            "summary",
            "url",
            "closed",
        )
    }


def _project_defect(value: object) -> dict[str, object]:
    return {
        "id": _int_value(value, "id"),
        "name": _str_value(value, "name"),
        "closed": _bool_value(value, "closed"),
        "issue": _json_value(_value(value, "issue")),
    }
