"""E2E coverage for high-priority entity commands via `uv run lucius`."""

from __future__ import annotations

import json
import os

import pytest

from tests.cli.subprocess_helpers import (
    assert_clean_cli_result,
    run_uv_cli,
    run_uv_cli_with_mocked_message_output,
    run_uv_cli_with_mocked_result,
)


def _env_with_utc() -> dict[str, str]:
    return {**os.environ, "TZ": "UTC"}


@pytest.mark.parametrize(
    ("args", "tool_name", "mocked_result", "expected_tool_format", "markers"),
    [
        (
            ["test_case", "list", "--args", "{}"],
            "list_test_cases",
            '{"ok":true,"count":2}',
            "json",
            ('{"ok":true,"count":2}',),
        ),
        (
            ["test_case", "get", "--args", '{"test_case_id": 1}', "--format", "plain"],
            "get_test_case_details",
            "Test Case 1\nStatus: Draft",
            "plain",
            ("Test Case 1", "Status: Draft"),
        ),
        (
            ["test_case", "list", "--args", "{}", "--format", "table"],
            "list_test_cases",
            json.dumps([{"id": 1, "name": "Alpha"}]),
            "json",
            ("Command Result", "Alpha"),
        ),
        (
            ["test_case", "list", "--args", "{}", "--format", "csv"],
            "list_test_cases",
            json.dumps([{"id": 1, "name": "Alpha"}]),
            "json",
            ("id,name", "1,Alpha"),
        ),
        (
            ["test_case", "list", "--args", "{}", "--pretty"],
            "list_test_cases",
            '{"ok":true,"count":2}',
            "json",
            ('"ok": true', '"count": 2'),
        ),
    ],
)
def test_uv_run_test_case_execution_formats(
    args: list[str],
    tool_name: str,
    mocked_result: str,
    expected_tool_format: str,
    markers: tuple[str, ...],
) -> None:
    result = run_uv_cli_with_mocked_result(args, tool_name, mocked_result, expected_tool_format)

    assert_clean_cli_result(result)
    for marker in markers:
        assert marker in result.stdout


def test_uv_run_test_case_plain_output_normalizes_escaped_newlines_through_console_script() -> None:
    result = run_uv_cli_with_mocked_message_output(
        ["test_case", "get", "--args", '{"test_case_id": 1}', "--format", "plain"],
        "get_test_case_details",
        "Line 1\\nLine 2",
        "plain",
    )

    assert_clean_cli_result(result)
    assert result.stdout == "Line 1\nLine 2"


@pytest.mark.parametrize(
    ("args", "tool_name", "mocked_result", "expected_tool_format", "markers"),
    [
        (
            ["launch", "list", "--args", "{}", "--format", "table"],
            "list_launches",
            json.dumps([{"id": 10, "name": "Nightly", "created_at": 1700000000}]),
            "json",
            ("Command Result", "Nightly", "Timezone: UTC"),
        ),
        (
            ["launch", "get", "--args", '{"launch_id": 10}', "--format", "plain"],
            "get_launch",
            "Launch 10: Nightly",
            "plain",
            ("Launch 10: Nightly",),
        ),
        (
            ["launch", "close", "--args", '{"launch_id": 10}'],
            "close_launch",
            '{"id":10,"status":"closed"}',
            "json",
            ('"status":"closed"',),
        ),
    ],
)
def test_uv_run_launch_execution_flows(
    args: list[str],
    tool_name: str,
    mocked_result: str,
    expected_tool_format: str,
    markers: tuple[str, ...],
) -> None:
    result = run_uv_cli_with_mocked_result(args, tool_name, mocked_result, expected_tool_format, env=_env_with_utc())

    assert_clean_cli_result(result)
    for marker in markers:
        assert marker in result.stdout


@pytest.mark.parametrize(
    ("tz_value", "expected_time", "expected_caption"),
    [
        ("Europe/Podgorica", "2023-11-14 23:13:20", "Timezone: Europe/Podgorica"),
        ("Invalid/Zone", "2023-11-14 22:13:20", "Timezone: UTC"),
    ],
)
def test_uv_run_table_datetime_timezone_resolution_and_fallback(
    tz_value: str,
    expected_time: str,
    expected_caption: str,
) -> None:
    result = run_uv_cli_with_mocked_result(
        ["launch", "list", "--args", "{}", "--format", "table"],
        "list_launches",
        json.dumps([{"id": 10, "name": "Nightly", "created_at": 1700000000}]),
        "json",
        env={**os.environ, "TZ": tz_value},
    )

    assert_clean_cli_result(result)
    assert expected_time in result.stdout
    assert expected_caption in result.stdout


@pytest.mark.parametrize(
    ("args", "tool_name", "mocked_result", "expected_tool_format", "markers"),
    [
        (
            ["custom_field", "get", "--args", '{"name": "Priority"}', "--format", "table"],
            "get_custom_fields",
            json.dumps([{"id": 1, "name": "Priority"}]),
            "json",
            ("Command Result", "Priority"),
        ),
        (
            ["custom_field_value", "list", "--args", '{"custom_field_name": "Priority"}', "--format", "csv"],
            "list_custom_field_values",
            json.dumps([{"id": 11, "name": "P0"}]),
            "json",
            ("id,name", "11,P0"),
        ),
        (
            ["custom_field_value", "create", "--args", '{"custom_field_name": "Priority", "name": "P1"}'],
            "create_custom_field_value",
            '{"id":12,"name":"P1"}',
            "json",
            ('"name":"P1"',),
        ),
        (
            [
                "custom_field_value",
                "update",
                "--args",
                '{"custom_field_name": "Priority", "cfv_id": 12, "name": "P2", "confirm": true}',
            ],
            "update_custom_field_value",
            '{"id":12,"name":"P2"}',
            "json",
            ('"name":"P2"',),
        ),
        (
            [
                "custom_field_value",
                "delete",
                "--args",
                '{"custom_field_name": "Priority", "cfv_id": 12, "confirm": true}',
                "--format",
                "plain",
            ],
            "delete_custom_field_value",
            "Deleted custom field value 12",
            "plain",
            ("Deleted custom field value 12",),
        ),
    ],
)
def test_uv_run_custom_field_execution_flows(
    args: list[str],
    tool_name: str,
    mocked_result: str,
    expected_tool_format: str,
    markers: tuple[str, ...],
) -> None:
    result = run_uv_cli_with_mocked_result(args, tool_name, mocked_result, expected_tool_format)

    assert_clean_cli_result(result)
    for marker in markers:
        assert marker in result.stdout


@pytest.mark.parametrize(
    ("args", "expected_marker"),
    [
        (["tc"], "Actions for test_case"),
        (["ln"], "Actions for launch"),
        (["cf"], "Actions for custom_field"),
        (["cfv"], "Actions for custom_field_value"),
    ],
)
def test_uv_run_short_alias_discovery_flows(args: list[str], expected_marker: str) -> None:
    result = run_uv_cli(args)

    assert_clean_cli_result(result)
    assert expected_marker in result.stdout


def test_uv_run_short_alias_executes_test_case_route() -> None:
    result = run_uv_cli_with_mocked_result(
        ["tc", "list", "--args", "{}"],
        "list_test_cases",
        '{"ok":true}',
        "json",
    )

    assert_clean_cli_result(result)
    assert result.stdout.strip() == '{"ok":true}'
