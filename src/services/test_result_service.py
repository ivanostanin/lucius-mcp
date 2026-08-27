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
    launch_url,
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
    attachment_id: int | None
    attachment_kind: str | None
    test_result_id: int | None
    test_case_id: int | None
    name: str | None
    entity: str | None
    content_type: str | None
    content_length: int | None
    missed: bool | None
    from_test_case: bool | None


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


class _IncompletePaginationError(Exception):
    """Carry items collected before an optional paginated request became incomplete."""

    def __init__(self, collected: list[object], error: AllureAPIError | None = None) -> None:
        self.collected = collected
        self.error = error


class TestResultService:
    """Compose one exact result without recursively reading related results."""

    def __init__(self, client: AllureClient) -> None:
        self._client = client
        self._base_url = client.get_base_url()
        self._project_id = client.get_project()

    async def get_test_result(self, test_result_id: int) -> TestRunResultDetail:
        """Return a stable exact-result view; base lookup failures remain fatal."""
        self._validate_positive(test_result_id, "Test Result ID")
        result = await self._client.get_test_result(test_result_id)
        actual_launch_id = _int_value(result, "launch_id")
        result_test_case_id = _int_value(result, "test_case_id")
        upstream_project_id = _int_value(result, "project_id")
        project_id = upstream_project_id if upstream_project_id is not None else self._project_id

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

        verified_launch_id = actual_launch_id if actual_launch_id is not None and actual_launch_id > 0 else None
        if verified_launch_id is None:
            unavailable.append(
                UnavailableSection(
                    "result_url",
                    "unverified_context",
                    message="The upstream result did not provide a verified launch ID",
                )
            )
        result_url = (
            test_result_url(self._base_url, verified_launch_id, test_result_id)
            if verified_launch_id is not None
            else None
        )
        verified_launch_url = (
            launch_url(self._base_url, project_id or 0, verified_launch_id) if verified_launch_id is not None else None
        )

        execution_steps = self._map_steps(
            _mapping_value(outcomes["execution"].value, "steps"),
            fixture=False,
            test_result_id=test_result_id,
            test_case_id=result_test_case_id,
        )
        fixtures, fixture_diagnostic = self._map_fixtures(
            _sequence(outcomes["fixtures"].value),
            _sequence(outcomes["fixture_attachments"].value),
            test_result_id=test_result_id,
            test_case_id=result_test_case_id,
        )
        if fixture_diagnostic is not None:
            unavailable.append(fixture_diagnostic)
        related = self._map_related(_sequence(outcomes["history"].value), _sequence(outcomes["retries"].value))
        retried_by = _value(result, "retried_by")
        if retried_by is not None:
            related = (*related, self._related_reference(retried_by, "retried_by"))

        return TestRunResultDetail(
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
                self._attachment(
                    item,
                    fixture=False,
                    test_result_id=test_result_id,
                    test_case_id=result_test_case_id,
                )
                for item in _sequence(outcomes["result_attachments"].value)
            ),
            related_results=related,
            partial=bool(unavailable),
            unavailable_sections=tuple(unavailable),
        )

    async def _optional(self, section: str, awaitable: Awaitable[T]) -> _Outcome:
        try:
            return _Outcome(await awaitable)
        except _IncompletePaginationError as exc:
            if exc.error is not None:
                unavailable = _unavailable(section, exc.error, items_retrieved=len(exc.collected))
            else:
                unavailable = UnavailableSection(
                    section,
                    "upstream_error",
                    message=f"{section.replace('_', ' ').title()} are incomplete",
                    items_retrieved=len(exc.collected),
                )
            return _Outcome(exc.collected, unavailable)
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
            try:
                page = await fetch(requested_page)
            except AllureAPIError as exc:
                raise _IncompletePaginationError(collected, exc) from exc
            except Exception as exc:
                raise _IncompletePaginationError(collected) from exc
            page_number = _int_value(page, "number")
            if page_number is not None and page_number in seen_pages:
                raise _IncompletePaginationError(collected, AllureAPIError("Pagination did not advance"))
            if page_number is not None:
                seen_pages.add(page_number)
                if page_number != requested_page:
                    raise _IncompletePaginationError(
                        collected, AllureAPIError("Pagination response returned an unexpected page number")
                    )
            content = _sequence(_value(page, "content"))
            collected.extend(content)
            total_pages = _int_value(page, "total_pages")
            if _is_terminal_page(page, requested_page, collected):
                return collected
            if not content and total_pages is None:
                raise _IncompletePaginationError(
                    collected, AllureAPIError("Pagination response did not establish completion")
                )
        raise _IncompletePaginationError(collected, AllureAPIError("Pagination safety bound reached"))

    def _core(self, result: object) -> dict[str, object]:
        scalar_keys = (
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
        )
        core = {key: _json_value(_value(result, key)) for key in scalar_keys}
        core.update(
            {
                "category": _project_named(_value(result, "category")),
                "layer": _project_named(_value(result, "layer")),
                "parameters": _parameter_dicts(_sequence(_value(result, "parameters"))),
                "tags": tuple(_project_named(item) for item in _sequence(_value(result, "tags"))),
                "links": tuple(_project_link(item) for item in _sequence(_value(result, "links"))),
                "job_run": _project_job_run(_value(result, "job_run")),
            }
        )
        return core

    def _test_case_reference(self, result: object, project_id: int | None) -> dict[str, object] | None:
        test_case_id = _int_value(result, "test_case_id")
        if test_case_id is None:
            return None
        return {
            "id": test_case_id,
            "name": _str_value(result, "test_case_name"),
            "url": test_case_url(self._base_url, project_id, test_case_id) if project_id is not None else None,
        }

    def _attachment(
        self,
        value: object,
        *,
        fixture: bool,
        test_result_id: int,
        test_case_id: int | None,
    ) -> AttachmentDetail:
        value = _unwrap_one_of(value)
        entity = _str_value(value, "entity")
        attachment_id = _int_value(value, "id")
        from_test_case = _bool_value(value, "from_test_case")
        entity_key = entity.lower().replace("_", "").replace("-", "") if entity else ""
        is_test_case = from_test_case is True or "testcase" in entity_key
        attachment_kind: str | None = (
            "test_case"
            if is_test_case
            else "fixture_result"
            if fixture or "testfixture" in entity_key
            else "test_result"
        )
        owner_test_result_id: int | None = None if attachment_kind == "test_case" else test_result_id
        owner_test_case_id: int | None = test_case_id if attachment_kind == "test_case" else None
        if attachment_id is not None and attachment_id <= 0:
            attachment_id = None
        if attachment_kind == "test_case" and test_case_id is None:
            attachment_id = None
            attachment_kind = None
            owner_test_result_id = None
        return AttachmentDetail(
            attachment_id,
            attachment_kind,
            owner_test_result_id,
            owner_test_case_id,
            _str_value(value, "name"),
            entity,
            _str_value(value, "content_type"),
            _int_value(value, "content_length"),
            _bool_value(value, "missed"),
            from_test_case,
        )

    def _map_steps(
        self,
        values: object,
        *,
        fixture: bool,
        test_result_id: int,
        test_case_id: int | None,
    ) -> tuple[StepDetail, ...]:
        mapped: list[StepDetail] = []
        for value in _sequence(values):
            value = _unwrap_one_of(value)
            attachment = _value(value, "attachment")
            nested = self._map_steps(
                _value(value, "steps"),
                fixture=fixture,
                test_result_id=test_result_id,
                test_case_id=test_case_id,
            )
            attachment_id = _int_value(value, "attachment_id")
            attachments = (
                (
                    self._attachment(
                        attachment,
                        fixture=fixture,
                        test_result_id=test_result_id,
                        test_case_id=test_case_id,
                    ),
                )
                if attachment is not None
                else (
                    self._attachment(
                        {"id": attachment_id},
                        fixture=fixture,
                        test_result_id=test_result_id,
                        test_case_id=test_case_id,
                    ),
                )
                if attachment_id is not None
                else ()
            )
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
        self,
        values: Sequence[object],
        aggregate_attachments: Sequence[object],
        *,
        test_result_id: int,
        test_case_id: int | None,
    ) -> tuple[tuple[FixtureDetail, ...], UnavailableSection | None]:
        aggregate_by_id = {
            attachment_id: item
            for item in aggregate_attachments
            if (attachment_id := _int_value(item, "id")) is not None
        }
        owned_ids: set[int] = set()
        fixtures: list[FixtureDetail] = []
        for value in values:
            steps = self._map_steps(
                _value(_value(value, "scenario"), "steps"),
                fixture=True,
                test_result_id=test_result_id,
                test_case_id=test_case_id,
            )
            steps = self._reconcile_fixture_steps(
                steps,
                aggregate_by_id,
                test_result_id=test_result_id,
                test_case_id=test_case_id,
            )
            step_attachments = _deduplicate_attachments(_attachments_from_steps(steps))
            for attachment in step_attachments:
                if attachment.attachment_id is not None:
                    owned_ids.add(attachment.attachment_id)
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

    def _reconcile_fixture_steps(
        self,
        steps: Sequence[StepDetail],
        aggregate_by_id: Mapping[int, object],
        *,
        test_result_id: int,
        test_case_id: int | None,
    ) -> tuple[StepDetail, ...]:
        return tuple(
            StepDetail(
                step.id,
                step.type,
                step.name,
                step.action,
                step.body,
                step.body_json,
                step.expected_result,
                step.keyword,
                step.status,
                step.start,
                step.stop,
                step.duration,
                step.message,
                step.trace,
                step.parameters,
                tuple(
                    self._attachment(
                        aggregate_by_id[attachment.attachment_id],
                        fixture=True,
                        test_result_id=test_result_id,
                        test_case_id=test_case_id,
                    )
                    if attachment.attachment_id is not None and attachment.attachment_id in aggregate_by_id
                    else attachment
                    for attachment in step.attachments
                ),
                self._reconcile_fixture_steps(
                    step.steps,
                    aggregate_by_id,
                    test_result_id=test_result_id,
                    test_case_id=test_case_id,
                ),
            )
            for step in steps
        )

    def _map_related(self, history: Sequence[object], retries: Sequence[object]) -> tuple[RelatedResult, ...]:
        references = [self._related_reference(item, "history") for item in history]
        references.extend(self._related_reference(item, "retry") for item in retries)
        return tuple(references)

    def _related_reference(self, value: object, relation: str) -> RelatedResult:
        launch = _value(value, "launch")
        launch_id = _int_value(launch, "id")
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
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise AllureValidationError(f"{label} must be a positive integer")


def _unavailable(section: str, error: AllureAPIError, *, items_retrieved: int = 0) -> UnavailableSection:
    status_code = error.status_code if isinstance(error.status_code, int) else None
    reason = "upstream_error"
    if status_code == 403:
        reason = "forbidden"
    elif status_code == 404:
        reason = "unsupported"
    return UnavailableSection(
        section,
        reason,
        status_code=status_code,
        message=f"{section.replace('_', ' ').title()} are unavailable",
        items_retrieved=items_retrieved,
    )


def _value(value: object | None, name: str) -> object | None:
    if isinstance(value, Mapping):
        return value.get(name) if name in value else value.get(_camel(name))
    return getattr(value, name, None) if value is not None else None


def _unwrap_one_of(value: object) -> object:
    """Extract the concrete generated-model value from a one-of envelope."""
    actual_instance = _value(value, "actual_instance")
    return actual_instance if actual_instance is not None else value


def _is_terminal_page(page: object, requested_page: int, collected: list[object]) -> bool:
    """Return whether pagination is complete, rejecting contradictory metadata."""
    last = _value(page, "last")
    total_pages = _int_value(page, "total_pages")
    if last is True:
        if total_pages is not None and total_pages != requested_page + 1:
            raise _IncompletePaginationError(
                collected, AllureAPIError("Pagination completion metadata is contradictory")
            )
        return True
    if total_pages is not None and requested_page + 1 >= total_pages:
        raise _IncompletePaginationError(collected, AllureAPIError("Pagination response did not establish completion"))
    return False


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


def _deduplicate_attachments(attachments: Sequence[AttachmentDetail]) -> tuple[AttachmentDetail, ...]:
    """Keep one fixture-owned attachment per verified ID, preserving ID-less rows."""
    seen_ids: set[int] = set()
    deduplicated: list[AttachmentDetail] = []
    for attachment in attachments:
        if attachment.attachment_id is not None:
            if attachment.attachment_id in seen_ids:
                continue
            seen_ids.add(attachment.attachment_id)
        deduplicated.append(attachment)
    return tuple(deduplicated)


def _parameter_dicts(values: Sequence[object]) -> tuple[dict[str, object], ...]:
    return tuple(
        {
            "name": _str_value(value, "name"),
            "value": _str_value(value, "value"),
            "excluded": _bool_value(value, "excluded"),
            "hidden": _bool_value(value, "hidden"),
        }
        for value in values
    )


def _project_named(value: object | None) -> dict[str, object] | None:
    if value is None:
        return None
    return {"id": _int_value(value, "id"), "name": _str_value(value, "name")}


def _project_link(value: object) -> dict[str, object]:
    return {
        "name": _str_value(value, "name"),
        "type": _str_value(value, "type"),
        "url": _str_value(value, "url"),
    }


def _project_job_run(value: object | None) -> dict[str, object] | None:
    if value is None:
        return None
    return {
        "id": _int_value(value, "id"),
        "name": _str_value(value, "name"),
        "status": _enum_value(_value(value, "status")),
        "stage": _enum_value(_value(value, "stage")),
        "url": _str_value(value, "url"),
        "error_message": _str_value(value, "error_message"),
        "external_id": _str_value(value, "external_id"),
        "job": _project_job(_value(value, "job")),
    }


def _project_job(value: object | None) -> dict[str, object] | None:
    if value is None:
        return None
    return {
        "id": _int_value(value, "id"),
        "name": _str_value(value, "name"),
        "type": _enum_value(_value(value, "type")),
        "url": _str_value(value, "url"),
    }


def _project_custom_field(value: object) -> dict[str, object]:
    custom_field = _value(value, "custom_field")
    return {
        "custom_field": (
            {
                "id": _int_value(custom_field, "id"),
                "name": _str_value(custom_field, "name"),
                "required": _bool_value(custom_field, "required"),
                "single_select": _bool_value(custom_field, "single_select"),
                "locked": _bool_value(custom_field, "locked"),
                "archived": _bool_value(custom_field, "archived"),
                "default_custom_field_value_id": _int_value(custom_field, "default_custom_field_value_id"),
            }
            if custom_field is not None
            else None
        ),
        "values": tuple(_project_named(item) for item in _sequence(_value(value, "values"))),
    }


def _project_environment(value: object) -> dict[str, object]:
    return {
        "id": _int_value(value, "id"),
        "name": _str_value(value, "name"),
        "variable": _project_named(_value(value, "variable")),
    }


def _project_member(value: object) -> dict[str, object]:
    return {
        "id": _int_value(value, "id"),
        "name": _str_value(value, "name"),
        "role": _project_named(_value(value, "role")),
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
        "id": _int_value(value, "id"),
        "integration_id": _int_value(value, "integration_id"),
        "integration_type": _enum_value(_value(value, "integration_type")),
        "name": _str_value(value, "name"),
        "display_name": _str_value(value, "display_name"),
        "status": _str_value(value, "status"),
        "summary": _str_value(value, "summary"),
        "url": _str_value(value, "url"),
        "closed": _bool_value(value, "closed"),
    }


def _project_defect(value: object) -> dict[str, object]:
    return {
        "id": _int_value(value, "id"),
        "name": _str_value(value, "name"),
        "closed": _bool_value(value, "closed"),
        "issue": _project_issue(_value(value, "issue")) if _value(value, "issue") is not None else None,
    }
