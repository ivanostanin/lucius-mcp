import pytest

from src.tools.output_contract import (
    apply_output_contract,
    render_collection_output,
    render_message_output,
    render_output,
)


def test_render_output_defaults_to_structured_only_tool_result() -> None:
    result = render_output(
        plain="Found 1 item",
        json_payload={"items": [{"id": 1}], "total": 1},
    )

    assert result.content == []
    assert result.structured_content == {"items": [{"id": 1}], "total": 1}


def test_render_output_preserves_plain_text_and_structured_json_modes() -> None:
    plain = render_output(
        plain="line1\\nline2",
        json_payload={"ok": True},
        output_format="plain",
    )
    structured_json = render_output(
        plain="ignored",
        json_payload={"ok": True},
        output_format="json",
    )

    assert plain == "line1\nline2"
    assert structured_json.content == []
    assert structured_json.structured_content == {"ok": True}


def test_message_and_collection_helpers_default_to_structured_only_tool_results() -> None:
    message = render_message_output("Done")
    collection = render_collection_output(
        items=[{"id": 1}],
        plain_empty="No items",
        plain_lines=["- item"],
        page=0,
    )

    assert message.content == []
    assert message.structured_content == {"message": "Done"}
    assert collection.content == []
    assert collection.structured_content == {"items": [{"id": 1}], "total": 1, "page": 0}


def test_apply_output_contract_wraps_non_object_structured_payloads() -> None:
    structured = apply_output_contract(["a", "b"])
    assert structured.content == []
    assert structured.structured_content == {"result": ["a", "b"]}
    json_structured = apply_output_contract({"ok": True}, output_format="json")
    assert json_structured.content == []
    assert json_structured.structured_content == {"ok": True}


def test_render_output_rejects_unknown_format() -> None:
    with pytest.raises(ValueError, match="Unsupported output_format"):
        render_output(plain="x", json_payload={"x": 1}, output_format="yaml")
