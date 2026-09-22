import json

# Configuration
INPUT_FILE = "openapi/allure-testops-service/report-service.json"
OUTPUT_FILE = "openapi/allure-testops-service/filtered-report-service.json"

# Tags to keep (MVP + Essential Supporting Controllers)
KEEP_TAGS = {
    # Core Entities
    "test-case-controller",
    "shared-step-controller",
    "project-controller",
    "launch-controller",
    # Test Case Details
    "test-case-attachment-controller",
    "test-case-scenario-controller",
    "test-case-tag-controller",
    "test-case-overview-controller",
    "test-case-custom-field-controller",
    # Shared Step Details
    "shared-step-attachment-controller",
    "shared-step-scenario-controller",
    # Search & Bulk
    "test-case-search-controller",
    "launch-search-controller",
    "test-case-bulk-controller",
    # Project & Custom Field Management
    "custom-field-controller",
    "custom-field-project-controller",
    "custom-field-project-controller-v-2",
    "custom-field-schema-controller",
    "custom-field-value-controller",
    "custom-field-value-project-controller",
    "status-controller",
    # Test Layer Management
    "test-layer-controller",
    "test-layer-schema-controller",
    # Test Hierarchy Management
    "test-case-tree-controller-v-2",
    "tree-controller-v-2",
    "test-case-tree-bulk-controller-v-2",
    "integration-controller",
    # Test Plan Management
    "test-plan-controller",
    "test-case-test-plan-bulk-controller",
    # Defect Management
    "defect-controller",
    "defect-matcher-controller",
    # Manual test execution inside launches
    "test-result-controller",
    "test-result-bulk-controller",
    "test-result-run-controller",
    "test-result-rerun-controller",
    "test-result-flat-controller",
    "test-result-tree-controller-v-2",
    "test-result-attachment-controller",
    "test-result-custom-field-controller",
    "test-result-defect-controller",
    "test-result-env-var-controller",
    "test-result-issue-controller",
    "test-result-members-controller",
    "test-result-test-key-controller",
    "upload-controller",
    "upload-test-result-controller",
    "test-result-fixture-controller",
    "test-fixture-result-attachment-controller",
    # IDE test code generation (not published in the standard TestOps spec)
    "ide-controller",
    # Native launch attachments (confirmed by the TestOps web client, absent from the public spec)
    "launch-attachment-controller",
}


def _add_ide_test_code_endpoint(spec: dict) -> None:
    """Add the documented IDE test-code endpoint absent from the public spec.

    TestOps exposes this endpoint to its IDE integrations, but it is not
    included in the report-service OpenAPI document. Keeping the small
    contract overlay here lets the generated client remain the single HTTP
    interface used by application services.
    """
    components = spec.setdefault("components", {})
    schemas = components.setdefault("schemas", {})
    schemas.setdefault(
        "TestCodeGenerationRequestDto",
        {
            "type": "object",
            "required": [
                "lang",
                "testFramework",
                "syncFields",
                "syncName",
                "syncTags",
                "syncMembers",
                "syncIssues",
                "syncScenario",
            ],
            "properties": {
                "lang": {"type": "string"},
                "testFramework": {"type": "string"},
                "syncFields": {"type": "boolean"},
                "syncName": {"type": "boolean"},
                "syncTags": {"type": "boolean"},
                "syncMembers": {"type": "boolean"},
                "syncIssues": {"type": "boolean"},
                "syncScenario": {"type": "boolean"},
            },
        },
    )
    schemas.setdefault(
        "TestCodeGenerationResponseDto",
        {
            "type": "object",
            "required": ["code"],
            "properties": {"code": {"type": "string"}},
        },
    )

    spec.setdefault("paths", {}).setdefault(
        "/api/ide/testcase/{id}/testcode",
        {
            "post": {
                "tags": ["ide-controller"],
                "operationId": "generateTestCode",
                "summary": "Generate test code from a test case",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer", "format": "int64"},
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/TestCodeGenerationRequestDto"}}
                    },
                },
                "responses": {
                    "200": {
                        "description": "Generated test code.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/TestCodeGenerationResponseDto"}
                            }
                        },
                    }
                },
            }
        },
    )


def _add_launch_attachment_endpoints(spec: dict) -> None:
    """Add the narrowly observed native launch-attachment contract.

    TestOps's web client exposes this controller, but the checked-in report
    service specification omits it.  Keep this overlay constrained to the
    observed GET and POST operations so generated code remains the sole HTTP
    interface used by Lucius services.
    """
    components = spec.setdefault("components", {})
    schemas = components.setdefault("schemas", {})
    schemas.setdefault(
        "LaunchAttachmentRowDto",
        {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "format": "int64"},
                "name": {"type": "string"},
                "contentType": {"type": "string"},
                "contentLength": {"type": "integer", "format": "int64"},
                "entity": {"type": "string"},
            },
        },
    )
    schemas.setdefault(
        "PageLaunchAttachmentRowDto",
        {
            "type": "object",
            "properties": {
                "content": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/LaunchAttachmentRowDto"},
                },
                "empty": {"type": "boolean"},
                "first": {"type": "boolean"},
                "last": {"type": "boolean"},
                "number": {"type": "integer", "format": "int32"},
                "numberOfElements": {"type": "integer", "format": "int32"},
                "pageable": {"$ref": "#/components/schemas/Pageable"},
                "size": {"type": "integer", "format": "int32"},
                "totalElements": {"type": "integer", "format": "int64"},
                "totalPages": {"type": "integer", "format": "int32"},
            },
        },
    )

    launch_id = {
        "name": "launchId",
        "in": "query",
        "required": True,
        "schema": {"type": "integer", "format": "int64"},
    }
    spec.setdefault("paths", {}).setdefault(
        "/api/launch/attachment",
        {
            "get": {
                "tags": ["launch-attachment-controller"],
                "operationId": "listLaunchAttachments",
                "summary": "List native launch attachments",
                "parameters": [
                    launch_id,
                    {
                        "name": "page",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "integer", "default": 0, "minimum": 0},
                    },
                    {
                        "name": "size",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "integer", "default": 10, "minimum": 1},
                    },
                    {
                        "name": "sort",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "array", "items": {"type": "string"}},
                    },
                ],
                "responses": {
                    "200": {
                        "description": "Native launch attachment page.",
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/PageLaunchAttachmentRowDto"}}
                        },
                    }
                },
            },
            "post": {
                "tags": ["launch-attachment-controller"],
                "operationId": "createLaunchAttachment",
                "summary": "Attach one file to a launch",
                "parameters": [launch_id],
                "requestBody": {
                    "required": True,
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "required": ["file"],
                                "properties": {"file": {"type": "string", "format": "binary"}},
                            }
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Created native launch attachment.",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/LaunchAttachmentRowDto"},
                                }
                            }
                        },
                    }
                },
            },
        },
    )


def _patch_manual_session_schema(spec: dict) -> None:
    manual_session_schema = spec.get("components", {}).get("schemas", {}).get("ManualSessionRequestDto")
    if not isinstance(manual_session_schema, dict):
        return

    properties = manual_session_schema.setdefault("properties", {})
    if "projectId" not in properties:
        properties["projectId"] = {"type": "integer", "format": "int64"}
    if "jobUid" not in properties:
        properties["jobUid"] = {"type": "string"}
    if "jobRunUid" not in properties:
        properties["jobRunUid"] = {"type": "string"}

    required = manual_session_schema.setdefault("required", [])
    for field_name in ("projectId", "jobUid", "jobRunUid"):
        if field_name not in required:
            required.append(field_name)


def _patch_test_case_tree_schema(spec: dict) -> None:
    """Repair hierarchy-node discrimination missing from the upstream contract.

    The TestOps response identifies tree children with the wire values ``GROUP``
    and ``LEAF``.  The upstream base schema omits those mappings and the page
    declares an inline oneOf, which the Python generator cannot discriminate.
    Referencing the corrected named base schema lets generated deserialization
    return the concrete group and leaf DTOs directly.
    """
    schemas = spec.get("components", {}).get("schemas", {})
    if not isinstance(schemas, dict):
        return

    node_schema = schemas.get("TestCaseTreeNodeDto")
    if isinstance(node_schema, dict):
        discriminator = node_schema.setdefault("discriminator", {})
        if isinstance(discriminator, dict):
            discriminator["propertyName"] = "type"
            discriminator["mapping"] = {
                "GROUP": "#/components/schemas/TestCaseLightTreeNodeDto",
                "LEAF": "#/components/schemas/TestCaseTreeLeafDtoV2",
            }

    page_schema = schemas.get("PageTestCaseTreeNodeDto")
    if isinstance(page_schema, dict):
        properties = page_schema.setdefault("properties", {})
        if isinstance(properties, dict):
            content = properties.setdefault("content", {"type": "array"})
            if isinstance(content, dict):
                content["type"] = "array"
                content["items"] = {"$ref": "#/components/schemas/TestCaseTreeNodeDto"}

    full_node_schema = schemas.get("TestCaseFullTreeNodeDto")
    if isinstance(full_node_schema, dict):
        properties = full_node_schema.setdefault("properties", {})
        if isinstance(properties, dict):
            properties.setdefault("type", {"$ref": "#/components/schemas/NodeType"})


def filter_spec() -> None:
    print(f"Reading spec from {INPUT_FILE}...")
    with open(INPUT_FILE) as f:
        spec = json.load(f)

    _add_ide_test_code_endpoint(spec)
    _add_launch_attachment_endpoints(spec)

    original_paths_count = len(spec.get("paths", {}))
    print(f"Original paths: {original_paths_count}")

    # Filter paths
    filtered_paths = {}
    for path, methods in spec.get("paths", {}).items():
        new_methods = {}
        for method, operation in methods.items():
            if method == "parameters":  # Keep path-level parameters if any
                new_methods[method] = operation
                continue

            tags = operation.get("tags", [])
            # Check if any of the operation's tags are in our keep list
            if any(tag in KEEP_TAGS for tag in tags):
                new_methods[method] = operation

        if new_methods:
            filtered_paths[path] = new_methods

    spec["paths"] = filtered_paths

    _patch_manual_session_schema(spec)
    _patch_test_case_tree_schema(spec)

    # We are NOT filtering components/schemas aggressively because it's hard to trace
    # all dependencies (refs) without a full graph traversal.
    # openapi-python-client might be smart enough to only generate models that are used,
    # or we can accept the extra models as "future proofing" without the bloat of 100+ extra controllers.

    print(f"Filtered paths: {len(filtered_paths)}")
    print(f"Writing filtered spec to {OUTPUT_FILE}...")

    with open(OUTPUT_FILE, "w") as f:
        json.dump(spec, f, indent=2)


if __name__ == "__main__":
    filter_spec()
