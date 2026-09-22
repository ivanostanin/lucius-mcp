"""Coverage for narrow, documented OpenAPI contract overlays."""

from __future__ import annotations

from scripts.filter_openapi import _add_launch_attachment_endpoints


def test_launch_attachment_overlay_exposes_only_the_observed_contract() -> None:
    spec: dict[str, object] = {}

    _add_launch_attachment_endpoints(spec)

    paths = spec["paths"]
    assert isinstance(paths, dict)
    endpoint = paths["/api/launch/attachment"]
    assert isinstance(endpoint, dict)
    assert set(endpoint) == {"get", "post"}

    get_operation = endpoint["get"]
    post_operation = endpoint["post"]
    assert isinstance(get_operation, dict)
    assert isinstance(post_operation, dict)
    assert get_operation["tags"] == ["launch-attachment-controller"]
    assert post_operation["tags"] == ["launch-attachment-controller"]
    assert post_operation["parameters"] == [
        {
            "name": "launchId",
            "in": "query",
            "required": True,
            "schema": {"type": "integer", "format": "int64"},
        }
    ]
    request_body = post_operation["requestBody"]
    assert isinstance(request_body, dict)
    content = request_body["content"]
    assert isinstance(content, dict)
    multipart = content["multipart/form-data"]
    assert isinstance(multipart, dict)
    assert multipart["schema"] == {
        "type": "object",
        "required": ["file"],
        "properties": {"file": {"type": "string", "format": "binary"}},
    }

    components = spec["components"]
    assert isinstance(components, dict)
    schemas = components["schemas"]
    assert isinstance(schemas, dict)
    assert schemas["LaunchAttachmentRowDto"]["properties"] == {
        "id": {"type": "integer", "format": "int64"},
        "name": {"type": "string"},
        "contentType": {"type": "string"},
        "contentLength": {"type": "integer", "format": "int64"},
        "entity": {"type": "string"},
    }
